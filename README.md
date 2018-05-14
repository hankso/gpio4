# gpio4
Python module to control gpio on Linux.

IMporoved gpio module based on sysfs and RPi.GPIO and gpio3 features

Support `RaspberryPi/OrangePi/BananaPi...`

# Usage
Want something like RPi.GPIO?
```python
>>> import gpio4.GPIO as GPIO
>>> GPIO.setmode(GPIO.BOARD_orangepi_zero_plus)
>>> GPIO.setup(12, GPIO.OUTPUT)
```

or call functions as you are using Arduino?
```python
>>> from gpio4.Arduino import *
>>> pinMode(13, OUTPUT)
>>> digitalWrite(13, HIGH)
>>> if digitalRead(13):
...     digitalWrite(12, LOW)
```

or most basic and fastest sysfs class?
```python
>>> import gpio4
>>> pin = gpio4.SysfsGPIO(gpio4.BOARD_nanopi[6])
>>> pin.export = True # regist pin through sysfs, same like pinMode()
>>> pin.direction = 'out' # same like pinMode()
>>> print(pin.value) # current level
>>> pin.value = 1 # digitalWrite()
```
