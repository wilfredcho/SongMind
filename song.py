from operator import attrgetter


class Genre(object):

    def __init__(self, genre, weight):
        self._genre = genre
        self._weight = weight

    @property
    def genre(self):
        return self._genre

    @property
    def weight(self):
        return self._weight


class SongInfo(object):

    def __init__(self, artist, title, filename, genre, lyrics, lang):
        self._artist = artist
        self._title = title
        self._filename = filename
        self._genre = genre
        self._lyrics = lyrics
        self._lang = lang

    @property
    def artist(self):
        return self._artist

    @property
    def title(self):
        return self._title

    @property
    def filename(self):
        return self._filename

    @property
    def genre(self):
        return self._genre

    @property
    def lyrics(self):
        return self._lyrics

    @property
    def lang(self):
        return self._lang

    @genre.setter
    def genre(self, value):
        self._genre = value

    @lyrics.setter
    def lyrics(self, value):
        self._lyrics = value

    @lang.setter
    def lang(self, value):
        self._lang = value

    @property
    def max_genre(self):
        return max(self.genre, key=attrgetter('weight'))
        # return max(self.genre, key=lambda x: x.weight)
