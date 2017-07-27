"""Docstring."""

import pytest
import mysql.connector as conn
from mysql.connector import errorcode
import chamber.sqldb as sqldb

TABLES = {}
TABLES['UnitTest'] = (
    "CREATE TABLE `UnitTest` ("
    "    `UnitTestID` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
    "    `Value` DECIMAL(5,2) NOT NULL,"
    "    `String` VARCHAR(30) NOT NULL,"
    "  PRIMARY KEY (`UnitTestID`)"
    ");")

ADD_ROW = ("INSERT INTO UnitTest (Value, String) VALUES (%s, %s);")
ROW_DATA = ('99.9', 'Test String')

@pytest.fixture(scope='module')
def cursor():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL...")
    cnx = sqldb.connect_sqldb()
    cur = cnx.cursor()
    print("Connected.")
    yield cur
    print("\nCleaning up test database...")
    cur.execute("DROP TABLE UnitTest;")
    print("Disconnecting from MySQL...")
    cur.close()
    cnx.close()
    print("Connection to MySQL closed.")

class TestSqlDb(object):
    """Unit testing of sqldb.py."""

    def test_connection(self, cursor):
        """Test connection to the MySQL database."""
        assert cursor

    def test_create_table(self, cursor):
        """"Test DDL for table creation."""
        sqldb.create_tables(cursor, TABLES)
        cursor.execute("SELECT 1 FROM UnitTest LIMIT 1;")
        assert len(cursor.fetchall()) == 0

    def test_enter_into_table(self, cursor):
        """Test DDL for row insertion."""
        sqldb.table_insert(cursor, ADD_ROW, ROW_DATA)
        cursor.execute("SELECT Value FROM UnitTest WHERE String = 'Test String';")
        assert float(cursor.fetchall()[0][0]) == 99.9


