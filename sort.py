import concurrent.futures
import os
import re
from filecmp import cmp
from os.path import isfile
from pathlib import Path
from shutil import copy

import eyed3
import langdetect
import numpy as np
from tqdm import tqdm

from api import Counter, Genius, LangClassifier, LastFm
from common.logger import getLogger, start_logger
from config.configuration import Configuration
from song import Genre, SongInfo

start_logger()
error_log = getLogger('error')
info_log = getLogger('info')

cfg = Configuration().cfg

lastfm = LastFm(cfg)
genius = Genius(cfg)
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
            info_log.info("Remove Identitcal File")
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
    #jobs = map(lambda x: os.path.basename(str(x)), jobs)
    outputs = [os.path.basename(output) for output in outputs]
    #outputs = map(lambda x: os.path.basename(str(x)), outputs)
    if len(jobs) == (len(outputs) + counter.count):
        print("Success")
    else:
        print(len(set(jobs)) - len(set(outputs)))
        print(counter.count)
        print(set(jobs) - set(outputs))
        print("Failed")


def multithreading(func, jobs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_job = (executor.submit(
            func, job) for job in jobs)
        for future in tqdm(concurrent.futures.as_completed(future_job), total=len(jobs), unit="job"):
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
            title = re.split(cfg['split'], song.tag.title)[0]
            if lang == 'en':
                lyrics = genius.get_lyrics(title, song.tag.artist)
                if lyrics != '':
                    lang = language.detect(lyrics)
            if lang == 'en':
                genre = lastfm.get_genre(
                    song.tag.artist, title)
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
        fileinfo = os.path.basename(filename).split('.mp3')[0]
        try:
            lang = language.detect(fileinfo)
            return SongInfo(None,
                            None,
                            str(filename),
                            [Genre(lang, 0)],
                            None,
                            None)
        except langdetect.lang_detect_exception.LangDetectException:
            return SongInfo(None,
                            None,
                            str(filename),
                            [Genre('Untitled', 0)],
                            None,
                            None)
    except Exception as e:
        error_log.exception("File: " + str(filename))
        return SongInfo(None,
                        None,
                        str(filename),
                        [Genre('Error', 0)],
                        None,
                        None)


def my_song_list(path):
    jobs = list(Path(path).glob('**/*.*'))
    file_jobs = [job for job in jobs
                 if isfile(job) and os.path.basename(job).split('.')[0] != '']
    # file_jobs = filter(lambda x: isfile(
    #    x) and os.path.basename(x).split('.')[0] != '', jobs)
    return file_jobs


if __name__ == "__main__":
    process(cfg['multithread'])
