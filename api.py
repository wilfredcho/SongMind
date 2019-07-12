import time

import lyricsgenius
import numpy as np
import pylast
import requests
import spotipy
from langdetect import detect
from ratelimit import limits, sleep_and_retry
from spotipy.oauth2 import SpotifyClientCredentials

from song import Genre


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Spotify(metaclass=Singleton):
    def __init__(self, cfg):
        self.spotify = spotipy.Spotify(
            SpotifyClientCredentials(
                client_id=cfg["spotify"]["client_id"],
                client_secret=cfg["spotify"]["client_secret"]
            )
        )


class LangClassifier(object):

    def detect(self, txt):
        return detect(txt)


class LastFm(metaclass=Singleton):

    def __init__(self, cfg):
        self.lasffm = pylast.LastFMNetwork(api_key=cfg["lastFM"]["api_key"])

    @sleep_and_retry
    @limits(calls=4, period=1)
    def get_genre(self, artist, title):
        info = self.lasffm.get_track(artist, title)
        MAX_TRIES = 10
        tries = 0
        while tries < MAX_TRIES:
            try:
                genre = info.get_top_tags()
                break
            except pylast.WSError as e:
                return [Genre(e.details, 0)]
            except pylast.MalformedResponseError:
                time.sleep(3)
            except pylast.NetworkError:
                time.sleep(3)
            finally:
                tries += 1
                if tries == MAX_TRIES - 1:
                    break
        weight_median = np.median([int(gen.weight) for gen in genre])

        genre_array = (Genre(gen.item.get_name(), int(gen.weight))
                       for gen in genre)
        return [gen for gen in genre_array if gen.weight > weight_median]


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
                time.sleep(3)

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
