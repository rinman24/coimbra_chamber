Coimbra Chamber
===============

|build| |codecov| |license|

.. image:: images/coimbra_ucsd_logo.png

Table of Contents
-----------------

  * `Description`_
  * `Installation`_
  * `Getting Started`_
  * `Python Version`_
  * `MySQL Database`_
  * `Preferred Way to Run Tests`_
  * `Images`_

Description
-----------

Back to `Table of Contents`_

Description will go here.

Installation
------------

Run the following to install:

.. code-block:: bash

    $ pip install coimbra_chamber

Getting Started
---------------

Back to `Table of Contents`_

We must configure our database before running any analysis:

First, we must decide if we want to use an in-memory SQLite database or point to an instance of a MySQL database.
Then we need to create a config file in our working directory to reflect our configuration.

Create a copy of the file `example-config.ini` from the repository and rename it to `config.ini`.
Move the `config.ini` file that we just created into your working directory and open the file.
Change database_type to `memory` if we chose an in-memory database above.
Otherwise, leave the database_type as `MySQL` and replace the `host`, `user`, and `password` fields with the host, username, and password for MySQL database we choose.

Then, to run an analysis:

.. code-block:: python

    >>> import coimbra_chamber as cc
    >>> manager = cc.DataManager()
    >>> manager.run()

Follow the prompts in the terminal to complete your analysis.

Python Version
--------------

Back to `Table of Contents`_

This module is intended to use Python 3.6. and above.


MySQL Database
------------------------------------------

Back to `Table of Contents`_

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

1. From the repo directory; i.e., coimbra_chamber
.. code-block:: bash

    $ python -m pytest tests -xv  --cov=coimbra_chamber --cov-report html tests

The above line requires both `pytest` and `pytest-cov` are installed.


Images
------

Back to `Table of Contents`_

.. image:: images/chamber_iso_view.jpg

.. image:: images/chamber_scale.jpg

.. image:: images/chamber_profile.jpg

.. image:: images/chamber_optics.jpg


.. |build| image:: https://travis-ci.com/rinman24/coimbra_chamber.svg?branch=master
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.com/rinman24/coimbra_chamber

.. |codecov| image:: https://codecov.io/gh/rinman24/coimbra_chamber/branch/master/graph/badge.svg
    :alt: Code Coverage Badge
    :scale: 100%
    :target: https://codecov.io/gh/rinman24/coimbra_chamber

.. |license| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :alt: License Badge
    :scale: 100%
    :target: https://opensource.org/licenses/MIT
