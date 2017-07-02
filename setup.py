#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='meli-sdk',
    version='0.1',
    packages=find_packages(exclude=['test']),
    install_requires=['requests']
)
