"""Docstring."""
from datetime import datetime
from decimal import Decimal
from os import path
from pathlib import Path
from shutil import move

import mysql.connector as conn
from mysql.connector import errorcode
from nptdms import TdmsFile
import pytest

import chamber.sqldb as sqldb
import chamber.const as const

@pytest.fixture(scope='module')
def cursor():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL...")
    cnx = sqldb.connect_sqldb()
    cur = cnx.cursor()
    print("Connected.")
    yield cur
    print("\nCleaning up test database...")
    drop_tables(cur)
    print("Disconnecting from MySQL...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL closed.")

@pytest.fixture(scope='module')
def test_tdms_obj():
    """fixture to instantiate only one TdmsnFile object for testing"""
    return TdmsFile(const.TDMS_TEST_FILES[0])


class TestSqlDb(object):
    """Unit testing of sqldb.py."""

    def test_connect_sqldb(self, cursor):
        """Test connection to the MySQL database."""
        assert cursor

    def test_create_tables(self, cursor):
        """"Test DDL for table creation."""
        sqldb.create_tables(cursor, const.TABLES)
        cursor.execute("SELECT 1 FROM UnitTest LIMIT 1;")
        assert not cursor.fetchall()

    def test_setting_exists(self, cursor):
        """Test that you can find settings that already exist."""
        cursor.execute(const.ADD_SETTING, const.SETTINGS_TEST_1)
        assert sqldb.setting_exists(cursor, const.SETTINGS_TEST_1)
        assert not sqldb.setting_exists(cursor, const.SETTINGS_TEST_2)

    def test_list_tdms(self):
        """Test correct output of all .tdms files contained in argument file."""
        files = sqldb.list_tdms(const.LIST_TDMS_TEST_DIR)
        for tdms_file in const.INCORRECT_FILE_LIST:
            assert tdms_file not in files
        for tdms_file in const.CORRECT_FILE_LIST:
            assert tdms_file in files

    def test_move_files(self):
        """Test that files are removed from the input directory and into user."""
        try:
            assert path.exists(const.CORRECT_FILE_LIST[1])
            sqldb.move_files(path.split(const.CORRECT_FILE_LIST[1])[0])
            assert not path.exists(const.CORRECT_FILE_LIST[1])
            new_path = path.join(path.join(str(Path.home()),"read_files"),
                                 path.relpath(const.CORRECT_FILE_LIST[1])[3:])
            assert path.exists(new_path)
            move(new_path,
                        path.split(const.CORRECT_FILE_LIST[1])[0])
        except FileNotFoundError:
            assert False

    def test_get_setting_info(self, test_tdms_obj):
        """Test correct dictionary output when reading .tdms files for settings"""
        assert const.TDMS_01_SETTING == sqldb.get_setting_info(test_tdms_obj)

    def test_get_test_info(self, test_tdms_obj):
        """Test correct dictionary output when reading .tdms files for tests"""
        assert const.TDMS_01_DICT_TESTS == sqldb.get_test_info(test_tdms_obj)

    def test_get_obs_info(self, test_tdms_obj):
        """Test correct output when converting tdms obj observation data to dictionary of strings"""
        assert const.TDMS_01_OBS_08 == sqldb.get_obs_info(test_tdms_obj, const.TEST_INDEX)

    def test_get_temp(self, test_tdms_obj):
        """Test correct output when converting tdms obj temperature data to dictionary of strings"""
        assert const.TDMS_01_THM_07 == sqldb.get_temp(test_tdms_obj, const.TEST_INDEX,
                                                      const.TC_INDEX)

    def test_add_tube_info(self, cursor):
        """Tsts correct data insertion into Tube table as well as correct handling of dulicate tubes"""
        sqldb.add_tube_info(cursor)
        cursor.execute("SELECT TubeID FROM Tube;")
        assert cursor.fetchone()[0] == 1
        cursor.execute("SELECT TubeID FROM Tube;")
        assert len(cursor.fetchall()) == 1

    def test_add_setting_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_setting."""
        clear_sqldb(cursor)
        sqldb.add_setting_info(cursor, test_tdms_obj)
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(test_tdms_obj))
        assert isinstance(setting_id, int)
        assert sqldb.add_setting_info(cursor, test_tdms_obj) == setting_id
        clear_sqldb(cursor)

    def test_add_test_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_test."""
        clear_sqldb(cursor)
        setting_id = sqldb.add_setting_info(cursor, test_tdms_obj)
        sqldb.add_test_info(cursor, test_tdms_obj, setting_id)
        cursor.execute("SELECT Author FROM Test WHERE TestID = {}".format(cursor.lastrowid))
        assert cursor.fetchone()[0] == "ADL"
        clear_sqldb(cursor)

    def test_test_exists(self, cursor, test_tdms_obj):
        """Test that you can find tests that already exist."""
        clear_sqldb(cursor)
        setting_id = sqldb.add_setting_info(cursor, test_tdms_obj)
        sqldb.add_test_info(cursor, test_tdms_obj, setting_id)
        test_id = cursor.lastrowid
        assert test_id == sqldb.test_exists(cursor, sqldb.get_test_info(test_tdms_obj))
        clear_sqldb(cursor)
        assert not test_id == sqldb.test_exists(cursor, sqldb.get_test_info(test_tdms_obj))

    def test_add_obs_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_obs."""
        clear_sqldb(cursor)
        test_id = sqldb.add_test_info(cursor, test_tdms_obj,
                                      sqldb.add_setting_info(cursor, test_tdms_obj))
        for obs_idx in range(len(test_tdms_obj.object("Data", "Idx").data)):
            sqldb.add_obs_info(cursor, test_tdms_obj, test_id, obs_idx)
        cursor.execute('SELECT Duty FROM Observation '
                       'WHERE ObservationID = {}'.format(cursor.lastrowid))
        assert cursor.fetchone()[0] == Decimal('0.0')
        clear_sqldb(cursor)

    def test_add_input(self, cursor):
        """Test correct data insertion through checking add_temp, the final table in cascade."""
        clear_sqldb(cursor)
        sqldb.add_input(cursor, const.TEST_DIRECTORY)
        cursor.execute("SELECT Temperature FROM TempObservation WHERE TempObservationID = "
                       + "'{}'".format(cursor.lastrowid))
        result = cursor.fetchone()[0]
        assert result == Decimal('297.33') or result == Decimal('297.36')


def clear_sqldb(cursor):
    """Clears test database."""
    cursor.execute('DELETE FROM TempObservation;')
    cursor.execute('DELETE FROM Observation;')
    cursor.execute('DELETE FROM Test;') 
    cursor.execute('DELETE FROM Setting;')

def drop_tables(cur):
    """Prompts user to drop database tables or not. 'y' to drop, 'n' to not drop"""
    user_input = input('\nDROP TABLES (y/n)?\n')
    if user_input:
        if user_input.lower() == 'y':
            print("Dropping tables...")
            cur.execute("DROP TABLE IF EXISTS " + ", ".join(const.TABLE_NAME_LIST) + ";")
            return
        if user_input.lower() == 'n':
            print("Tables not dropped.")
            return
    drop_tables(cur)
