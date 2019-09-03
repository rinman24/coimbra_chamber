#?/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys

from setuptools import find_packages, setup

from coimbra_chamber.__version__ import VERSION

# Package meta-data
NAME = 'coimbra_chamber'
DESCRIPTION = (
    "Python programs for Rich Inman's PhD work involving the Coimbra "
    "Chamber at UCSD."
)
URL = 'https://github.com/rinman24/coimbra_chamber'
EMAIL = 'rinman24@gmail.com'
AUTHOR = 'Rich H. Inman'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = '.'.join(map(str, VERSION))

# What packages are required for this module to be executed
REQUIRED = [
    'dacite>=1.0.2',
    'matplotlib>=3.1.1',
    'mysql-connector-python>=8.0.17',
    'numpy>=1.17.1',
    'pandas>=0.25.1',
    'scipy>=1.3.1',
    'uncertainties>=3.1.2',
    'coolprop>=6.3.0',
    'nptdms>=0.15.1',
    'sqlalchemy>=1.3.8',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# NOTE: this will only work if 'README.rst' is present in your MANIFEST.in file.
try:
    with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the packages's __version__.py module as a dictionary.
about ={}
if not VERSION:
    project_slug = NAME.lower().replace('-', '_').replace(' ', '_')
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    install_requires=REQUIRED,
    extra_require=EXTRAS,
    include_package_data=True,
    license='LICENSE.txt',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
