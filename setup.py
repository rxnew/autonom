#!/usr/bin/env python

import os
import re

from setuptools import setup, find_packages

ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


def get_version():
    init = open(os.path.join(ROOT, 'autonom', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='autonom',
    version=get_version(),
    author='rxnew',
    url='https://github.com/rxnew/autonom',
    packages=find_packages(exclude=['tests*']),
    scripts=['scripts/autonom'],
    install_requires=[
        'awsiotpythonsdk>=1.4.7',
        'ansible-api>=0.5.0',
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
)
