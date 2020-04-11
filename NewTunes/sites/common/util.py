import re

from fuzzywuzzy import fuzz

import newtunes.sites.common.compare as compare
from newtunes import config as constants
from newtunes.sites.common.Info import Info

from nltk import word_tokenize


def condit(info, chart):
    return all([getattr(compare, condit)(info, activate)for condit, activate in chart.condit.items() if activate]) and \
        not any(dislike_artist.lower() in info.artist.lower()
                for dislike_artist in chart.dislike_artist) and \
        not bool(set(word_tokenize(info.title.lower())
                     ).intersection(set(chart.dislike_title)))

def format_text(text):
    text = text.lstrip().rstrip()
    try:
        text = int(re.sub(r'\s+', '', text))
    except ValueError:
        text = re.sub(r'\s+', ' ', text)
    return text

def proc_info(chart, cur_pos, last_pos, title, artist):
    info = Info(cur_pos, last_pos, title, artist)
    for song in chart.old_songs:
        if fuzzy_match(str(info.artist) + str(info.title), str(song[0]) + str(song[1])):
            return False
    if condit(info, chart):
        return (artist, title)
    return False

def alpha_only(text):
    return ''.join(char.lower()
                   for char in text if char.isalpha() or char == ' ').strip()


def fuzzy_match(text1, text2):
    return fuzz.ratio(alpha_only(text1), alpha_only(text2)) > constants.MATCH_RATIO
