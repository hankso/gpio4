#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 18:14:02 2018

@author: hank
@page:   https://github.com/hankso
"""

import re

class _sunxi():
    def __getitem__(self, pin):
        rst = re.findall(r"P([A-Z])(\d+)", str(pin))
        if not rst:
            raise KeyError('pin name {} not supported!'.format(pin))
        return 32*(ord(rst[0][0])-65) + int(rst[0][1])


RISING       = 'rising'
FALLING      = 'falling'
CHANGE       = 'change'
HIGH         = 1
LOW          = 0
INPUT        = 'in'
OUTPUT       = 'out'
INPUT_PULLUP = 'pullup'
INPUT_PULLDN = 'pulldn'
MSBFIRST     = 1
LSBFIRST     = 2
true         = True
false        = False
FOREVER      = 1e5
FOREVER_ms   = 1e5 * 1000

BOARD_SUNXI = _sunxi()
BOARD_NANO_PI = {}
BOARD_ORANGE_PI_PC = {}
BCM = {}

__all__ = ['RISING', 'FALLING', 'CHANGE', 'HIGH', 'LOW',
           'OUTPUT', 'INPUT', 'INPUT_PULLUP', 'INPUT_PULLDN',
           'MSBFIRST', 'LSBFIRST', 'true', 'false', 'FOREVER', 'FOREVER_ms',
           'BOARD_SUNXI', 'BOARD_NANO_PI', 'BOARD_ORANGE_PI_PC', 'BCM']
