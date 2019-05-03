"""Module holds base classes and helper functions for integration testing."""

from pathlib import Path

import mysql.connector
from mysql.connector import errorcode

import chamber.ifx.configuration as config


class SQLTestHelper(object):
    """Class for handling setup and teardown of mySQL testing resources."""

    def __init__(self):
        """Set up mySQL for tests."""
        self._database = config.get_value('database', 'MySQL-Server')

        self._create_db()

    # ------------------------------------------------------------------------
    # 'Public' methods: included in the API

    def run_script(self, script_file_name):
        """
        Run a sql script against the managed test database.

        The script file must be located in the relative path
        `chamber/tests/resources` and should include MySQL statements.

        Parameters
        ----------
        script_file_name : str or pathlib.Path
            Name of the sql script to run, which should have a .sql extension.

        Notes
        -----
        Comments are allowed in the script if they begin with '--'. MySQL
        queries are allowed to span multiple lines in the script as long as
        they terminate with a semicolon.

        Examples
        --------
        >>> from chamber.ifx.testing import SQLTestHelper
        >>> helper = SQLTestHelper()
        >>> helper.run_script('createdb.sql')

        """
        cursor = self.cnx.cursor()

        path = Path(f'chamber/tests/resources/{script_file_name}')

        statement = ''

        with open(path) as inserts:
            sql_script = inserts.readlines()
            for part in sql_script:
                part = part.replace('\n', '')
                if part.startswith('--'):  # ignore sql comment lies
                    continue
                else:
                    statement = statement + part
                    if statement.endswith(';'):  # try to execute
                        try:
                            cursor.execute(statement)
                        except mysql.connector.Error as err:
                            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                                print(f'Something is wrong with your user name or password: {err}')
                            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                                print(f'Database does not exist: {err}')
                            else:
                                print(err)
                        else:
                            statement = ''

    def clear_db(self):
        """Clean up sql from tests."""
        # TODO: Docsring
        cursor = self.cnx.cursor()

        cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
        cursor.execute(f'DROP DATABASE IF EXISTS `{self._database}`;')
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')

        self.cnx.close()

    # ------------------------------------------------------------------------
    # 'Internal' methods: not part of the API

    def _create_db(self):
        """Create the target db and then sets up the schema."""
        cnx = self._create_connection('sys')
        cursor = cnx.cursor()
        database = self._database
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS `{database}` DEFAULT CHARACTER SET utf8 ;')
        cnx.close()

        self.cnx = self._create_connection()
        self.run_script('createdb.sql')

    def _create_connection(self, database=None):
        """Create a MySQL connection from configuration settings."""
        host = config.get_value('host', 'MySQL-Server')
        user = config.get_value('user', 'MySQL-Server')
        password = config.get_value('password', 'MySQL-Server')
        if not database:
            database = self._database

        kwargs = dict(host=host, user=user, password=password, database=database)
        cnx = mysql.connector.connect(**kwargs)

        cnx.autocommit = True

        return cnx
