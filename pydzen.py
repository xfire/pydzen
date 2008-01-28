#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import sys
import os
import re
import types
import time
import subprocess
import logging
from logging.handlers import SysLogHandler

class utils(object):
    @staticmethod
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

    @staticmethod
    def parse_app(args, regex_list, value = None):
        return utils.parse(execute(args, value).split('\n'), regex_list)

    @staticmethod
    def parse_file(path_list, regex_list):
        if not isinstance(path_list, (types.ListType, types.TupleType)):
            path_list = [path_list]

        lines = []
        for path in path_list:
            try:
                file = open(path, 'r')
                lines.extend(file.readlines())
                file.close()
            except IOError, e:
                logger.exception(e)

        return utils.parse(lines, regex_list)

    @staticmethod
    def parse(lines, regex_list):
        if not isinstance(regex_list, (types.ListType, types.TupleType)):
            regex_list = [regex_list]

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

    @staticmethod
    def pipe(app, **kwargs):
        def _to_param(k, v):
            if isinstance(v, types.BooleanType):
                return ['-%s' % k]
            return ['-%s' % k, '%s' % str(v)]

        args = [app]
        for k,v in kwargs.iteritems():
            if not isinstance(v, types.NoneType):
                args.extend(_to_param(k,v))
        
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, close_fds=True)
        return p

    @staticmethod
    def execute(app, value = None, **kwargs):
        if not value: value = ''

        p = utils.pipe(app, **kwargs)
        if value:
            out, err = p.communicate(str(value))
        else:
            out, err = p.communicate()
        if err:
            logger.error('execute: err')
        return out

    @staticmethod
    def dzen(**kwargs):
        args = config.DZEN_OPTIONS.copy()
        args.update(kwargs)
        return utils.pipe(config.DZEN, **args)

    @staticmethod
    def gdbar(value, **kwargs):
        args = config.GDBAR_OPTIONS.copy()
        args.update(kwargs)
        return utils.execute(config.GDBAR, value, **args)

    @staticmethod
    def cache(timeout):
        def wrapper(f, cache={}):
            def nfunc():
                key = f
                if key not in cache:
                    cache[key] = [f(), time.time()]
                elif (time.time() - cache[key][1]) >= timeout:
                    cache[key] = [f(), time.time()]
                return cache[key][0]
            return nfunc
        return wrapper

def load_plugins(pnames):
    plugins = []
    for p in pnames:
        try:
            plugin = __import__(p, {}, {}, '*')
            if hasattr(plugin, 'update'):
                plugins.append(plugin)
            else:
                logger.warning()
        except ImportError, e:
            logger.error('error loading "%s": %s' % (p, e))
    return plugins

DEFAULT_CONFIG = dict(PLUGINS = [], 
                      LOGLEVEL = logging.ERROR)
def read_config(file):
    config = DEFAULT_CONFIG.copy()
    try:
        execfile(file, {}, config)
    except Exception, e:
        print 'Invalid configuration file: %s' % e
        sys.exit(1)
    class _ConfigWrapper(dict):
        def __init__(self, *args, **kwargs):
            super(_ConfigWrapper, self).__init__(*args, **kwargs)
        def __getattr__(self, name):
            return self[name]
        def __setattr__(self, name, value):
            self[name] = value
            return self[name]
    return _ConfigWrapper(config)

def init_logger(loglevel):
    logger = logging.getLogger()

    logger.setLevel(loglevel)

    formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    syslog = SysLogHandler(address = '/dev/log')
    syslog.setFormatter(formatter)
    syslog.setLevel(loglevel)
    logger.addHandler(syslog)

    return logger

config = read_config('/home/fire/work/src/pydzen.simplify/pydzenrc')

if __name__ == '__main__':
    logger = init_logger(config.LOGLEVEL)
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

