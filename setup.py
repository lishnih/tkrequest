#!/usr/bin/env python
# coding=utf-8

import sys, os
from setuptools import setup

py_version = sys.version_info[:2]
PY3 = py_version[0] == 3
if PY3:
    if py_version < (3, 3):
        raise RuntimeError('On Python 3, Index requires Python 3.3 or better')
else:
    if py_version < (2, 6):
        raise RuntimeError('On Python 2, Index requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
try:
    README = open(os.path.join(here, 'README.md')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''


from tkrequest.lib.info import __pkgname__, __description__, __version__


if __name__ == '__main__':
    setup(
        name = __pkgname__,
        description = __description__,
        version = __version__,
        long_description = __doc__,

        author = 'Stan',
        author_email = 'lishnih@gmail.com',
        url = 'http://github.com/lishnih/tkrequest',
        license = 'Public Domain',
        platforms = 'any',
        keywords = ['Tk', 'urllib', 'Request'],

        packages = [__pkgname__, __pkgname__+'/lib'],
        package_data = {__pkgname__: []},
        scripts = [
            'scripts/run_tkrequest.py',
        ],
        install_requires = [
        ],

        classifiers = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: Public Domain',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Topic :: Utilities',
        ],
    )
