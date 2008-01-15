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
from utils.statusbar import parse_file
from config import BAR_NORMAL_COLORS

logger = logging.getLogger('statusbar.cpu')

FILE_TEMP = '/proc/acpi/thermal_zone/TZ4/temperature'

RE_CPU = re.compile(r'^cpu MHz\s*:\s*(?P<mhz>\d+).*$')
RE_STATS = re.compile(r'^cpu  (?P<user>\d+) (?P<system>\d+) (?P<nice>\d+) (?P<idle>\d+).*$')
RE_TEMP = re.compile(r'^temperature:\s*(?P<temp>\d+)\s+(?P<unit>.*)$')

OLD_STATS = dict(user = 0, system = 0, nice = 0, idle = 0)


def interval():
    return 2


def update():
    cpu_vals = parse_file('/proc/cpuinfo', RE_CPU)
    stat_vals = parse_file('/proc/stat', RE_STATS)
    temp_vals = parse_file(FILE_TEMP, RE_TEMP)

    cpu = '--'
    try:
        cpu = '/'.join(cpu_vals['mhz'])
    except Exception, e:
        logger.exception(e)

    load = '--'
    try:
        # convert values to int's
        stat_vals = dict([(k, int(v[0])) for k, v in stat_vals.items()])
        dtotal = stat_vals['user'] - OLD_STATS['user'] + \
                 stat_vals['system'] - OLD_STATS['system'] + \
                 stat_vals['nice'] - OLD_STATS['nice'] + \
                 stat_vals['idle'] - OLD_STATS['idle']
        if dtotal > 0:
            load = '%02d' % (100 - ((stat_vals['idle'] - OLD_STATS['idle']) * 100 / dtotal))
        OLD_STATS.update(stat_vals)
    except Exception, e:
        logger.exception(e)

    temp = '--'
    try:
        temp = '%02d %s' % (int(temp_vals['temp'][0]), temp_vals['unit'][0])
    except Exception, e:
        logger.exception(e)

    return (BAR_NORMAL_COLORS, 'CPU: %s MHz (%s%%) [%s]' % (cpu, load, temp))
