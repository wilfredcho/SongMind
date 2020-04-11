from fuzzywuzzy import fuzz

from settings.configuration import Configuration

cfg = Configuration().cfg


import datetime
import re
import string

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.manifold import TSNE
from wordcloud import WordCloud

STOP_WORDS = set(stopwords.words('english') +
                 [p for p in string.punctuation] + ["'s", '’'])
REMOVE = ['.…', '…', '@', '#']
DEM = 25

"""
def word_embeddings(dim=DEM):
    glove_file = 'glove.twitter.27B.'+str(dim)+'d.txt'
    emb_dict = {}
    glove = open('./' + glove_file)
    for line in glove:
        values = line.split()
        word = values[0]
        vector = np.asarray(values[1:], dtype='float32')
        emb_dict[word] = vector
    glove.close()
    return emb_dict


EMBEDDINGS = word_embeddings()
"""

def flatten(lst):
    return [item for sublist in lst for item in sublist]


def join_words(words):
    return ''.join(word + ' ' for word in words).strip()


def display_cloud(ticker, text, label):
    if text != '':
        wordcloud = WordCloud(max_font_size=40).generate(text)
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(ticker + ' ' + label + ' Words')
        plt.show()


def visualize_tweets(tweets):
    for ticker, data in tweets.items():
        data = pd.DataFrame(data)
        words = join_words(flatten(data[(data['label'] == -1) & (
            data['tags'].str.contains(ticker))]['Tweet Text Filtered'].to_list()))
        display_cloud(ticker, words, 'Negative Changes')
        words = join_words(flatten(data[(data['label'] == 1) & (
            data['tags'].str.contains(ticker))]['Tweet Text Filtered'].to_list()))
        display_cloud(ticker, words, 'Positive Changes')


def clean_word(word):
    for pattern in REMOVE:
        word = word.replace(pattern, '')
    word = ''.join(char for char in word if char.isalpha()
                   or char == ' ' or char in string.punctuation)
    return word


def word_vector(training_tweets):
    ticker_vectors = {}
    for ticker, data in training_tweets.items():
        vectors = []
        for datum in data:
            total_word_vect = None
            for word in datum['Tweet Text Filtered']:
                if word not in STOP_WORDS:
                    word_vect = EMBEDDINGS.get(word)
                    if word_vect is not None and total_word_vect is None:
                        total_word_vect = word_vect
                    elif total_word_vect is not None and word_vect is not None:
                        total_word_vect += word_vect
            if total_word_vect is not None:
                total_word_vect = np.append(
                    total_word_vect, [datum['Favorite Count'], datum['Retweet Count']])
                vectors.append(
                    {'vector': total_word_vect, 'label': datum['label']})
        ticker_vectors[ticker] = vectors
    return ticker_vectors


def scanner(pattern, sentence):
    scan_len = len(pattern)
    sen_len = len(sentence)
    if scan_len == sen_len:
        return pattern == sentence
    if not scan_len > sen_len:
        for idx in range(0, sen_len):
            if idx == 0:
                check_pattern = pattern + ' '
                begin = 0
                end = 1
            elif idx == sen_len - scan_len:
                check_pattern = pattern
                begin = 0
                end = 0
            else:
                check_pattern = ' ' + pattern + ' '
                begin = -1
                end = 1
            if check_pattern == sentence[idx + begin: idx + scan_len + end]:
                return True
    return False


def tsne_scatter_plot(ticker, words, word_labels):
    category_to_color = {0: 'lightgreen', 1: 'blue', -1: 'red'}
    tsne = TSNE(n_components=2, random_state=0)
    np.set_printoptions(suppress=True)
    Y = tsne.fit_transform(words)
    point_color = [category_to_color[label] for label in word_labels]
    x_coords = Y[:, 0]
    y_coords = Y[:, 1]
    plt.scatter(x_coords, y_coords, color=point_color)
    for label, x, y in zip(word_labels, x_coords, y_coords):
        plt.annotate(label, xy=(x, y), xytext=(
            0, 0), textcoords='offset points')
    plt.xlim(x_coords.min()+0.00005, x_coords.max()+0.00005)
    plt.ylim(y_coords.min()+0.00005, y_coords.max()+0.00005)
    plt.title(ticker)
    plt.show()


def plot_density(price_history, title):
    for ticker in list(price_history):
        sns.distplot(price_history[ticker], hist=False, kde=True,
                     kde_kws={'linewidth': 3},
                     label=ticker)
    plt.legend(prop={'size': 10}, title='Stock')
    plt.title(title + ' Density Plot of Stock Prices Changes')
    plt.xlabel('Percentage Change')
    plt.ylabel('Density')



def alpha_only(text):
    return ''.join(char.lower()
                   for char in text if char.isalpha() or char == ' ')


def fuzzy_match(text1, text2):
    return fuzz.ratio(alpha_only(text1), alpha_only(text2)) > cfg['genre']['match_ratio']
