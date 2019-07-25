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
    packages=find_packages(exclude=['tests*']),
    scripts=['scripts/autonom'],
    install_requires=['awsiotpythonsdk', 'ansible-api'],
)
