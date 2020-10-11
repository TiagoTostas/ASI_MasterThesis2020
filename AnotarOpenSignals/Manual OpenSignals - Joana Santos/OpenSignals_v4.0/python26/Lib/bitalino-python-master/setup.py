# -*- coding: utf-8 -*-

"""
BITalino Python API

Setup for package installation.

Created on Nov 27 11:25:00 2013

@author: Carlos Carreiras

"""

import re
from setuptools import setup


def readme():
    with open('README.rst', 'r') as f:
        description = f.read()
    return description


def getVersion():
    VERSIONFILE = 'bitalino/_version.py'
    verstrline = open(VERSIONFILE, 'rt').read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
    return verstr


setup(
    name='bitalino',
    version=getVersion(),
    packages=['bitalino'],
    install_requires=[],
    url='http://www.bitalino.com',
    license='GPL',
    author='Team BIT',
    author_email='bitalino@plux.info',
    description='BITalino Python API.',
    long_description=readme(),
    keywords='BITalino, Physiological Computing, Biosignal, EDA, ECG, EMG, Accelerometer',
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Scientific/Engineering'],
    zip_safe=False
)
