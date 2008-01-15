# python-wmii mpd status plugin v.0.1
#
# Description: 
# ------------
# Display the state of MPD in the wmii status bar. 
# Requires the mpdlib2 library, part of pympd.
#
# Install:
# -------
# Copy this file in ~/.wmii-3.5/statusbar/
#
# How I use it:
# -------------
# I have some global bindings set up to control MPD, via mpc,
# using xbindkeys. (could use directly the wmii keybinding system
# but I prefer to access these functions from any window manager.
# This small plugin allows me to have some visual feedback by 
# showing the current playing song, if any.
#
# Can also be used as a stand-alone script:
#	python 10_mpd.py | dzen2
# (passes the output to dzen)
#
# Updates:
# --------
# 2007-11-28    simplify update() function, update songstr()
#               to generate better output, add logger, add to 
#               python-wmii mercurial repository
#
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

has_pympd = False
try:
    from pympd.modules import mpdlib2
    has_pympd = True
except:
    pass

try:
    from config import BAR_NORMAL_COLORS
except:
    BAR_NORMAL_COLORS=None
 
logger = logging.getLogger('statusbar.mpd')

SONG_MAX = 30
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
                song = ''
                if status.state in ('play', 'pause'):
                    song = ' %s' % songstr(mpd.currentsong())
                return (BAR_NORMAL_COLORS, 'MPD: [%s]%s' % (status.state, song))
        except Exception, e:
            logger.exception(e)
            mpd = None  # try to reconnect if connection is lost

    return None



if __name__ == "__main__":  # stand-alone mode, outside of python-wmii
    import sys
    import time

    while True:
        res = update()
        if res:
            print res[1]
		time.sleep(interval())
