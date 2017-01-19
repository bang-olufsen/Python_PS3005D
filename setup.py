#!/usr/bin/env python

from distutils.core import setup

setup(name='PS3005D',
    version='0.1',
    description='PS3005D logger',
    author='Ekidna Engineering',
    author_email='sales@ekidna-engineering.com',
    url='http://www.ekidna-engineering.com',
    packages=['ps3005d'],
    entry_points = 
    {
        'console_scripts': 
        [
            'ps3005d = ps3005d.main:main',
        ]
    }
)