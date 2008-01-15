#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import sys
import time
import logging
from logging.handlers import SysLogHandler

import config
import utils

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
    # init logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    syslog = SysLogHandler(address = '/dev/log')
    formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)

    plugins = load_plugins(config.PLUGINS)
    g = utils.gzen2()
    while True:
        s = []
        for p in plugins:
            s.append(p.update())
        g.stdin.write('%s\n' % ' '.join(s))
        # sys.stdout.write('%s\n' % ' '.join(s))
        # sys.stdout.flush()
        del s
        time.sleep(1)

