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
  * `Preferred Way to Run Tests`_
  * `Preferred Way to Run Scripts`_
  * `Images`_

Description
-----------

Back to `Table of Contents`_

Description will go here.

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

  * CoolProp.HumidAirProp.HAPropsSI (for humid air calculations)
  * matplotlib.pyplot
  * matplotlib.legend_handler.HandlerLine2D
  * mysql.connector (for access to MySQL databases)
  * nptdms (for interacting with LabVIEW TDMS files)
  * pandas (for loading data into DataFrames)
  * pytest (for testing)
  * pytz (for datetime testing)
  * schedule (for autonomous execution)
  * tabulate.tabulate (for table formatting)

Setting up Initial State of MySQL Database
------------------------------------------

Back to `Table of Contents`_

Setting up the initial state of the MySQL Server is handled by the
setup_sqldb.py file. However, before running this script, you must make some
changes to the `config_example.ini` file:

#. Change this filename to from `config_example.ini` to `config.ini`.
#. Populate `config.ini` with information relevant to your application; i.e.,
   insert your own username, password, and host for the MySQL Server.



Once you have made this changes, simply run the following command from the root
directory; e.g., ucsd_ch:
.. code-block:: console
 
    python setup/setup_sqldb.py <database_name>


Where `<database_name>` is replaced with the name of the MySQL database schema.
This will create all tables and populate the Unit table and add Tube 1
(default tube used in experiments).

The database schema is described below:

.. image:: images/mysql_schema.png


Preferred Way to Run Tests
---------------------------

Back to `Table of Contents`_

1. From the repo directory; i.e., chamber:
.. code-block:: console
 
    python -m pytest tests/<your-test-name>.py -v --capture=no


It should also be noted that the test_const.py file in the test directory
does not acctually contain tests, but rather the constants that are
needed for testing.


Preferred Way to Run Scripts
---------------------------

Back to `Table of Contents`_

1. From the repo directory; i.e., chamber:
.. code-block:: console

    python -m chamber.scripts.<yout-script-name>


It should also be noted that the `.py` is not required at the end of this line.


Images
------

Back to `Table of Contents`_

.. image:: images/chamber_optics.jpg

.. image:: images/chamber_iso_view.jpg

.. image:: images/chamber_scale.jpg

.. image:: images/chamber_profile.jpg


.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://docs.readthedocs.io/en/latest/?badge=latest

.. _chamber.readthedocs.io: http://chamber.readthedocs.io
