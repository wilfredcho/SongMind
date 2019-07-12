from __future__ import absolute_import

import logging
from logging.handlers import RotatingFileHandler

import yaml

with open("./config/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

LOG_DIR = cfg['logs']['path']
LOGS = cfg['logs']['topic']


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = RotatingFileHandler(LOG_DIR + log_file, mode='a', maxBytes=5*1024*1024,
                                      backupCount=100, encoding=None, delay=0)
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)


def init_logger(logs):
    for log in logs:
        setup_logger(log, log + '.log')


def start_logger():
    init_logger(LOGS)


def getLogger(log):
    return logging.getLogger(log)
