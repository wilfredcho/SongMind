import concurrent.futures
import os
import re
import shutil
from filecmp import cmp
from os.path import isfile
from pathlib import Path
from shutil import copy

import eyed3
import mutagen
import numpy as np
import polyglot
from mutagen.easyid3 import EasyID3
from tqdm import tqdm

from organizer.api import Counter, Genius, LangClassifier, LastFm, Spotify
from common.logger import getLogger, start_logger
from common.util import fuzzy_match
from settings.configuration import Configuration
from organizer.song import Genre, SongInfo

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
        info_log.info("Process Successful")
    else:
        info_log.info("Process Failed: ")
        info_log.info("Duplicates: " + str(counter.count))
        info_log.info("Difference: " + str(set(jobs) - set(outputs)))
        info_log.info("Duplicates: " + str(counter.count))


def multithreading(func, jobs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=int(cfg['multithread']['workers'])) as executor:
        future_job = (executor.submit(
            func, job) for job in jobs)
        for future in tqdm(concurrent.futures.as_completed(future_job), total=len(jobs), unit="job"):
            song_info = future.result()
            copy_file(song_info)


def details_from_lyrics(title, artist):
    base_title = re.split(cfg['split'], title)[0].strip()
    details = genius.get_song(base_title, artist)
    return details


def get_language(title, artist):
    def find_lang(details, alpha_title):
        if details is not None:
            try:
                return language.detect(details.lyrics)
            except Exception:
                return language.detect(alpha_title)
        return language.detect(alpha_title)
    details = details_from_lyrics(title, artist)
    base_title = re.split(cfg['split'], title)[0].strip()
    alpha_title = ''.join(
        char for char in base_title if char.isalpha() or char == ' ').strip()
    try:
        lang = find_lang(details, alpha_title)
    except ValueError as e:
        raise Exception('Title is not valid') from e
    return base_title, details, lang

def artist_lang(artist):
    return language.detect(artist)


def get_genre(artist, base_title, details, lang):
    if lang.lower() in language.english:
        genre = lastfm.get_genre(artist, base_title)
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
                    artist = spotify.search_artist(artist)
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
                    data = spotify.search_artist(artist)
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
            title = song.tag.title
            artist = song.tag.artist
            art_lang = artist_lang(artist)
            base_title, details, lang = get_language(title, artist)
            if art_lang != language.english:
                lang = art_lang
            genre = get_genre(artist, base_title, details, lang)
            return SongInfo(artist,
                            title,
                            str(filename),
                            genre,
                            None,
                            None)
        try:
            song = EasyID3(str(filename))
        except mutagen.id3._util.ID3NoHeaderError:
            return SongInfo(None,
                            None,
                            str(filename),
                            [Genre("ID3NoHeader", 0)],
                            None,
                            None)
        if song:
            if all(meta in song.keys() for meta in ['title', 'artist']):
                title = song['title'][0]
                artist = song['artist'][0]
                art_lang = artist_lang(artist)
                base_title, details, lang = get_language(title, artist)
                if art_lang != language.english:
                    lang = art_lang
                genre = get_genre(artist, base_title, details, lang)
                return SongInfo(artist,
                                title,
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


def move_dir(source_folder, dest):
    files = os.listdir(source_folder)
    os.makedirs(os.path.dirname(source_folder)+'/'+dest, exist_ok=True)
    for f in files:
        dest_name = os.path.dirname(source_folder)+'/'+dest+'/'+f
        while True:
            i = 0
            if os.path.exists(dest_name):
                dest_name = os.path.splitext(
                    dest_name)[0] + str(i) + os.path.splitext(dest_name)[1]
                i += 1
            else:
                shutil.move(source_folder+'/'+f, dest_name)
                break


def merge(cfg):
    num_songs = len(my_song_list(cfg['paths']['output']))
    folders = list(filter(os.path.isdir, [
                   cfg['paths']['output'] + path for path in os.listdir(cfg['paths']['output'])]))
    genre_map = cfg['genre']['pair']
    for source_folder in folders:
        genre = os.path.basename(source_folder)
        if genre in genre_map.keys():
            move_dir(source_folder, genre_map[genre])
            os.rmdir(os.path.dirname(source_folder)+'/'+genre)

    if len(my_song_list(cfg['paths']['output'])) == num_songs:
        info_log.info("Merge Successful")
    else:
        info_log.info("Merge Failed")


if __name__ == "__main__":
    process(cfg['multithread']['status'])
    merge(cfg)
