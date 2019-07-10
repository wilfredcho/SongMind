import concurrent.futures
import os
from os.path import isfile
from pathlib import Path
from shutil import copy

import eyed3
import langdetect
import numpy as np
import yaml
from tqdm import tqdm

from api import Genius, LangClassifier, LastFm
from common.logger import getLogger, start_logger
from song import Genre, SongInfo

start_logger()
error_log = getLogger('error')


with open("./config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
lastfm = LastFm(cfg)
genius = Genius(cfg)
language = LangClassifier()


def song_condit(song):
    if song is not None:
        if song.tag is not None:
            if song.tag.artist is not None and song.tag.title is not None:
                if song.tag.artist != '' and song.tag.title != '':
                    return True
    return False


def copy_file(song_info):
    if song_info:
        copy_path = cfg['paths']['output']+song_info.max_genre.genre+"/"
        if not os.path.exists(copy_path):
            os.makedirs(copy_path)
        copy(song_info.filename, copy_path)


def process(MULTI=True):
    jobs = my_song_list()
    if MULTI:
        multithreading(get_info, jobs)
    else:
        for job in jobs:
            song_info = get_info(job)
            copy_file(song_info)


def multithreading(func, jobs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_job = (executor.submit(
            func, job) for job in jobs)
        for future in tqdm(concurrent.futures.as_completed(future_job), total=len(jobs), unit="jobs"):
            song_info = future.result()
            copy_file(song_info)


def get_info(filename):
    try:
        song = eyed3.load(str(filename))
        if song_condit(song):
            try:
                lang = language.detect(song.tag.title)
            except langdetect.lang_detect_exception.LangDetectException:
                return SongInfo(None,
                                None,
                                str(filename),
                                [Genre('Untitled', 0)],
                                None,
                                None)
            if lang == 'en':
                lyrics = genius.get_lyrics(song.tag.title, song.tag.artist)
                if lyrics != '':
                    lang = language.detect(lyrics)
            if lang == 'en':
                genre = lastfm.get_genre(
                    song.tag.artist, song.tag.title)
            else:
                genre = [Genre(lang, 0)]
            if genre:
                return SongInfo(song.tag.artist,
                                song.tag.title,
                                str(filename),
                                genre,
                                None,
                                None)
            else:
                return SongInfo(None,
                                None,
                                str(filename),
                                [Genre(lang, 0)],
                                None,
                                None)
        return SongInfo(None,
                        None,
                        str(filename),
                        [Genre('Untitled', 0)],
                        None,
                        None)
    except Exception as e:
        error_log.exception("File: " + str(filename))
        pass


def my_song_list():
    jobs = list(Path(cfg['paths']['input']).glob('**/*.*'))
    file_jobs = list(filter(lambda x: isfile(
        x) and os.path.basename(x).split('.')[0] != '', jobs))
    return file_jobs


if __name__ == "__main__":

    #info = []
    process()

    # info.append(song_info)
