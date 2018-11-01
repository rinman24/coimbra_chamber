"""Setup."""

from distutils.core import setup

setup(
    name='Chmaber',
    version='2.0.0',
    author='Rich H. Inman',
    author_email='rinman24@gmail.com',
    packages=['chamber.managers', 'chamber.engines', 'chamber.access'],
    url='https://github.com/rinman24/chamber',
    license='LICENSE.txt',
    description=(
        'Python programs for Rich Inman\'s PhD work involving the Coimbra '
        'Chamber at UCSD.'
        ),
    long_description=open('README.rst').read(),
    install_requires=[
        'npTDMS==0.11.3',
        'matplotlib==2.1.0',
        'tabulate==0.8.1',
        'scipy==0.19.1',
        'numpy==1.13.3',
        'pandas==0.22.0',
        'CoolProp==6.1.0',
        'mysql-connector=2.1.6',
        'schedule==0.5.0',
        ],
    )
