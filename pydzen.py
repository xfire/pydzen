#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import types
import time
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
    dzens = [utils.dzen(xs = i + 1) for i in utils.screens()]
    try:
        while True:
            lines = []
            for p in plugins:
                values = p.update()
                if values:
                    if not isinstance(values, (types.ListType, types.TupleType)):
                        values = [values]
                    for i, value in enumerate(values):
                        if len(lines) < (i + 1):
                            lines.append([])
                        if value:
                            lines[i].append(value)

            lines = [config.JOINTS.join(l) for l in lines]
            lines = '\n'.join(lines) + '\n'
            for d in dzens:
                d.stdin.write(lines)
            del lines
            time.sleep(1)
    except (KeyboardInterrupt):
        pass
