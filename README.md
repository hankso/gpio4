# gpio4
Control gpio in python on Linux.

Improved version based on Sysfs, features same as RPi.GPIO and [gpio3](https://pypi.org/project/gpio3)

Support `RaspberryPi / OrangePi / BananaPi...`


# Attention
Don't run this on your PC because gpios of computer are usually protected.


# Installation
Install from PyPI is suggested.

```bash
pip install gpio4
```

Or install from source.

```bash
git clone git@github.com:hankso/gpio4.git
cd gpio4
python setup.py build && sudo python setup.py install
```


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

Try the most basic but fastest Sysfs class

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

If you have any question on usage, it is strongly recommended to directly read well commented source codes. Also check [kernel doc of sysfs](https://www.kernel.org/doc/Documentation/gpio/sysfs.txt), and [this article](https://www.acmesystems.it/gpio_sysfs).
