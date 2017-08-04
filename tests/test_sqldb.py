"""Docstring."""
from math import isclose
import mysql.connector as conn
from mysql.connector import errorcode
import pytest

import chamber.sqldb as sqldb

TABLES = []
TABLES.append(('UnitTest',
               "CREATE TABLE UnitTest ("
               "    UnitTestID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
               "    Number DECIMAL(5,2) NULL,"
               "    String VARCHAR(30) NULL,"
               "  PRIMARY KEY (`UnitTestID`)"
               ");"))

ROW_DATA_1 = {'String': 'unit testing'}
ROW_DATA_2 = {'Number': '99.9', 'String': 'more testing'}

SETTINGS_1 = {'InitialDewPoint': '100', 'InitialDuty': '100', 'InitialMass': '0.07',
              'InitialPressure': '100000', 'InitialTemp': '290', 'TimeStep': '1'}
SETTINGS_2 = {'InitialDewPoint': '500', 'InitialDuty': '1000', 'InitialMass': '20',
              'InitialPressure': '8', 'InitialTemp': '400', 'TimeStep': '20'}

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
    cnx.commit()
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

    def test_build_insert_dml(self):
        """Test DML for INSERT statements."""
        query = sqldb.insert_dml('UnitTest', ROW_DATA_1)
        ref = "INSERT INTO UnitTest     (String)  VALUES    ('unit testing');"
        assert ref == query

    def test_last_insert_id(self, cursor):
        """Test retrevial of last insert id."""
        assert isinstance(sqldb.last_insert_id(cursor), int)

    def test_enter_into_table(self, cursor):
        """Test DDL for row insertion."""
        cursor.execute(sqldb.insert_dml('UnitTest', ROW_DATA_2))
        cursor.execute("SELECT Number FROM UnitTest WHERE String = 'more testing';")
        assert isclose(float(cursor.fetchall()[0][0]), 99.9)

    def test_setting_exists(self, cursor):
        """Test that you can find settings that already exist."""
        cursor.execute(sqldb.insert_dml('Setting', SETTINGS_1))
        assert sqldb.setting_exists(cursor, SETTINGS_1)
        assert not sqldb.setting_exists(cursor, SETTINGS_2)
        setting_id = sqldb.last_insert_id(cursor)
        cursor.execute("DELETE FROM Setting WHERE SettingID = {};".format(setting_id))
