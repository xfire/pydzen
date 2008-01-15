#
# Copyright (C) 2007 Rico Schiekel (fire at downgra dot de)
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

import re
import logging

from utils import Colors
from utils.statusbar import execute
from config import BAR_NORMAL_COLORS

logger = logging.getLogger('statusbar.mem')

RE_MEM = re.compile('^Mem:\s*(?P<total>\d+)\s+(?P<used>\d+)\s+(?P<free>\d+)\s+(?P<shared>\d+)\s+(?P<buffers>\d+)\s+(?P<cached>\d+).*$')
RE_SWAP = re.compile('^Swap:\s*(?P<total>\d+)\s+(?P<used>\d+)\s+(?P<free>\d+).*$')


def interval():
    return 4


def update():
    try:
        out, err = execute('free', m = True)
        lines = out.split('\n')

        mem = RE_MEM.match(lines[1])
        swap = RE_SWAP.match(lines[3])

        if mem and swap:
            mem = dict([(k, float(v)) for k, v in mem.groupdict().items()])
            swap = dict([(k, float(v)) for k, v in swap.groupdict().items()])

            mem_used = mem['used'] - mem['buffers'] - mem['cached']
            mem_usage = mem_used / mem['total'] * 100.0

            swap_usage = swap['used'] / swap['total'] * 100.0

            # return (BAR_NORMAL_COLORS, 'RAM: %d / %d MB (%02d%%) SWAP: %d / %d MB (%02d%%)' % \
            #         (mem_used, mem['total'], mem_usage, swap['used'], swap['total'], swap_usage))
            return (BAR_NORMAL_COLORS, 'RAM: %d MB (%02d%%) SWAP: %d MB (%02d%%)' % \
                    (mem_used, mem_usage, swap['used'], swap_usage))
    except Exception, e:
        logger.exception(e)

    return (BAR_NORMAL_COLORS, 'RAM: -- MB (--%%) SWAP: -- MB (--%%)')
