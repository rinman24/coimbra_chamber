"""Setup."""

from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='coimbra_chamber',
    version='0.0.1',
    author='Rich H. Inman',
    description=(
        'Python programs for Rich Inman\'s PhD work involving the Coimbra '
        'Chamber at UCSD.'
        ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    author_email='rinman24@gmail.com',
    packages=[
        'coimbra_chamber.access',
        'coimbra_chamber.engine',
        'coimbra_chamber.ifx',
        'coimbra_chamber.manager'
        ],
    url='https://github.com/rinman24/coimbra_chamber',
    license='LICENSE.txt',
    long_description=long_description,
    )
