====================
UCSD Coimbra Chamber
====================

.. image:: images/coimbra_ucsd_logo.png

Table of Contents
-----------------

  * `Description`_
  * `Python Version`_
  * `Dependencies`_
  * `Repo Directory Structure`_
  * `Preferred Way to Run Tests`_

Description
-----------

Back to `Table of Contents`_

Description will go here.

Python Version
--------------

Back to `Table of Contents`_

This module is intended to use Python 3.x.
Backward compatability with Python 2.x. has not been tested.

Dependencies
------------

Back to `Table of Contents`_

  * matplotlib.pyplot

Repo Directory Structure
------------------------

Back to `Table of Contents`_

The structure of the directory
::

    ├── README.rst
    ├── chamber
    |   ├── __init__.py
    |   └── const.py
    |   └── laser.py
    ├── images
    |   └── coimbra_ucsd_logo.png
    └── tests
        └── test_const.py
        └── test_laser.py

Preferred Way to Run Tests
---------------------------

Back to `Table of Contents`_

1. From the repo directory; i.e., ucsd_ch
::

    $ python -m pytest tests/<your-test-name>.py -v