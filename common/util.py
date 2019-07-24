from fuzzywuzzy import fuzz

from config.configuration import Configuration

cfg = Configuration().cfg


def alpha_only(text):
    return ''.join(char.lower()
                   for char in text if char.isalpha() or char == ' ')


def fuzzy_match(text1, text2):
    return fuzz.ratio(alpha_only(text1), alpha_only(text2)) > cfg['genre']['match_ratio']
