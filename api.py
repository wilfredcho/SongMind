import json
import time

import detectlanguage
import lyricsgenius
import polyglot
import pylast
import spotipy
import requests
from googletrans import Translator
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
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=cfg["spotify"]["client_id"],
            client_secret=cfg["spotify"]["client_secret"]
        )
        )

    @sleep_and_retry
    @limits(calls=5, period=1)
    def get_track(self, track_id):
        return self.spotify.track(track_id)

    @sleep_and_retry
    @limits(calls=5, period=1)
    def get_artist(self, artist_id):
        return self.spotify.artist(artist_id)

    @sleep_and_retry
    @limits(calls=5, period=1)
    def search_track(self, track, artist):
        # data['tracks']['items']
        return self.spotify.search(q='artist:' + artist + ' track:' + track, type='track')

    @sleep_and_retry
    @limits(calls=5, period=1)
    def search_artist(self, artist):
        return self.spotify.search(q='artist:' + artist, type='artist')

    @sleep_and_retry
    @limits(calls=5, period=1)
    def audio_analysis(self, track_id):
        return self.spotify.audio_analysis(track_id)

    @sleep_and_retry
    @limits(calls=5, period=1)
    def audio_features(self, track_id):
        return self.spotify.audio_features([track_id])

    @sleep_and_retry
    @limits(calls=5, period=1)
    def related_artists(self, track_id):
        return self.spotify.artist_related_artists(track_id)

class LanguageLayer(metaclass=Singleton):

    def __init__(self, cfg):
        self.__access_key = cfg['languagelayer']['api_key']
        self.__url = "http://api.languagelayer.com/detect"

    def detect(self, txt):
        query = {"access_key":self.__access_key,"query":txt}
        response = requests.request("GET", self.__url, params=query)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                if data['results'][0]['reliable_result']:
                    return data['results'][0]['language_code']
        return "Unknown Language"

class LangClassifier(metaclass=Singleton):

    def __init__(self, cfg):
        self.__english = ['en', 'english']
        self._max_tries = int(cfg['tries'])
        detectlanguage.configuration.api_key = cfg['detectlanguage']['api_key']
        self.languagelayer = LanguageLayer(cfg)

    def detect(self, txt):
        txt = ''.join(char for char in txt if char.isalpha() or char == " ")
        if txt != "":
            lang = self.translate(txt)
            return lang
        raise ValueError

    @sleep_and_retry
    @limits(calls=1, period=4)
    def translate(self, txt):
        tries = 0
        while tries < self._max_tries:
            detector = Detector(txt)
            if detector.reliable:
                return detector.language.name
            google_translator = Translator()
            try:
                return google_translator.detect(txt).lang
            except json.decoder.JSONDecodeError:
                tries += 1
                if tries == self._max_tries - 1:
                    try:
                        langs = detectlanguage.detect(txt)
                        if langs:
                            return langs[0]['language']
                        return self.languagelayer.detect(txt)
                    except detectlanguage.exceptions.DetectLanguageError:
                        return self.languagelayer.detect(txt)
                time.sleep(1)

    @property
    def english(self):
        return self.__english

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
        return [gen for gen in genre_array]  # [0].genre == 'Track not found'


class Genius(metaclass=Singleton):

    def __init__(self, cfg):
        self.genius = lyricsgenius.Genius(cfg["genius"]["user_token"])
        self._max_tries = int(cfg['tries'])

    @sleep_and_retry
    @limits(calls=5, period=1)
    def get_song(self, title, artist):
        if title is None or artist is None:
            return None
        if title == "" or artist == "":
            return None
        tries = 0
        while tries < self._max_tries:
            try:
                song = self.genius.search_song(title, artist)
                return song
            except Exception:
                tries += 1
                if tries == self._max_tries - 1:
                    return None
                time.sleep(1)
