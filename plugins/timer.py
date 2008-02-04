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

import time
import datetime
import logging

from pydzen import utils

logger = logging.getLogger('plugin.cpu')

def format_td(seconds):
    td = datetime.timedelta(seconds = seconds)
    sec = td.days * 24 * 60 * 60 + td.seconds 
    min, sec = divmod(sec, 60) 
    hrs, min = divmod(min, 60) 
    return '%02d:%02d:%02d' % (hrs, min, sec) 

@utils.cache(5)
def update():
    try:
        uptime, idletime = [float(field) for field in open('/proc/uptime').read().split()]

        return ['^fg()^bg()%s ' % time.strftime('%Y-%m-%d - %H:%M'),
                '^fg()^bg()uptime: %s ' % format_td(uptime)]
    except StandardError, e:
        logger.warn(e)

    return None
