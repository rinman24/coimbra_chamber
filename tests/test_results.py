"""Docstring."""
import mysql.connector as conn
from mysql.connector import errorcode
import pytest

import chamber.const as const
import chamber.results as results
import tests.test_const as test_const

@pytest.fixture(scope='module')
def cursor_ch():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL chamber...")
    cnx = results.connect_sqldb_chamber()
    cur = cnx.cursor()
    print("Connected.")
    yield cur
    print("\nCleaning up test database...")
    print("Disconnecting from MySQL chamber...")
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
    print("\nCleaning up test database...")
    drop_tables(cur, False)
    print("Disconnecting from MySQL results...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL results closed.")


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


def drop_tables(cur, bol):
    """Prompts user to drop database tables or not. 'y' to drop, 'n' to not drop"""
    if bol:
        print("Dropping tables...")
        cur.execute("DROP TABLE IF EXISTS " + ", ".join(const.VIEW_NAME_LIST) + ";")
        return
    else:
        print("Tables not dropped.")
        return
