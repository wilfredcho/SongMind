import time

import lyricsgenius
import numpy as np
import pylast
import requests
import spotipy
import polyglot
from polyglot.detect import Detector
from ratelimit import limits, sleep_and_retry
from spotipy.oauth2 import SpotifyClientCredentials
from common.singleton import Singleton

from song import Genre



class Counter(metaclass=Singleton):
    def __init__(self, count):
        self.count = count

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, value):
        self.__count = value


class Spotify(metaclass=Singleton):
    def __init__(self, cfg):
        self.spotify = spotipy.Spotify(client_credentials_manager=
            SpotifyClientCredentials(
                client_id=cfg["spotify"]["client_id"],
                client_secret=cfg["spotify"]["client_secret"]
            )
        )
    
    def search_track(self, track, artist):
        return self.spotify.search(q='artist:' + artist + ' track:' + track, type='track') #data['tracks']['items']

    def audio_analysis(self, id):
        return self.spotify.audio_analysis(id)

    def audio_features(self, id):
        return self.spotify.audio_features([id])
    
    def related_artists(self, id):
        return self.spotify.artist_related_artists(id)

class LangClassifier(metaclass=Singleton):

    def detect(self, txt):
        detector = Detector(txt)
        return detector.language.name

    @property
    def english(self):
        return self.detect("This is English, Can I BE more clear?")
    
    @property
    def error(self):
        return polyglot.detect.base.UnknownLanguage


class LastFm(metaclass=Singleton):

    def __init__(self, cfg):
        self.lasffm = pylast.LastFMNetwork(api_key=cfg["lastFM"]["api_key"])
        self._max_tries = int(cfg['tries'])

    @sleep_and_retry
    @limits(calls=5, period=1)
    def get_genre(self, artist, title):
        info = self.lasffm.get_track(artist, title)
        tries = 0
        while tries < self._max_tries:
            try:
                genre = info.get_top_tags()
                break
            except pylast.WSError as e:
                return [Genre(e.details, 0)]
            except pylast.MalformedResponseError as e:
                tries += 1
                if tries == self._max_tries - 1:
                    return [Genre(str(e), 0)]
                time.sleep(1)
            except pylast.NetworkError as e:
                tries += 1
                if tries == self._max_tries - 1:
                    return [Genre(str(e), 0)]
                time.sleep(1)
        genre_array = (Genre(gen.item.get_name(), int(gen.weight))
                       for gen in genre)
        return [gen for gen in genre_array]


class Genius(metaclass=Singleton):

    def __init__(self, cfg):
        self.genius = lyricsgenius.Genius(cfg["genius"]["user_token"])
        self._max_tries = int(cfg['tries'])

    @sleep_and_retry
    @limits(calls=5, period=1)
    def get_song(self, title, artist):
        tries = 0
        while tries < self._max_tries:
            try:
                song = self.genius.search_song(title, artist)
                return song
            except requests.exceptions.ReadTimeout:
                tries += 1
                if tries == self._max_tries - 1:
                    return None
                time.sleep(1)
                

        """
        if song is not None:
            song.artist
            song.title
            song.year
            song.featured_artists
            song.media
        """
    


"""
d = discogs_client.Client('ExampleApplication/0.1', user_token=cfg["discogs"]["user_token"])
results = d.search('Stockholm By Night', type='release')
artist = results[0].artists[0]
print(artist.name)
"""
