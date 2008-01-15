#!/usr/bin/env python
#
# vim:syntax=python:sw=4:ts=4:expandtab

import types
import subprocess
import logging
import config

logger = logging.getLogger('utils')

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

def gzen2(**kwargs):
    args = config.DZEN2_OPTIONS.copy()
    args.update(kwargs)
    return pipe(config.DZEN2, **args)

def gdbar(value, **kwargs):
    args = config.GDBAR_OPTIONS.copy()
    args.update(kwargs)
    return execute(config.GDBAR, value, **args)

