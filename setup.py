#!/usr/bin/env python
# -*- coding: utf8 -*-

from distutils.core import setup

setup(
    name='HA-Spixy',
    version='0.0.1',
    description='High-Availibility Spixy',
    author='Johan Hägg',
    author_email='johan.hagg@shard.se',
    url='https://github.com/jhaegg/HA-Spixy',
    packages=['spixy'],
    install_requires=[
        'requests-futures'
    ]
)
