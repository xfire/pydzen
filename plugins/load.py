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
import config

def update():
    lavg = os.getloadavg()

    fg_color = config.FG_COLOR
    if max(lavg) > 1.5:
        fg_color = config.FG_COLOR_NOTICE
    if max(lavg) > 4.0:
        fg_color = config.FG_COLOR_URGENT

    return '^fg(%s)Load: %.2f %.2f %.2f^fg()' % ((fg_color,) + lavg)
