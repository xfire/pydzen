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
import math

from pydzen import config, utils

logger = logging.getLogger('plugin.battery')

# ------- user config ----------------------------------------------------------
FILE_BAT_INFO = '/proc/acpi/battery/C1BE/info'
FILE_BAT_STATE = '/proc/acpi/battery/C1BE/state'
FILE_AC = '/proc/acpi/ac_adapter/C1BC/state'

ICON_BAT = os.path.join(config.ICON_PATH, 'battery.xbm')
ICON_AC = os.path.join(config.ICON_PATH, 'ac.xbm')
# ------- user config ----------------------------------------------------------

RE_FULL_CAPACITY = re.compile(r'^last full capacity:\s+(?P<lastfull>\d+).*$')
RE_REMAINING_CAPACITY = re.compile(r'^remaining capacity:\s+(?P<remain>\d+).*$')
RE_PRESENT_RATE = re.compile(r'^present rate:\s+(?P<rate>\d+).*$')
RE_AC_ONLINE = re.compile(r'^state:\s*(?P<state>on.line).*$')

@utils.cache(2)
def update():
    try:
        fg_color = config.FG_COLOR
        icon = ICON_AC

        ac_vals = utils.parse_file(FILE_AC, RE_AC_ONLINE)
        bat_vals = utils.parse_file([FILE_BAT_INFO, FILE_BAT_STATE], [RE_FULL_CAPACITY, RE_REMAINING_CAPACITY, RE_PRESENT_RATE])

        lastfull = float(bat_vals['lastfull'][0])
        remain = float(bat_vals['remain'][0])
        rate = float(bat_vals['rate'][0])

        percent = math.floor(remain / lastfull * 100.0 + 0.5)
        if percent < 25:
            fg_color = config.FG_COLOR_URGENT
        elif percent < 50:
            fg_color = config.FG_COLOR_NOTICE
        bat = utils.gdbar('%s %s' % (remain, lastfull))

        ac = ''
        if not ac_vals and rate > 0:
            mins = (3600.0 * (remain / rate)) / 60.0
            hours = math.floor(mins / 60.0)
            mins = math.floor(mins - (hours * 60.0))
            ac = ' %02d:%02d' % (hours, mins)
            icon = ICON_BAT

        return '^fg(%s)^i(%s)%s%s^fg()' % (fg_color, icon, bat, ac)
    except StandardError, e:
        logger.warn(e)

    return None
