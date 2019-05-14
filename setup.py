"""Setup."""

from distutils.core import setup

setup(
    name='Chmaber',
    version='2.1.0',
    author='Rich H. Inman',
    author_email='rinman24@gmail.com',
    packages=[
        'chamber.access',
        'chamber.engine',
        'chamber.ifx',
        'chamber.manager'
        ],
    url='https://github.com/rinman24/inman_phd',
    license='LICENSE.txt',
    description=(
        'Python programs for Rich Inman\'s PhD work involving the Coimbra '
        'Chamber at UCSD.'
        ),
    long_description=open('README.rst').read()
    )
