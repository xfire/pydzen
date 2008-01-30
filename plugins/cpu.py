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

import os
import re
import logging

import config
import utils

# ------- user config ----------------------------------------------------------
ICON_TEMP = os.path.join(config.ICON_PATH, 'temp.xbm')
# ------- user config ----------------------------------------------------------

logger = logging.getLogger('statusbar.cpu')

FILE_TEMP = '/proc/acpi/thermal_zone/TZ4/temperature'

RE_CPU = re.compile(r'^cpu MHz\s*:\s*(?P<mhz>\d+).*$')
RE_STATS = re.compile(r'^cpu  (?P<user>\d+) (?P<system>\d+) (?P<nice>\d+) (?P<idle>\d+).*$')
RE_TEMP = re.compile(r'^temperature:\s*(?P<temp>\d+)\s+(?P<unit>.*)$')

OLD_STATS = dict(user = 0, system = 0, nice = 0, idle = 0)


def update():
    try:
        cpu_vals = utils.parse_file('/proc/cpuinfo', RE_CPU)
        stat_vals = utils.parse_file('/proc/stat', RE_STATS)
        temp_vals = utils.parse_file(FILE_TEMP, RE_TEMP)

        ghz_vals = [float(i) / 1000 for i in cpu_vals['mhz']]
        cpu = '/'.join(['%.1f' % i for i in ghz_vals])

        stat_vals = dict([(k, int(v[0])) for k, v in stat_vals.items()])
        dtotal = stat_vals['user'] - OLD_STATS['user'] + \
                 stat_vals['system'] - OLD_STATS['system'] + \
                 stat_vals['nice'] - OLD_STATS['nice'] + \
                 stat_vals['idle'] - OLD_STATS['idle']
        if dtotal > 0:
            load = '%02d' % (100 - ((stat_vals['idle'] - OLD_STATS['idle']) * 100 / dtotal))
        else:
            load = '0'
        OLD_STATS.update(stat_vals)

        temp = ''
        try:
            temp = '^i(%s)%02d%s' % (ICON_TEMP, int(temp_vals['temp'][0]), temp_vals['unit'][0])
        except Exception:
            pass

        return 'CPU: %s GHz (%s%%)%s' % (cpu, load, temp)
    except Exception, e:
        logger.warn(e)

    return None
