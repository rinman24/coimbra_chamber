from distutils.core import setup

setup(
    name='Chmaber',
    version='0.1.0',
    author='Rich H. Inman',
    author_email='rinman24@gmail.com',
    packages=['chamber', 'chamber.data', 'chamber.models',
              'chamber.tools', 'chamber.analysis'],
    url='https://github.com/rinman24/chamber',
    license='LICENSE.txt',
    description=('Python programs for Rich Inman\'s PhD work involving the the'
                 'Coimbra Chamber at UCSD. '),
    # long_description=open('README.rst').read(),
    # install_requires=[
    # "nptdms >= 1.1.1",
    # "test2 == 0.1.4",
    # ],
)
