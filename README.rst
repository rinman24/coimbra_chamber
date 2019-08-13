UCSD Coimbra Chamber
====================

|build| |codecov| |license|

.. image:: images/coimbra_ucsd_logo.png

Table of Contents
-----------------

  * `Description`_
  * `Python Version`_
  * `MySQL Database`_
  * `Preferred Way to Run Tests`_
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

1. From the repo directory; i.e., chamber
.. code-block:: bash

    $ python -m pytest tests -xv  --cov=chamber --cov-report html tests

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
