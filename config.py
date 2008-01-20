#
# vim:syntax=python:sw=4:ts=4:expandtab

PLUGINS = ('plugins.mpd',
           'plugins.wlan',
           'plugins.load',
           'plugins.mem',
           'plugins.cpu',
           'plugins.battery',
           'plugins.datetime',
          )

FONT = '-artwiz-snap-*-*-*-*-*-100-*-*-*-*-*-*'

FG_COLOR = '#b6b4b8'                # default foreground color
BG_COLOR = '#1c2636'                # default background color

FG_COLOR_NOTICE = '#FFFF00'         # notice foreground color
BG_COLOR_NOTICE = BG_COLOR          # notice background color

FG_COLOR_URGENT = '#FF0000'         # urgent foreground color
BG_COLOR_URGENT = BG_COLOR          # urgent background color

DZEN_OPTIONS = dict(fg = FG_COLOR, 
                    bg = BG_COLOR, 
                    fn = FONT,
                    ta = 'r',
                    sa = 'r',
                    x = 620,
                    l = 1,
                    u = True,
                    e = 'button1=togglecollapse;')

GDBAR_OPTIONS = dict(fg = FG_COLOR,
                     bg = '#47484A',
                     ss = 1,
                     sw = 2,
                     h = 6,
                     w = 30,
                     nonl = True)

JOINTS = '  ^fg(grey60)^r(1x8)^fg()  '

ICON_PATH = '/home/fire/.xmonad/icons'

DZEN = 'dzen2'
GDBAR = 'gdbar'
