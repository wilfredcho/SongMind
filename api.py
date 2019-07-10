import time

import lyricsgenius
import numpy as np
import pylast
import requests
from langdetect import detect
from ratelimit import limits, sleep_and_retry

from song import Genre


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LangClassifier(object):

    def detect(self, txt):
        return detect(txt)


class LastFm(metaclass=Singleton):

    def __init__(self, cfg):
        self.network = pylast.LastFMNetwork(api_key=cfg["lastFM"]["api_key"])

    @sleep_and_retry
    @limits(calls=4, period=1)
    def get_genre(self, artist, title):
        def map_weight(genre):
            return (int(genre.weight))

        def map_genre(genre):
            return (Genre(genre.item.get_name(), int(genre.weight)))
        info = self.network.get_track(artist, title)
        MAX_TRIES = 10
        tries = 0
        while tries < MAX_TRIES:
            try:
                genre = info.get_top_tags()
            except pylast.WSError as e:
                return [Genre(e.details, 0)]
            except pylast.NetworkError:
                tries += 1
                if tries == MAX_TRIES - 1:
                    break
                time.sleep(1)
                continue
        weight_median = np.median(list(map(map_weight, genre)))
        genre_array = list(map(map_genre, genre))
        return list(filter(lambda x: x.weight > weight_median, genre_array))


class Genius(metaclass=Singleton):

    def __init__(self, cfg):
        self.genius = lyricsgenius.Genius(cfg["genius"]["user_token"])

    def get_lyrics(self, title, artist):
        MAX_TRIES = 10
        tries = 0
        while tries < MAX_TRIES:
            try:
                song = self.genius.search_song(title, artist)
                break
            except requests.exceptions.ReadTimeout:
                tries += 1
                if tries == MAX_TRIES - 1:
                    break
                time.sleep(1)
                continue

        if song is not None:
            return song.lyrics
        """
        if song is not None:
            song.artist
            song.title
            song.year
            song.featured_artists
        """
        return ''


"""
d = discogs_client.Client('ExampleApplication/0.1', user_token=cfg["discogs"]["user_token"])
results = d.search('Stockholm By Night', type='release')
artist = results[0].artists[0]
print(artist.name)
"""
