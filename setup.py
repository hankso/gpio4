#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_des = f.read()

setup(
    name="gpio4",
    version="0.0.2",
    author="hankso",
    author_email="3080863354@qq.com",
    description=("Improved gpio module based on Sysfs, "
                 "features same as RPi.GPIO and gpio3"),
    long_description=long_des,
    url="https://github.com/hankso/gpio4",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: System :: Hardware :: Hardware Drivers"
    ]
)
