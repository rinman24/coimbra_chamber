UCSD Coimbra Chamber
====================

|docs|

.. image:: images/coimbra_ucsd_logo.png

Table of Contents
-----------------

  * `Description`_
  * `Python Version`_
  * `Documentation`_
  * `Dependencies`_
  * `Setting up Initial State of MySQL Database`_
  * `Repo Directory Structure`_
  * `Preferred Way to Run Tests`_
  * `Images`_

Description
-----------

Back to `Table of Contents`_

Description will go here.

Make sure that you export your MySQLCredentials environment variable for
access
::

    $ export MySqlUserName=<user_name>
    $ export MySqlCredentials=<password>
    $ export MySqlHost=<host>

Python Version
--------------

Back to `Table of Contents`_

This module is intended to use Python 3.x.

Documentation
-------------

Back to `Table of Contents`_

For detailed documentaton head over to `read the docs`_.

Dependencies
------------

Back to `Table of Contents`_

  * CoolProp.HumidAirProp.HAPropsSI (for humid air calculations)
  * matplotlib.pyplot
  * matplotlib.legend_handler.HandlerLine2D
  * mysql.connector (for access to MySQL databases)
  * nptdms (for interacting with LabVIEW TDMS files)
  * pytest (for testing)
  * pytz (for datetime testing)
  * schedule (for autonomous execution)
  * tabulate.tabulate (for table formatting)

Setting up Initial State of MySQL Database
------------------------------------------

Back to `Table of Contents`_

Setting up the initial state of the MySQL Server is handled by the
setup_sqldb.py file.
Simply run the following command from the root directory; e.g., ucsd_ch:
::

  $ python setup/setup_sqldb.py <database_name>


Where <database_name> is replaced with the name of the MySQL database schema.
This will create all tables and populate the Unit table and add Tube 1
(default tube used in experiments).

The database schema is described below:

.. image:: images/mysql_schema.png

Repo Directory Structure
------------------------

Back to `Table of Contents`_

The structure of the directory
::

    ├── data_transfer_script.bat
    ├── LICENSE.txt
    ├── README.rst
    ├── chamber
    |   ├── __init__.py
    |   ├── const.py
    |   ├── laser.py
    |   ├── properties.py
    |   ├── results.py
    |   ├── runner.py
    |   ├── sqldb.py
    |   ├── tools.py
    |   └── water.py
    ├── images
    |   ├── chamber_iso_view.jpg
    |   ├── chamber_optics.jpg
    |   ├── chamber_profile.jpg
    |   ├── chamber_scale.jpg
    |   ├── coimbra_ucsd_logo.png
    |   └── mysql_schema.png
    ├── setup
    |   ├── add_tube.py
    |   └── setup_sqldb.py
    └── tests
        ├── data_transfer_test_files
        ├── test_const.py
        ├── test_laser.py
        ├── test_properties.py
        ├── test_results.py
        ├── test_sqldb.py
        ├── test_tools.py
        └── test_water.py

Preferred Way to Run Tests
---------------------------

Back to `Table of Contents`_

1. From the repo directory; i.e., ucsd_ch
::

    $ python -m pytest tests/<your-test-name>.py -v --capture=no

It should also be noted that the test_const.py file in the test directory
does not acctually contain tests, but rather the constants that are
needed for testing.

Images
------

Back to `Table of Contents`_

.. image:: images/chamber_iso_view.jpg

.. image:: images/chamber_scale.jpg

.. image:: images/chamber_profile.jpg

.. image:: images/chamber_optics.jpg


.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://docs.readthedocs.io/en/latest/?badge=latest

.. _`read the docs`: http://chamber.readthedocs.io
