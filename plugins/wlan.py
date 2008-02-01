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

from pydzen import config, utils

# ------- user config ----------------------------------------------------------
INTERVAL = 1
IFACE = 'wlan0'
ICON_UP = os.path.join(config.ICON_PATH, 'net_up.xbm')
ICON_DOWN = os.path.join(config.ICON_PATH, 'net_down.xbm')
# ------- user config ----------------------------------------------------------

logger = logging.getLogger('plugin.wlan')

RX_STAT = '/sys/class/net/%s/statistics/rx_bytes' % IFACE
TX_STAT = '/sys/class/net/%s/statistics/tx_bytes' % IFACE

RE_RXTX_STAT = re.compile(r'^(?P<val>\d+)$')

try:
    OLD_STATS = (int(utils.parse_file(RX_STAT, RE_RXTX_STAT)['val'][0]),
                 int(utils.parse_file(TX_STAT, RE_RXTX_STAT)['val'][0]))
except:
    OLD_STATS = (0, 0)

def update():
    global OLD_STATS
    try:
        nrx = int(utils.parse_file(RX_STAT, RE_RXTX_STAT)['val'][0])
        ntx = int(utils.parse_file(TX_STAT, RE_RXTX_STAT)['val'][0])

        rx = (nrx - OLD_STATS[0]) / 1024 / INTERVAL
        tx = (ntx - OLD_STATS[1]) / 1024 / INTERVAL

        OLD_STATS = (nrx, ntx)

        # lq = utils.parse_app('/sbin/iwconfig', re.compile(r'^.*Link Quality.(?P<val>(\d+))\/(?P<max>(\d+)).*$', re.M))
        # lqbar = utils.gdbar('%s %s' % (lq['val'][0], lq['max'][0]), sw = 1, ss = 1, w = 15 ) 

        return '%s: %dkB/s^i(%s) %dkB/s^i(%s)' % (IFACE, rx, ICON_DOWN, tx, ICON_UP)
    except StandardError, e:
        logger.warn(e)

    return None
