#
# Copyright (C) 2008 Rico Schiekel (fire at downgra dot de)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# vim:syntax=python:sw=4:ts=4:expandtab

import os
import re
import logging

from pydzen import utils

logger = logging.getLogger('plugin.mem')

RE_MEM = re.compile('^Mem:\s*(?P<total>\d+)\s+(?P<used>\d+)\s+(?P<free>\d+)\s+(?P<shared>\d+)\s+(?P<buffers>\d+)\s+(?P<cached>\d+).*$')
RE_SWAP = re.compile('^Swap:\s*(?P<total>\d+)\s+(?P<used>\d+)\s+(?P<free>\d+).*$')

@utils.cache(2)
def update():
    try:
        out = utils.execute('free', m = True)
        lines = out.split('\n')

        _mem = RE_MEM.match(lines[1])
        _swap = RE_SWAP.match(lines[3])

        if _mem and _swap:
            _mem = dict([(k, float(v)) for k, v in _mem.groupdict().items()])
            _swap = dict([(k, float(v)) for k, v in _swap.groupdict().items()])

            mem_used = _mem['used'] - _mem['buffers'] - _mem['cached']
            swap_used = _swap['used']

            mem = utils.gdbar('%d %d' % (mem_used, _mem['total'] ))
            swap = utils.gdbar('%d %d' % (swap_used, _swap['total'] ))

            return ['Mem: %s' % mem, 
                    'Mem: %s (%d Mb) Swap: %s (%d Mb)' % (mem, mem_used, swap, swap_used)]
    except StandardError, e:
        logger.warn(e)

    return None
