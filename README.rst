UCSD Coimbra Chamber
====================

|docs| |build| |codecov| |license|

.. image:: images/coimbra_ucsd_logo.png

Table of Contents
-----------------

  * `Description`_
  * `Python Version`_
  * `Documentation`_
  * `Dependencies`_
  * `Setting up Initial State of MySQL Database`_
  * `Preferred Way to Run Tests`_
  * `Preferred Way to Run Scripts`_
  * `Images`_

Description
-----------

Back to `Table of Contents`_

Description will go here.

The host, username, and password used to acces the server are all stored in
config.ini in the root of the repository. Make sure to edit this file so that
it contains your information.
::

  [MySQL-Server]
  host = your-host
  user = your-username
  password = your-password

Python Version
--------------

Back to `Table of Contents`_

This module is intended to use Python 3.x.

Documentation
-------------

Back to `Table of Contents`_

For detailed documentaton head over to chamber.readthedocs.io_.

Dependencies
------------

Back to `Table of Contents`_

  * codecov (for code coverage reporting)
  * CoolProp.HumidAirProp.HAPropsSI (for humid air calculations)
  * matplotlib.pyplot
  * matplotlib.legend_handler.HandlerLine2D
  * mysql_connector (for access to MySQL databases)
  * nptdms (for interacting with LabVIEW TDMS files)
  * pandas (for loading data into DataFrames)
  * pytest (for testing)
  * pytest-cov (for code coverage information)
  * pytz (for datetime testing)
  * scipy (for calculations and statistics)
  * schedule (for autonomous execution)
  * seaborn (for plot styling)
  * tabulate.tabulate (for table formatting)
  * tqdm (for progress bars)

Setting up Initial State of MySQL Database
------------------------------------------

Back to `Table of Contents`_

Setting up the initial state of the MySQL Server is handled by the
setup_sqldb.py file.
Simply run the following command from the root directory; e.g., ucsd_ch:
.. code-block:: bash

  $ python setup/setup_sqldb.py <database_name>


Where <database_name> is replaced with the name of the MySQL database schema.
This will create all tables and populate the Unit table and add pool 1
(default pool used in experiments).

The database schema is described below:

.. image:: images/mysql_schema.png


NOTE: In order to run the integration tests, a local version of mySQL must be
installed and running.

On OSX you can run the following line to start the mySQL service after
installing from LINK

.. code-block:: bash

    $ sudo launchctl load -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist

Stopping the mySQL service:

.. code-block:: bash

    $ sudo launchctl unload -F /Library/LaunchDaemons/com.oracle.oss.mysql.mysqld.plist


Preferred Way to Run Tests
---------------------------

Back to `Table of Contents`_

1. From the repo directory; i.e., chamber
.. code-block:: bash

    $ python -m pytest tests -xv  --cov=chamber --cov-report html tests

The above line requires both `pytest` and `pytest-cov` are installed.


Preferred Way to Run Scripts
----------------------------

Back to `Table of Contents`_

1. From the repo directory; i.e., chamber
.. code-block:: bash

    $ python -m chamber.scripts.<yout-script-name>

It should also be noted that the `.py` is not required at the end of this line.


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
    :target: https://chamber.readthedocs.io/en/latest/?badge=latest

.. |build| image:: https://travis-ci.com/rinman24/inman_phd.svg?branch=master
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.com/rinman24/chamber

.. |codecov| image:: https://codecov.io/gh/rinman24/chamber/branch/master/graph/badge.svg
    :alt: Code Coverage Badge
    :scale: 100%
    :target: https://codecov.io/gh/rinman24/chamber

.. |license| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :alt: License Badge
    :scale: 100%
    :target: https://opensource.org/licenses/MIT

.. _chamber.readthedocs.io: http://chamber.readthedocs.io
