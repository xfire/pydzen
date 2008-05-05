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
# original written by Julia Evans <dotbork@gmail.com>
#
# vim:syntax=python:sw=4:ts=4:expandtab

import os
import time
import urllib
from xml.dom import minidom

from pydzen import config, utils

WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?p=%s&u=%s'
WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'
# to add some more data (forecasts, etc), see examples at: http://developer.yahoo.com/python/python-xml.html

# user settings
# frequency with which to update (in minutes)
update_interval = 10

# units: should be f or c (fahrenheit or celsius)
units  = 'c'

# weather zone (according to Yahoo! weather)
# you can put an American zip code here.
# If you're not american, go to http://weather.yahoo.com/, search for your city, copy it out of the URL
# zone = '90210'
zone = 'SZXX0054' # st. gallen

def get_weather(zone, units):
    url = WEATHER_URL % (zone , units)
    dom = minidom.parse(urllib.urlopen(url))
    ycondition = dom.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]
    condition = ycondition.getAttribute('text')
    temp = ycondition.getAttribute('temp'),
    return "%s %sC" % (condition, temp[0])

@utils.cache(update_interval)
def update():
    try:
        data = get_weather(zone, units)
    except:
        data = 'N/A'
    data = 'weather: %s' % data
    return [data, data]
