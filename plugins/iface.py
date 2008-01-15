#
# Copyright (C) 2007 Alexander Bernauer (alex at copton dot net)
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

from utils.statusbar import execute
from config import BAR_NORMAL_COLORS

logger = logging.getLogger('statusbar.iface')


def interval():
    return 5


def update():
    try:
        s = ""
        for iface in ['eth0', 'wlan0']:
            s += iface + ": "
            out, err = execute(['ip', 'a', 's', iface])
            lines = out.split('\n')

            if re.search("UP", lines[0]) == None:
                s += "off "
            for l in lines[1:]:
                mo = re.search("inet\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", l)
                if mo:
                    s += mo.group(1) + " "

        return (BAR_NORMAL_COLORS, s)
    except Exception, e:
        logger.exception(e)
