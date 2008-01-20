#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import os
import re
import types
import subprocess
import logging
import config

logger = logging.getLogger('utils')


def screens():
    """
    try to get number of xinerama screens and return a list of screen numbers.

    first check XINERAMA_SCREENS environment variable, which should contain the
    number of screens. 

    if the environment variable is not set, try xrandr to get the number of
    connected displays.

    if xrandr fails, return one screen. (-> [0])
    """
    screens = os.environ.get('XINERAMA_SCREENS')
    if not isinstance(screens, types.StringTypes):
        try:
            screens = execute('xrandr')
            screens = len(re.findall(" connected ", screens, re.M))
        except OSError:
            logger.warning('can not execute xrandr')
            screens = 1
    else:
        try:
            screens = int(screens)
        except ValueError:
            logger.error('XINERAMA_SCREENS invalid (%s)' % screens)
            screens = 1
    return range(0, screens)

def parse_file(path_list, regex_list):
    if not isinstance(path_list, (types.ListType, types.TupleType)):
        path_list = [path_list]

    if not isinstance(regex_list, (types.ListType, types.TupleType)):
        regex_list = [regex_list]

    lines = []
    for path in path_list:
        try:
            file = open(path, 'r')
            lines.extend(file.readlines())
            file.close()
        except IOError, e:
            logger.exception(e)

    ret = {}
    for line in lines:
        for regex in regex_list:
            match = regex.match(line)
            if match:
                for k, v in match.groupdict().iteritems():
                    ov = ret.get(k, v)
                    if k in ret:
                        ov.append(v)
                    else:
                        ov = [ov]
                    ret[k] = ov

    return ret

def pipe(app, **kwargs):
    def _to_param(k, v):
        if isinstance(v, types.BooleanType):
            return ['-%s' % k]
        return ['-%s' % k, '%s' % str(v)]

    args = [app]
    for k,v in kwargs.iteritems():
        if not isinstance(v, types.NoneType):
            args.extend(_to_param(k,v))
    
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, close_fds=True)
    return p

def execute(app, value = None, **kwargs):
    if not value: value = ''

    p = pipe(app, **kwargs)
    if value:
        out, err = p.communicate(str(value))
    else:
        out, err = p.communicate()
    if err:
        logger.error('execute: err')
    return out

def dzen(**kwargs):
    args = config.DZEN_OPTIONS.copy()
    args.update(kwargs)
    return pipe(config.DZEN, **args)

def gdbar(value, **kwargs):
    args = config.GDBAR_OPTIONS.copy()
    args.update(kwargs)
    return execute(config.GDBAR, value, **args)

