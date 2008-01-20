# ------------------------------------------------------------
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
# Copyright (C) 2007 Brescan Florin ( ratzunu at gmail ... )

# vim:syntax=python:sw=4:ts=4:expandtab

import os
import logging

import config
import utils

# ------- user config ----------------------------------------------------------
SONG_MAX = 100

ICON_STOP = os.path.join(config.ICON_PATH, 'stop.xbm')
ICON_PLAY = os.path.join(config.ICON_PATH, 'play.xbm')
ICON_PAUSE = os.path.join(config.ICON_PATH, 'pause.xbm')
# ------- user config ----------------------------------------------------------

has_pympd = False
try:
    from pympd.modules import mpdlib2
    has_pympd = True
except:
    pass

logger = logging.getLogger('statusbar.mpd')

mpd = None

def interval():
    return 3

def songstr(song):
    s = ''
    if 'title' in song:
        if 'artist' in song:
            s += song['artist'] + ' - '
        s += song['title']
    else:
        s = song.get('file', '')

    if s and len(s) > SONG_MAX:
        s = '..%s' % s[len(s) - SONG_MAX:]
    return s

def update():
    global mpd
        
    if has_pympd:
        try:
            if not mpd:
                mpd = mpdlib2.connect()

            status = mpd.status()

            if status:
                song = '--'
                if status.state != 'stop':
                    song = ' %s' % songstr(mpd.currentsong())
                icon = dict(play = ICON_PLAY, pause = ICON_PAUSE, stop = ICON_STOP).get(status.state, '')
                progress = ''
                if 'time' in status:
                    progress = utils.gdbar('%s %s' % tuple(status['time'].split(':')))
                return ['MPD: ^i(%s)%s' % (icon, progress),
                        'MPD: %s' % song]
        except Exception, e:
            logger.exception(e)
            mpd = None  # try to reconnect if connection is lost

    return None



if __name__ == "__main__":  # stand-alone mode, outside of python-wmii
    print update()
