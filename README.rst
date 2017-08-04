====================
UCSD Coimbra Chamber
====================

.. image:: images/coimbra_ucsd_logo.png

Table of Contents
-----------------

  * `Description`_
  * `Python Version`_
  * `Dependencies`_
  * `Setting up Initial State of MySQL Database`_
  * `Repo Directory Structure`_
  * `Preferred Way to Run Tests`_
  * `Images`_

Description
-----------

Back to `Table of Contents`_

Description will go here.

Make sure that you export your MySQLCredentials environment variable for access
::

    $ export MySqlUserName=<user_name>
    $ export MySqlCredentials=<password>
    $ export MySqlHost=<host>
    $ export MySqlDataBase=<database>

Python Version
--------------

Back to `Table of Contents`_

This module is intended to use Python 3.x.

Dependencies
------------

Back to `Table of Contents`_

  * matplotlib.pyplot
  * mysql.connector (for access to MySQL databases)
  * nptdms (for interacting with LabVIEW TDMS files)
  * pytest (for testing)
  * pytz (for datetime testing)

Setting up Initial State of MySQL Database
------------------------------------------

Back to `Table of Contents`_

Setting up the initial state of the MySQL Server is handled by the setup_sqldb.py file.
Simply run the following command from the root directory; e.g., ucsd_ch:
::

  $ python chamber/setup_sqldb.py

This will create all tables and populate the Unit table as well.

The database schema is described below:

.. image:: images/mysql_schema.png

Repo Directory Structure
------------------------

Back to `Table of Contents`_

The structure of the directory
::

    ├── README.rst
    ├── chamber
    |   ├── __init__.py
    |   ├── const.py
    |   ├── laser.py
    |   ├── properties.py
    |   ├── sqldb.py
    |   └── tools.py
    ├── images
    |   ├── coimbra_ucsd_logo.png
    |   └── mysql_schema.png
    ├── setup
    |   ├── add_tube.py
    |   └── setup_sqldb.py
    └── tests
        ├── test_const.py
        ├── test_laser.py
        ├── test_properties.py
        ├── test_sqldb.py
        └── test_tools.py

Preferred Way to Run Tests
---------------------------

Back to `Table of Contents`_

1. From the repo directory; i.e., ucsd_ch
::

    $ python -m pytest tests/<your-test-name>.py -v --capture=no

Images
------

.. image:: images/chamber_iso_view.jpg

.. image:: images/chamber_scale.jpg

.. image:: images/chamber_profile.jpg

.. image:: images/chamber_optics.jpg