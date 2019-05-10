Getting Started
===============

MySQL Dependancy
----------------
It is important to note that many of the sub-packages and modules in the
`chamber` package interact with a MySQL database. The remainder of the
documentation assumes basic familiarity with MySQL dabase installation
and administration.

That being said, the user is only required set up the database and create
a schema. The rest of the interaction with the database is handled
programatically. For example, running the following line from the ternimal
(or command prompt in Windows) from the root of the repository will create
all the tables and set up the inital state of the database with units and
a default pool:

.. code-block:: shell

   $ python -m chamber.scripts.setup_sqldb <your-schema-here>


However, before a connection can be made to the database, we must edit the
configuration file which is explained in the following section.


Configuration file
------------------

A configuration file is used to store credentials for the MySQL database. An
example configuraton file named 'example_config.ini' is included in the
repository. In order for the `chamber` package to function properly a few
modifications to the `example_config.ini` file.

1. Rename `example_config.ini` to `config.ini`. This is required to prevent
   the remote repository from tracking sensitive credentials.
2. Open the newly renamed `config.ini` file and enter your specific `host`,
   `user`, and `password` for your instance of the MySQL database.

Once this is done, you configuration file shoule be ready to go!

Python Dependancies
-------------------
Several dependancies are covered in the README file, please refer to the
README file for more information on installing dependencies. Authors recommend
using the anaconda package manager, which is the method covered in the README.
Howver, the user is free to use whatever package manager they prefer or are
most comportable with.
