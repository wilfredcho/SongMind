from __future__ import absolute_import

import logging
from logging.handlers import RotatingFileHandler

import yaml

from settings.configuration import Configuration

cfg = Configuration().cfg


def setup_logger(logger_name, log_file, level=logging.INFO):
    log = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    file_handler = RotatingFileHandler(cfg['logs']['path'] + log_file, mode='a', maxBytes=int(cfg['logs']['size']),
                                       backupCount=int(cfg['logs']['backup']), encoding=None, delay=0)
    file_handler.setFormatter(formatter)
    log.setLevel(level)
    log.addHandler(file_handler)


def init_logger(logs):
    for log in logs:
        setup_logger(log, log + '.log')


def start_logger():
    init_logger(cfg['logs']['topic'])


def getLogger(log):
    return logging.getLogger(log)
