#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 01:17:55 2018

@author: hank
@page:   https://github.com/hankso
"""
import threading
import time
from gpio4.constants import *
from gpio4 import GPIO


'''
Digital I/O
'''
def pinMode(pin, state):
    GPIO.setup(pin, state)


def digitalWrite(pin, value):
    try:
        GPIO.output(pin, value)
    except NameError:
        raise NameError(('Pin {} is not setup yet, please run'
                         '`pinMode({}, state)` first!').format(pin, pin))


def digitalRead(pin):
    try:
        return GPIO.input(pin)
    except NameError:
        raise NameError(('Pin {} is not setup yet, please run'
                         '`pinMode({}, state)` first!').format(pin, pin))


'''
Advanced I/O
'''
def tone(pin, frequency, duration=None):
    p = GPIO.PWM(pin, frequency)
    p.start(50)
    if duration is not None and duration > 0:
        threading.Timer(duration, lambda *args, **kwargs: p.stop()).start()


def noTone(pin):
    GPIO.PWM(pin).stop()


def pulseIn(pin, value, timeout=FOREVER_ms):
    # wait for any previous pulse end
    start = micros()
    while digitalRead(pin) == value:
        if (micros() - start) > timeout:
            return 0
    # wait for the pulse to start
    while digitalRead(pin) != value:
        if (micros() - start) > timeout:
            return 0
    start = micros()
    # wait for the pulse to end
    while digitalRead(pin) == value:
        if (micros() - start) > timeout:
            return 0
    return micros() - start


def shiftIn(dataPin, clockPin, bitOrder):
    digitalWrite(clockPin, LOW)
    value = 0
    if bitOrder == MSBFIRST:
        for i in range(8):
            digitalWrite(clockPin, HIGH)
            value |= digitalRead(dataPin) << (7 - i)
            digitalWrite(clockPin, LOW)
    elif bitOrder == LSBFIRST:
        for i in range(8):
            digitalWrite(clockPin, HIGH)
            value |= digitalRead(dataPin) << i
            digitalWrite(clockPin, LOW)
    else:
        raise ValueError('Invalid bitOrder: {}'.format(bitOrder))
    return value


def shiftOut(dataPin, clockPin, bitOrder, value):
    if bitOrder == MSBFIRST:
        for i in range(8):
            digitalWrite(clockPin, LOW)
            digitalWrite(dataPin, value & (1 << (7 - i)))
            digitalWrite(clockPin, HIGH)
    elif bitOrder == LSBFIRST:
        for i in range(8):
            digitalWrite(clockPin, LOW)
            digitalWrite(dataPin, value & (1 << i))
            digitalWrite(clockPin, HIGH)
    else:
        raise ValueError('Invalid bitOrder: {}'.format(bitOrder))


'''
Time
'''
def delay(timeout):
    time.sleep(timeout/1000.0)


def delayMicroseconds(timeout):
    time.sleep(timeout/1000000.0)


def micros():
    return time.time() * 1000


def millis():
    return time.time() * 1000000


'''
Math
'''
def constrain(x, a, b):
    return max(min(x, b), a)


def map(x, low, high, t_low, t_high):
    return float(x-low) / (high-low) * (t_high-t_low) + t_low


'''
Bits and Bytes
'''
def bitClear(x, n):
    return bitWrite(x, n, 0)


def bitSet(x, n):
    return bitWrite(x, n, 1)


def bitRead(x, n):
    return (x >> n) & 0x01


def bitWrite(x, n, b):
    if b:
        x |= 1 << n
    else:
        x &= ~(1 << n)
    return x


def highByte(x):
    return (x >> 8) & 0xff


def lowByte(x):
    return x & 0xff


'''
External Interrupts
'''
def attachInterrupt(pin, ISR, mode):
    GPIO.add_event_detect(pin, edge=mode, callback=[ISR])


def detachInterrupt(pin):
    GPIO.remove_event_detect(pin)


def interrupts():
    GPIO.enable_interrupts()


def noInterrupts():
    GPIO.disable_interrupts()



__all__ = ['HIGH', 'LOW', 'OUTPUT', 'INPUT', 'INPUT_PULLUP', 'INPUT_PULLDN',
           'MSBFIRST', 'LSBFIRST', 'true', 'false',
           'pinMode', 'digitalWrite', 'digitalRead', 'tone', 'noTone',
           'pulseIn', 'shiftIn', 'shiftOut', 'constrain', 'map',
           'delay', 'delayMicroseconds', 'micros', 'millis',
           'bitClear', 'bitSet', 'bitRead', 'bitWrite', 'highByte', 'lowByte',
           'attachInterrupt', 'detachInterrupt', 'interrupts', 'noInterrupts']
