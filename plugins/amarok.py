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
import logging

from pydzen import config, utils

# ------- user config ----------------------------------------------------------
SONG_MAX = 100

ICON_STOP = os.path.join(config.ICON_PATH, 'stop.xbm')
ICON_PLAY = os.path.join(config.ICON_PATH, 'play.xbm')
ICON_PAUSE = os.path.join(config.ICON_PATH, 'pause.xbm')
# ------- user config ----------------------------------------------------------

logger = logging.getLogger('plugin.mpd')

has_pydcop = False
try:
    import pydcop
    has_pydcop = True
except:
    logger.warn('no python dcop module installed')

amarok = None

def songstr(song):
    s = ''
    if 'title' in song:
        if song['artist']:
            s += song['artist'] + ' - '
        s += song['title']
        if song['album']:
            s += '(%s)' % song['album']
    else:
        s = song.get('path', '')

    if s and len(s) > SONG_MAX:
        s = '..%s' % s[len(s) - SONG_MAX:]
    return s

AMAROK_STOP, AMAROK_PAUSE, AMAROK_PLAY = range(0, 3)

@utils.cache(2)
def update():
    global amarok

    if has_pydcop:
        try:
            if 'amarok' in pydcop.apps():
                if not amarok:
                    amarok = pydcop.DCOPObject('amarok', 'player')

                state = dict(artist = amarok.artist(),
                             album = amarok.album(),
                             title = amarok.title(),
                             currentTime = amarok.trackCurrentTime(),
                             totalTime = amarok.trackTotalTime(),
                             status = amarok.status())

                song = '--'
                if state['status'] != AMAROK_STOP:
                    song = ' %s' % songstr(state)
                icon = { AMAROK_PLAY: ICON_PLAY,
                         AMAROK_PAUSE: ICON_PAUSE,
                         AMAROK_STOP: ICON_STOP}.get(state['status'], ICON_STOP)
                progress = ''
                progress_detail = ''
                if state['status'] != AMAROK_STOP:
                    state['currentMin'] = state['currentTime'] / 60
                    state['currentSec'] = state['currentTime'] % 60
                    state['totalMin'] = state['totalTime'] / 60
                    state['totalSec'] = state['totalTime'] % 60
                    state['song'] = song

                    progress = utils.gdbar('%(currentTime)d %(totalTime)d' % state,
                                           l = '%d%% ' % (100. / state['totalTime'] * state['currentTime']))
                    progress_detail = '[%(currentMin)02d:%(currentSec)02d/%(totalMin)02d:%(totalSec)02d]' % state
                return ['Amarok: ^i(%s)%s' % (icon, progress),
                        'Amarok: %s%s' % (song, progress_detail)]
        except (StandardError, RuntimeError), e:
            amarok = None  # try to reconnect if connection is lost
            logger.warn(e)

    return None

