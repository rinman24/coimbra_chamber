"""Setup."""

from distutils.core import setup

setup(
    name='Chmaber',
    version='2.1.0',
    author='Rich H. Inman',
    author_email='rinman24@gmail.com',
    packages=[
        'coimbra_chamber.access',
        'coimbra_chamber.engine',
        'coimbra_chamber.ifx',
        'coimbra_chamber.manager'
        ],
    url='https://github.com/rinman24/coimbra_chamber',
    license='LICENSE.txt',
    description=(
        'Python programs for Rich Inman\'s PhD work involving the Coimbra '
        'Chamber at UCSD.'
        ),
    long_description=open('README.rst').read()
    )
