import concurrent.futures
import csv
import logging
import pickle
import time
from datetime import datetime
from os.path import isfile, exists

import NewTunes.charts as charts
from NewTunes.ChartCSS import ChartCss
from NewTunes.config import LOG_NAME, MULTIPROC, VISITED_SONGS
from NewTunes.Scraper import Scraper
from NewTunes.sites.common.util import fuzzy_match
from NewTunes.tool.llist import LinkedList
from NewTunes.tool.logger import setup_logger

setup_logger(LOG_NAME)
LOGGER = logging.getLogger(LOG_NAME)

def get_chart(visits):
    songs = Scraper(visits).process()
    if songs is None:
        raise RuntimeError("Chart Failed")
    if len(songs) == 0:
        LOGGER.info("No new songs: " + visits.url)
    else:
        LOGGER.info("New Songs: " + visits.url)
    return songs


def remove_duplicate(song_list):
    if song_list:
        llist = LinkedList(song_list)
        song = llist.head
        song_list = []
        while song and song.next:
            next_song = song
            while next_song.next:
                first = str(song.value[0]) + " " + str(song.value[1])
                second = str(next_song.next.value[0]) + " " + str(next_song.next.value[1])
                if fuzzy_match(first, second):
                    next_song.next = next_song.next.next
                else:
                    next_song = next_song.next
            song_list.append(song.value)
            song = song.next
        return song_list
    return []


def to_file(song_list):
    filename = datetime.now().strftime("%Y_%m_%d_%H_%M") + ".csv"
    while isfile(filename):
        time.sleep(30)
        filename = datetime.now().strftime("%Y_%m_%d_%H_%M") + ".csv"
    with open(filename, 'w') as out:
        csv_out = csv.writer(out)
        for row in song_list:
            csv_out.writerow(row)


def entry():
    proceed = True
    start = time.time()
    LOGGER.info('Started')
    if exists(VISITED_SONGS):
        with open(VISITED_SONGS, 'rb') as f:
            old_songs = pickle.load(f)
    else:
        old_songs = []
    crawl_queue = [ChartCss(chart) for chart in charts.Charts]
    new_songs = []
    if MULTIPROC:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MULTIPROC) as executor:
            future_to_url = (executor.submit(
                get_chart, crawl) for crawl in crawl_queue)
            for new_list in concurrent.futures.as_completed(future_to_url):
                try:
                    add_songs = new_list.result()
                    new_songs.extend(add_songs)
                except Exception as e:
                    LOGGER.exception('Chart Failed')
                    proceed = False
                    break
    else:
        for chart in crawl_queue:
            print(chart.url)
            new_list = get_chart(chart)
            if new_list:
                new_songs.extend(new_list)

    if proceed:
        new_songs = remove_duplicate(new_songs)
        to_file(new_songs)
        end = time.time()
        with open(VISITED_SONGS, 'wb') as f:
            pickle.dump(new_songs + old_songs, f)
        LOGGER.info('Ended: Run time ' + str(end - start) + 's')
    else:
        LOGGER.info("Failed")
        end = time.time()
        LOGGER.info('Ended: Run time ' + str(end - start) + 's')


if __name__ == "__main__":
    entry()
