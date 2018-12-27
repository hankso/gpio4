#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="gpio4",
    version="0.0.4",
    author="hankso",
    author_email="hankso1106@gmail.com",
    description=("Improved gpio module based on Sysfs, "
                 "features same as RPi.GPIO and gpio3"),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/hankso/gpio4",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: System :: Hardware :: Hardware Drivers"
    ]
)
