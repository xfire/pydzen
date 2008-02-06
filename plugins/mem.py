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

def bar(used, total):
    return utils.gdbar('%d %d' % (used, total), l = '%d%% ' % (100. / total * used))

@utils.cache(2)
def update():
    try:
        out = utils.execute('free', m = True)
        lines = out.split('\n')

        _mem = RE_MEM.match(lines[1]).groupdict()
        _swap = RE_SWAP.match(lines[3]).groupdict()

        if _mem and _swap:
            mem_total = float(_mem['total'])
            swap_total = float(_swap['total'])

            mem_used = float(_mem['used']) - float(_mem['buffers']) - float(_mem['cached'])
            swap_used = float(_swap['used'])

            mem = bar(mem_used, mem_total)
            swap = bar(swap_used, swap_total)

            return ['Mem: %s' % mem, 
                    'Mem: %s (%d/%d Mb) Swap: %s (%d/%d Mb)' % (mem, mem_used, mem_total, swap, swap_used, swap_total)]
    except StandardError, e:
        logger.warn(e)

    return None
