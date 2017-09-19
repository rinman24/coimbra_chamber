"""Docstring."""
import mysql.connector as conn
from mysql.connector import errorcode
from os import getcwd
import pytest

import chamber.const as const
import chamber.results as results
import chamber.sqldb as sqldb
import tests.test_const as test_const

@pytest.fixture(scope='module')
def cursor_ch():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL chamber...")
    cnx = results.connect_sqldb_chamber()
    cur = cnx.cursor()
    print("Connected.")
    yield cur
    print("\nCleaning up test_chamber database...")
    print("Disconnecting from MySQL test_chamber...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL chamber closed.")

@pytest.fixture(scope='module')
def cursor_re():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL results...")
    cnx = results.connect_sqldb_results()
    cur = cnx.cursor()
    print("Connected.")
    yield cur
    print("\nCleaning up test_results database...")
    drop_views(cur, False)
    print("Disconnecting from MySQL test_results...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL results closed.")

@pytest.fixture(scope='module')
def cursor_test():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL...")
    cnx = sqldb.connect_sqldb("test")
    cur = cnx.cursor()
    print("Connected.")
    sqldb.create_tables(cur, const.TABLES)
    sqldb.add_tube_info(cur)
    sqldb.add_input(cur, getcwd() + "/tests/data_transfer_test_files", True)
    yield cur
    print("\nCleaning up test database...")
    drop_tables(cur, True)
    print("Disconnecting from MySQL...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL closed.")

class TestSqlDb(object):
    """Unit testing of sqldb.py."""

    def test_connect_sqldb_chamber(self, cursor_ch):
        """Test connection to the MySQL chamber database."""
        assert cursor_ch

    def test_connect_sqldb_results(self, cursor_re):
        """Test connection to the MySQL results database."""
        assert cursor_re

    def test_create_views(self, cursor_re):
        """"Test DDL for table creation."""
        results.create_views(cursor_re, const.VIEWS)
        cursor_re.execute("SELECT 1 FROM UnitTest LIMIT 1;")
        assert not cursor_re.fetchall()

    def test_normalized_mass(self, cursor_ch, cursor_re):
        """Tests insertion and proper calculation of Normalized Mass"""
        results.normalized_mass(cursor_ch, cursor_re, 33)
        cursor_re.execute("SELECT NormalizedMass FROM NormalizedMass LIMIT 1;")
        assert cursor_re.fetchall()[0][0] == 1

    def test_get_mass(self, cursor_test):
        """Test ability to get the list of mass observations of a specific Test"""
        mass = results.get_mass(cursor_test, 2)
        assert mass[0] == 0.087427
        assert mass[-1] == 0.087427
        assert len(mass) == 14

    def test_get_pressure(self, cursor_test):
        """Test ability to get the list of pressure observations of a specific Test"""
        pressure = results.get_pressure(cursor_test, 2)
        assert pressure[0] == 99662
        assert pressure[-1] ==99649
        assert len(pressure) == 14

    def test_get_dew_point(self, cursor_test):
        """Test ability to get the list of dewpoint observations of a specific Test"""
        dew_point = results.get_dew_point(cursor_test, 2)
        print(dew_point[0], dew_point[-1], len(dew_point))
        assert dew_point[0] == 289.73
        assert dew_point[-1] == 289.72
        assert len(dew_point) == 14


def drop_views(cur, bol):
    """Drops tables in test_results database if bol=True"""
    if bol:
        print("Dropping tables...")
        cur.execute("DROP TABLE IF EXISTS " + ", ".join(const.VIEW_NAME_LIST) + ";")
    else:
        print("Tables not dropped.")

def drop_tables(cur, bol):
    """Drops tables in test database if bol=True"""
    if bol:
        print("Dropping tables...")
        cur.execute("DROP TABLE IF EXISTS " + ", ".join(const.TABLE_NAME_LIST) + ";")
    else:
        print("Tables not dropped.")
