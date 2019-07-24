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
from common.util import fuzzy_match
from config.configuration import Configuration
from song import Genre, SongInfo

start_logger()
error_log = getLogger('error')
info_log = getLogger('info')

cfg = Configuration().cfg

lastfm = LastFm(cfg)
genius = Genius(cfg)
spotify = Spotify(cfg)
language = LangClassifier(cfg)

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
    copy_path = cfg['paths']['output']+song_info.max_genre.genre.lower()+"/"
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


def details_from_lyrics(song):
    title = song.tag.title
    base_title = re.split(cfg['split'], song.tag.title)[0].strip()
    details = genius.get_song(base_title, song.tag.artist)
    return details


def get_language(song):
    def find_lang(details, alpha_title):
        if details is not None:
            try:
                return language.detect(details.lyrics)
            except Exception:
                return language.detect(alpha_title)
        return language.detect(alpha_title)
    details = details_from_lyrics(song)
    base_title = re.split(cfg['split'], song.tag.title)[0].strip()
    alpha_title = ''.join(
        char for char in base_title if char.isalpha() or char == ' ').strip()
    try:
        lang = find_lang(details, alpha_title)
    except ValueError as e:
        raise Exception('Title is not valid') from e
    return base_title, details, lang


def get_genre(song, base_title, details, lang):
    if lang.lower() in language.english:
        genre = lastfm.get_genre(song.tag.artist, base_title)
        if genre:
            if genre[0].genre == 'Track not found'.lower() and details is not None:
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
                clean_genre = []
                for gen in genre:
                    for my_gen in cfg['genre']['main']:
                        if fuzzy_match(gen.genre, my_gen):
                            clean_genre.append(gen)
                if not clean_genre:
                    data = spotify.search_artist(song.tag.artist)
                    if data['artists']['total'] == 0:
                        clean_genre = [Genre(lang, 0)]
                    else:
                        genres = data['artists']['items'][0]['genres']
                        if genres:
                            clean_genre = [Genre(genres[0], 0)]
                        else:
                            clean_genre = [Genre(lang, 0)]
                return clean_genre
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
        return SongInfo(None,
                        None,
                        str(filename),
                        [Genre("Check Failed", 0)],
                        None,
                        None)
    except Exception as e:
        error_log.exception(str(filename))
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
