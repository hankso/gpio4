# gpio4
Python module to control gpio on Linux.

Improved gpio module based on sysfs and RPi.GPIO and gpio3 features

Support `RaspberryPi/OrangePi/BananaPi...`

# Usage
Want something like RPi.GPIO?
```python
>>> import gpio4.GPIO as GPIO
>>> GPIO.setmode(GPIO.BCM)
>>> GPIO.setup([12, 13], GPIO.IN)
>>> GPIO.input([12, 13])
[0, 0]
>>> p = GPIO.PWN(12) # it will automatically setup this pin to output first
>>> p.start(30) # duty cycle is 30%
...
>>> from gpio4.constants import BOARD_NANO_PI as BOARD
>>> GPIO.setmode(BOARD)
>>> GPIO.setup([6, 7, 9], GPIO.OUTPUT)
>>> GPIO.output([6, 7, 9], [GPIO.HIGH, GPIO.LOW, GPIO.HIGH])
>>> GPIO.add_event_detect(8, GPIO.RAISING, bouncetime=300)
```

or call functions as you are using Arduino?
```python
>>> from gpio4.arduino import *
>>> pinMode(13, OUTPUT)
>>> pinMode(12, INPUT_PULLUP)
>>> digitalWrite(13, HIGH)
>>> digitalWrite(13, digitalRead(12))
>>> shiftIn(dataPin=12, clockPin=13, bitOrder=MSBFIRST)
170
```

or most basic but fastest sysfs class?
```python
>>> from gpio4 import SysfsGPIO
>>> from gpio4.constants import BOARD_ORANGE_PI_PC
>>> pin_name = 6
>>> pin_num = BOARD_ORANGE_PI_PC[pin_name]
>>> pin = SysfsGPIO(pin_num)
>>> pin.export = True # regist pin through sysfs, same like pinMode()
>>> pin.direction = 'out' # same like pinMode()
>>> print(pin.value) # current level
>>> pin.value = 1 # same like digitalWrite()
>>> pin.export = False # clear this pin from sysfs
```
