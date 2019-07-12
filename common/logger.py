from __future__ import absolute_import

import logging
from config.configuration import Configuration
from logging.handlers import RotatingFileHandler

import yaml

cfg = Configuration().cfg


def setup_logger(logger_name, log_file, level=logging.INFO):
    log = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    file_handler = RotatingFileHandler(cfg['logs']['path'] + log_file, mode='a', maxBytes=int(cfg['log']['size']),
                                      backupCount=int(cfg['log']['backup']), encoding=None, delay=0)
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
