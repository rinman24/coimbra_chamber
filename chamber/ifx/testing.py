"""Module holds base classes and helper functions for integration testing."""

from pathlib import Path

import mysql.connector
import pyodbc

import chamber.ifx.configuration as config


class SQLTestHelper(object):
    """Class for handling setup and teardown of mySQL testing resources."""

    def __init__(self):
        """Set up mySQL for tests."""
        self.database = config.get_value('database', 'MySQL-Server')

        # self._create_db()

    def _create_db(self):
        """Create the target db and then sets up the schema."""
        self.cnx = self._create_connection('sys')
        cursor = self.cnx.cursor()
        # Check if the database exists; if not, create it.
        dml = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{self.database}';"
        cursor.execute(dml)
        row = cursor.fetchone()
        if not row:
            ddl = f'CREATE DATABASE {self.database} DEFAULT character SET latin1;'
            cursor.execute(ddl)
        # Now run the scripts
        self.cnx = self._create_connection(self.database)
        self.run_script('clearschema.sql')
        self.run_script('createdb.sql')

    def clear_db(self):
        """Clean up sql from tests."""
        self.run_script('clearschema.sql')
        self.cnx.close()

    def run_script(self, script_file_name):
        """Run a sql script against the managed test database."""
        cursor = self.cnx.cursor()

        path = Path(f'chamber/tests/resources/{script_file_name}')
        with open(path) as inserts:
            sql_script = inserts.readlines()
            for part in sql_script:
                try:
                    part = part.strip()
                    if part:
                        cursor.execute(part)
                except Exception as e:
                    print(e)

    def _create_connection(self, database):
        """Create a MySQL connection from configuration settings."""
        host = config.get_value('host', 'MySQL-Server')
        user = config.get_value('user', 'MySQL-Server')
        password = config.get_value('password', 'MySQL-Server')

        kwargs = dict(host=host, user=user, password=password, database=database)
        cnx = mysql.connector.connect(**kwargs)
        cnx.autocommit = True

        return cnx
