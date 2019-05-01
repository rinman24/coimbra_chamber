"""Module holds base classes and helper functions for integration testing."""

from pathlib import Path

import pyodbc

import chamber.ifx.configuration as config


class SQLTestHelper(object):
    """Class for handling setup and teardown of mySQL testing resources."""

    def __init__(self):
        """Set up mySQL for tests."""
        self.db_name = config.get_value('test_database')
        self._create_db()

    def _create_db(self):
        """Create the target db and then sets up the schema."""
        self.conn = self._create_connection('test')
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(dbid) as count FROM  sys.sysdatabases WHERE name='{self.db_name}';")
        row = cursor.fetchone()
        if row:
            if not row.count:
                cursor.execute(f'CREATE DATABASE {self.db_name};')

        self.conn = self._create_connection(self.db_name)
        self.run_script('clearschema.sql')
        self.run_script('createdb.sql')

    def clear_db(self):
        """Clean up sql from tests."""
        self.run_script('clearschema.sql')
        self.run_script('createdb.sql')
        self.conn.close()

    def run_script(self, script_file_name):
        """Run a sql script against the managed test database."""
        cursor = self.conn.cursor()

        path = Path(f'chamber/tests/resources/{script_file_name}')
        with open(path) as inserts:
            sql_script = inserts.readlines()
            sql = (' '.join(sql_script))
            sql = sql.replace('\n', ' ')
            if ' GO ' in sql:
                sql_script = sql.split(' GO ')
            for part in sql_script:
                try:
                    part = part.strip()
                    if part:
                        cursor.execute(part)
                except Exception as e:
                    print(e)

    def _create_connection(self, database=None):
        """Create a mySQL connection from configuration settings."""
        server = config.get_value('test')
        if not database:
            database = config.get_value('CHAMBER_DB_DATABASE')
        conn_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};'

        conn = pyodbc.connect(conn_string)
        conn.autocommit = True
        return conn
