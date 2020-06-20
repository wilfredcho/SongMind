import logging
import pickle
import re
import time
from importlib import import_module
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

import newtunes.config as constants
from .config import VISITED_SONGS
from newtunes.sites import *

logger = logging.getLogger('process')

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class LoadFile(object):
    __metaclass__ = Singleton

    def __init__(self, load_file):
        if os.path.exists(load_file):
            with open(load_file, "rb") as f:
                self.old_songs = pickle.load(f)
        else:
            self.old_songs = []


FILES = LoadFile(VISITED_SONGS)


class Scraper(object):

    def __init__(self, chart):
        self.chart = chart
        setattr(self.chart, 'dislike_artist', constants.DISLIKE_ARTIST)
        setattr(self.chart, 'dislike_title', constants.DISLIKE_TITLE)
        setattr(self, 'run', getattr(import_module(
            'newtunes.sites.' + self.chart.site), self.chart.site)().run)
        setattr(self.chart, 'old_songs', FILES.old_songs)

    def _get_page(self):
        return requests.get(self.chart.url)

    def _make_soup(self):
        return BeautifulSoup(self.page.content, 'html.parser')

    def _make_js_soup(self):
        driver = webdriver.Chrome()
        driver.get(self.chart.url)
        time.sleep(constants.WAIT)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            if hasattr(self.chart, 'button'):
                rows = driver.find_elements_by_css_selector(self.chart.button)
                for row in rows:
                    row.click()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height >= last_height:
                break

        time.sleep(constants.WAIT)
        soup = driver.page_source
        driver.quit()
        return BeautifulSoup(soup, 'html.parser')

    def process(self):
        self.page = self._get_page()
        if self.page.status_code == constants.OK:
            if self.chart.js:
                soup = self._make_js_soup()
            else:
                soup = self._make_soup()
            try:
                return self.run(soup, self.chart)
            except Exception:
                logging.error("Failed to visit " +
                              self.chart.url)
                logger.exception("Exception: ")
                return None
        else:
            logging.error("Failed to visit : " +
                          str(self.page.status_code) + " : " + self.chart.url)
            return None
