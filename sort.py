import concurrent.futures
import os
import re
from filecmp import cmp
from os.path import isfile
from pathlib import Path
from shutil import copy

import eyed3
import numpy as np
import polyglot
from tqdm import tqdm

from api import Counter, Genius, LangClassifier, LastFm, Spotify
from common.logger import getLogger, start_logger
from config.configuration import Configuration
from song import Genre, SongInfo

start_logger()
error_log = getLogger('error')
info_log = getLogger('info')

cfg = Configuration().cfg

lastfm = LastFm(cfg)
genius = Genius(cfg)
spotify = Spotify(cfg)
language = LangClassifier()

counter = Counter(0)


def song_condit(song):
    if song is not None:
        if song.tag is not None:
            if song.tag.artist is not None and song.tag.title is not None:
                if song.tag.artist != '' and song.tag.title != '':
                    return True
    return False


def duplicate_files(copy_path, song_info, dup):
    if not os.path.exists(copy_path):
        os.makedirs(copy_path)
    copy_file = copy_path + os.path.basename(str(song_info.filename))
    if os.path.exists(copy_file):
        if cmp(song_info.filename, copy_file):
            if dup == '':
                dup = 0
            duplicate_files(copy_path + '_' + str(dup+1), song_info, dup+1)
        else:
            info_log.info("Remove Identitcal File: " + str(song_info.filename))
            counter.count += 1
    else:
        copy(song_info.filename, copy_path)


def copy_file(song_info):
    copy_path = cfg['paths']['output']+song_info.max_genre.genre+"/"
    duplicate_files(copy_path, song_info, '')


def process(MULTI=False):
    jobs = my_song_list(cfg['paths']['input'])

    if MULTI:
        multithreading(get_info, jobs)
    else:
        for job in tqdm(jobs, total=len(jobs), unit="job"):
            song_info = get_info(job)
            copy_file(song_info)

    outputs = my_song_list(cfg['paths']['output'])
    jobs = [os.path.basename(job) for job in jobs]
    outputs = [os.path.basename(output) for output in outputs]
    if len(jobs) == (len(outputs) + counter.count):
        print("Success")
    else:
        print(len(set(jobs)) - len(set(outputs)))
        print(counter.count)
        print(set(jobs) - set(outputs))
        print("Failed")


def multithreading(func, jobs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(cfg['multithread']['workers'])) as executor:
        future_job = (executor.submit(
            func, job) for job in jobs)
        for future in tqdm(concurrent.futures.as_completed(future_job), total=len(jobs), unit="job"):
            song_info = future.result()
            copy_file(song_info)


def details_from_lyrics(song, lang):
    title = song.tag.title
    if lang == language.english:
        details = genius.get_song(title, song.tag.artist)
        return details
    return None


def get_language(song):
    base_title = re.split(cfg['split'], song.tag.title)[0].strip()
    alpha_title = ''.join(
        char for char in base_title if char.isalpha() or char == ' ').strip()
    try:
        lang = language.detect(alpha_title)
    except language.error:
        lang = language.english
    finally:
        details = details_from_lyrics(song, lang)
        if details is not None:
            lang = language.detect(details.lyrics)
    return base_title, details, lang


def get_genre(song, base_title, details, lang):
    if lang == language.english:
        genre = lastfm.get_genre(song.tag.artist, base_title)
        if genre:
            if genre[0].genre == 'Track not found' and details is not None:
                spotify_data = [
                    data for data in details.media if data['provider'] == 'spotify']
                if spotify_data:
                    spotify_data = spotify_data[0]
                    track = spotify.get_track(spotify_data['native_uri'])
                    artist = spotify.get_artist(track['artists'][0]['uri'])
                    genres = artist['genres']
                    if genres:
                        return [Genre(genres[0], 0)]
                else:
                    artist = spotify.search_artist(song.tag.artist)
                    if artist['artists']['items']:
                        genres = artist['artists']['items'][0]['genres']
                        if genres:
                            return [Genre(genres[0], 0)]
            else:
                return genre
    return [Genre(lang, 0)]


def get_info(filename):
    try:
        song = eyed3.load(str(filename))
        if song_condit(song):
            base_title, details, lang = get_language(song)
            genre = get_genre(song, base_title, details, lang)
            return SongInfo(song.tag.artist,
                            song.tag.title,
                            str(filename),
                            genre,
                            None,
                            None)
        try:
            #fileinfo = os.path.basename(filename).split('.mp3')[0]
            #lang = language.detect(fileinfo)
            return SongInfo(None,
                            None,
                            str(filename),
                            [Genre("Check Failed", 0)],
                            None,
                            None)
        except language.error:
            error_log.exception("Line 145, File: " + str(filename))
            return SongInfo(None,
                            None,
                            str(filename),
                            [Genre('Untitled', 0)],
                            None,
                            None)
    except Exception as e:
        error_log.exception("Line 153, File: " + str(filename))
        return SongInfo(None,
                        None,
                        str(filename),
                        [Genre(str(e), 0)],
                        None,
                        None)


def my_song_list(path):
    jobs = list(Path(path).glob('**/*.*'))
    file_jobs = [job for job in jobs
                 if isfile(job) and os.path.basename(job).split('.')[0] != '']
    return file_jobs


if __name__ == "__main__":
    process(cfg['multithread']['status'])
