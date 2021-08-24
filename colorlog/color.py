#!/usr/bin/env python3

# Tested on Windows 10 (python3.6), Ubuntu 16.4.1 (python3.5)

import os, sys

# this is the magic for ASCII escape sequences of text
# attribute control to work on Windows platform
if sys.platform.lower() == "win32":
    os.system('color')

# Group of Different functions for different styles
# For a list of ASCII sequences that change display graphics, see http://ascii-table.com/ansi-escape-sequences.php
# Text attributes
RESET       = '0'
BOLD        = '1'
UNDERSCORE 	= '4' # on monochrome display adapter only
BLINK       = '5'
REVERSE     = '7'
CONCEALED   = '8'

# Foreground colors
FG_COLOR_START    = 30
FG_BLACK   = 30
FG_RED     = 31
FG_GREEN   = 32
FG_YELLOW  = 33
FG_BLUE    = 34
FG_MAGENTA = 35
FG_CYAN    = 36
FG_WHITE   = 37

# Background colors
BG_COLOR_START    = 40
BG_BLACK   = 40
BG_RED     = 41
BG_GREEN   = 42
BG_YELLOW  = 43
BG_BLUE    = 44
BG_MAGENTA = 45
BG_CYAN    = 46
BG_WHITE   = 47

ALL_COLORS = [
    FG_BLACK, FG_RED, FG_GREEN, FG_YELLOW, FG_BLUE, FG_MAGENTA, FG_CYAN, FG_WHITE,
    BG_BLACK, BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE
    ]


# reset text attribute.
def reset():
    return '\033[{0}m'.format(RESET)

# major function
def deco(s: str, fg_color=0x111, bg_color=None, const_deco='', **kwargs):
    '''
        Params:
        fg_color, bg_color: int or 3-tuple
            if given as a three digit hex integer, each digit
              represents red, green or blue respectively, either 0 or 1.
              for example:
                0x100 red, 0x010 green, 0x001 blue
                0x110 yellow, 0x101  magenta.
            if given a value in the list `ALL_COLORS`, it is used 
              directly.
        kwargs: all kwargs are of boolean type.
            reset:  same as reset() if True, else no effect.
            bold:   set bold.
            underscore: set underscore. on monochrome display adapter only.
            blink:  set blink.
            reverse: reverse backgound and forground color.
            concealed: Concealed on.
    '''
    if not isinstance(s, str):
        s = str(s)
    if not isinstance(const_deco, str):
        const_deco = str(const_deco)

    if const_deco:
        return const_deco + s
    
    fg = _parse_color_param(fg_color, FG_COLOR_START)
    bg = _parse_color_param(bg_color, BG_COLOR_START) if bg_color is not None else ''

    TEXT_ATTR_MAP = {
        'reset': RESET,
        'bold': BOLD,
        'underscore': UNDERSCORE,
        'blink': BLINK,
        'reverse': REVERSE,
        'concealed': CONCEALED,
    }

    attr = []
    for a in kwargs:
        if(kwargs.get(a, False)):
            attr.append(TEXT_ATTR_MAP.get(a))
    attr = ';'.join(attr)

    return '\033[' + ';'.join([x for x in (fg, bg, attr) if x])  + 'm' + s

def _parse_color_param(color_param, color_start):
    if(type(color_param) is int and color_param in ALL_COLORS):
        c = color_param
    else:
        if(type(color_param) is int):
            color_param = [color_param / 0x100, color_param % 0x100 / 0x10, color_param % 0x10]
            color_param = [int(x) for x in color_param]
        
        if(any([x > 1 for x in color_param])):
            raise('Invalid color!')
        c = color_start
        c += 1 * color_param[0]
        c += 2 * color_param[1]
        c += 4 * color_param[2]
    return str(c)


# onvenience functions

def warning(wrnmsg :str):
    wrnmsg = 'Warning:' + wrnmsg
    print(deco(wrnmsg, FG_YELLOW, bold=True), reset())

def error(errmsg :str):
    wrnmsg = 'Error:' + errmsg
    print(deco(wrnmsg, FG_RED, bold=True), reset())
    sys.exit()


# demo usage
if __name__ == '__main__':
    print(deco('Hello, ', 0x011, bold=True) + reset() + 'world!')
    print(deco('Hello, ', reverse=True) + reset() + 'world!')
    print(deco('Hello, ', FG_BLUE, bold=True) + reset() + 'world!')
    print(deco('Hello, ', FG_YELLOW, BG_GREEN, bold=True) + reset() + 'world!')
    print(deco('Hello, ', FG_MAGENTA, bold=True) + reset() + 'w...')
    warning("emmm, seems there is a small proble...")
    error('Unknown error!')

