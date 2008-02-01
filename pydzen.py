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
from optparse import OptionParser

class utils(object):
    @staticmethod
    def screens(screens = 0):
        """
        try to get number of xinerama screens and return a list of screen numbers.

        first check if parameter value is > 0, if so, use it.

        second check XINERAMA_SCREENS environment variable, which should contain the
        number of screens. 

        if the environment variable is not set, try xrandr to get the number of
        connected displays.

        if xrandr fails, return one screen. (-> [0])
        """
        logger = logging.getLogger('utils')

        if screens <= 0:
            screens = os.environ.get('XINERAMA_SCREENS')
        if isinstance(screens, types.StringTypes):
            try:
                screens = int(screens)
            except ValueError:
                logger.error('XINERAMA_SCREENS invalid (%s)' % screens)
                screens = 0
        if not screens:
            try:
                screens = utils.execute('xrandr')
                screens = len(re.findall(" connected ", screens, re.M))
            except OSError:
                logger.warning('can not execute xrandr')
                screens = 1
        return range(0, screens)

    @staticmethod
    def parse_app(args, regex_list, value = None):
        return utils.parse(execute(args, value).split('\n'), regex_list)

    @staticmethod
    def parse_file(path_list, regex_list):
        logger = logging.getLogger('utils')

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
        logger = logging.getLogger('utils')

        def _to_param(k, v):
            if isinstance(v, types.BooleanType):
                return ['-%s' % k]
            return ['-%s' % k, '%s' % str(v)]

        args = [app]
        for k,v in kwargs.iteritems():
            if not isinstance(v, types.NoneType):
                args.extend(_to_param(k,v))
        
        try:
            logger.debug('utils.pipe(%s)' % str(args))
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, close_fds=True)
        except OSError, e:
            logger.error('can not execute "%s": %s' % (app, e))
            sys.exit(1)
        return p

    @staticmethod
    def execute(app, value = None, **kwargs):
        logger = logging.getLogger('utils')

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

def load_plugins():
    logger = logging.getLogger('pydzen')

    sys.path.insert(0, os.path.expanduser(config.PLUGIN_DIR))
    plugins = []
    for p in config.PLUGINS:
        try:
            plugin = __import__(p, {}, {}, '*')
            if hasattr(plugin, 'update'):
                plugins.append(plugin)
            else:
                logger.warning('invalid plugin "%s": no update() function specified' % p)
        except ImportError, e:
            logger.error('error loading plugin "%s": %s' % (p, e))
    sys.path = sys.path[1:]
    return plugins

def init_logger():
    logging.basicConfig(level = config.LOGLEVEL,
                        format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

def read_config_file(file, **defaults):
    config = defaults.copy()
    try:
        execfile(os.path.expanduser(file), {}, config)
    except StandardError, e:
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

def configure():
    parser = OptionParser()
    parser.add_option('-c', '--config', dest = 'CONFIG_FILE',
                      help = 'specify an alternate pydzenrc file')
    parser.add_option('-p', '--plugins', dest = 'PLUGIN_DIR',
                      help = 'specify an alternate plugin directory')
    parser.add_option('-s', '--screens', dest = 'SCREENS', type = 'int',
                      help = 'number of Xinerama screen')
    parser.set_defaults(CONFIG_FILE = '~/.pydzen/pydzenrc',
                        PLUGIN_DIR = '~/.pydzen',
                        SCREENS = 0)

    (options, args) = parser.parse_args()
    config = read_config_file(options.CONFIG_FILE,
                              PLUGINS = [],
                              LOGLEVEL = logging.WARN,
                              SCREENS = options.SCREENS,
                              PLUGIN_DIR = options.PLUGIN_DIR)
    return config

config = configure()

if __name__ == '__main__':
    init_logger()
    logger = logging.getLogger('pydzen')

    plugins = load_plugins()

    dzens = [utils.dzen(xs = i + 1) for i in utils.screens(config.SCREENS)]
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

