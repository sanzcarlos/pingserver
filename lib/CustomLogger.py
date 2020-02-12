#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler
import os
import gzip

def namer(name):
    return name + ".gz"

def rotator(source, dest):
    with open(source, "rb") as sf:
        data = sf.read()
        with gzip.open(dest, "wb") as df:
            df.write(data)
        os.remove(source)

def getCustomLogger(name, filename, setlevel='INFO'):
    directory = os.path.dirname(os.path.abspath(__file__))
    logger = logging.getLogger(name)
    if setlevel is 'DEBUG':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(filename)s:%(lineno)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler = RotatingFileHandler('logs/' + filename + '.log', maxBytes=2000000, backupCount=1000)
    handler.setFormatter(formatter)
    handler.rotator = rotator
    handler.namer = namer
    logger.addHandler(handler)
    return logger
