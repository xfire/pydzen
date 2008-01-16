#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import sys
import time
import re
import subprocess

import logging
from logging.handlers import SysLogHandler

import config
import utils

def init_logger():
    logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    syslog = SysLogHandler(address = '/dev/log')
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)

    return logger

def screens():
    screens = utils.execute('xrandr')
    return range(0, len(re.findall(" connected ", screens, re.M)))

def load_plugins(pnames):
    plugins = []
    for p in pnames:
        try:
            plugin = __import__(p, [], [], '*')
            if hasattr(plugin, 'update'):
                plugins.append(plugin)
            else:
                logger.error()
        except ImportError, e:
            logger.error(e)
    return plugins

if __name__ == '__main__':
    init_logger()

    plugins = load_plugins(config.PLUGINS)
    g = utils.gzen2()
    dzens = [utils.gzen2(xs = i + 1) for i in screens()]
    while True:
        s = []
        for p in plugins:
            s.append(p.update())
        s = '%s\n' % ' '.join(s)
        for d in dzens:
            d.stdin.write(s)
        del s
        time.sleep(1)

