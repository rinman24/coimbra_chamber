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

import chamber.const as const
import chamber.sqldb as sqldb
import tests.test_const as test_const


@pytest.fixture(scope='module')
def cursor():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL...")
    cnx = sqldb.connect_sqldb("test")
    cur = cnx.cursor()
    print("Connected.")
    yield cur
    print("\nCleaning up test database...")
    drop_tables(cur, True)
    print("Disconnecting from MySQL...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL closed.")


@pytest.fixture(scope='module')
def test_tdms_obj():
    """fixture to instantiate only one TdmsnFile object for testing"""
    return TdmsFile(test_const.TDMS_TEST_FILE_MF), TdmsFile(test_const.TDMS_TEST_FILE_MT)


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
        cursor.execute(const.ADD_SETTING_M_T, test_const.SETTINGS_TEST_1)
        cursor.execute(const.ADD_SETTING_M_F, test_const.SETTINGS_TEST_3)
        assert sqldb.setting_exists(cursor, test_const.SETTINGS_TEST_1)
        assert not sqldb.setting_exists(cursor, test_const.SETTINGS_TEST_2)
        assert sqldb.setting_exists(cursor, test_const.SETTINGS_TEST_3)

    def test_list_tdms(self):
        """Test correct output of all .tdms files contained in argument."""
        files = sqldb.list_tdms(test_const.TEST_DIRECTORY)
        for tdms_file in test_const.INCORRECT_FILE_LIST:
            assert tdms_file not in files
        for tdms_file in test_const.CORRECT_FILE_LIST:
            assert tdms_file in files

    def test_move_files(self):
        """Test that files are removed from the directory and into user."""
        try:
            assert path.exists(test_const.CORRECT_FILE_LIST[3])
            sqldb.move_files(path.split(test_const.CORRECT_FILE_LIST[3])[0])
            assert not path.exists(test_const.CORRECT_FILE_LIST[3])
            new_path = path.join(path.join(str(Path.home()), "read_files"),
                                 path.relpath(test_const.CORRECT_FILE_LIST[3])[3:])
            assert path.exists(new_path)
            move(new_path, path.split(test_const.CORRECT_FILE_LIST[3])[0])
        except FileNotFoundError:
            assert False

    def test_get_setting_info(self, test_tdms_obj):
        """Test output when reading .tdms files for settings"""
        assert test_const.TDMS_TEST_FILE_MT_SETTING == sqldb.get_setting_info(test_tdms_obj[1])
        assert test_const.TDMS_TEST_FILE_MF_SETTING == sqldb.get_setting_info(test_tdms_obj[0])

    def test_get_test_info(self, test_tdms_obj):
        """Test dictionary output when reading .tdms files for tests"""
        assert test_const.TDMS_TEST_FILE_MT_TESTS == sqldb.get_test_info(test_tdms_obj[1])
        assert test_const.TDMS_TEST_FILE_MF_TESTS == sqldb.get_test_info(test_tdms_obj[0])

    def test_get_obs_info(self, test_tdms_obj):
        """Test output when converting Observation data to a dict of strs"""
        assert test_const.TDMS_TEST_FILE_MT_OBS_09 == sqldb.get_obs_info(test_tdms_obj[1],
                                                                         test_const.TEST_INDEX,
                                                                         True)
        assert test_const.TDMS_TEST_FILE_MF_OBS_09 == sqldb.get_obs_info(test_tdms_obj[0],
                                                                         test_const.TEST_INDEX,
                                                                         False)

    def test_get_temp_info(self, test_tdms_obj):
        """Test output when converting temperature data to a dict of strings"""
        assert test_const.TDMS_TEST_FILE_MT_THM_07 == sqldb.get_temp_info(test_tdms_obj[1],
                                                                          test_const.TEST_INDEX,
                                                                          test_const.TC_INDEX)
        assert test_const.TDMS_TEST_FILE_MF_THM_07 == sqldb.get_temp_info(test_tdms_obj[0],
                                                                          test_const.TEST_INDEX,
                                                                          test_const.TC_INDEX)

    def test_add_tube_info(self, cursor):
        """Tsts data insertion into Tube and handling of dulicate tubes"""
        sqldb.add_tube_info(cursor)
        cursor.execute("SELECT TubeID FROM Tube;")
        assert cursor.fetchone()[0] == 1
        cursor.execute("SELECT TubeID FROM Tube;")
        assert len(cursor.fetchall()) == 1

    def test_add_setting_info(self, cursor, test_tdms_obj):
        """Test data insertion and condition handling in add_setting."""
        sqldb.add_setting_info(cursor, test_tdms_obj[0])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(test_tdms_obj[0]))
        assert isinstance(setting_id, tuple)
        assert setting_id[1] == 0

        sqldb.add_setting_info(cursor, test_tdms_obj[1])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(test_tdms_obj[1]))
        assert isinstance(setting_id, tuple)
        assert setting_id[1] == 1

    def test_add_test_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_test."""
        setting_id = sqldb.add_setting_info(cursor, test_tdms_obj[0])
        sqldb.add_test_info(cursor, test_tdms_obj[0], setting_id)
        cursor.execute("SELECT Author FROM Test WHERE TestID = {}".format(cursor.lastrowid))
        assert cursor.fetchone()[0] == "ADL"

    def test_test_exists(self, cursor, test_tdms_obj):
        """Test that you can find tests that already exist."""
        setting_id = sqldb.add_setting_info(cursor, test_tdms_obj[0])
        sqldb.add_test_info(cursor, test_tdms_obj[0], setting_id)
        test_id = cursor.lastrowid
        assert test_id == sqldb.test_exists(cursor, sqldb.get_test_info(test_tdms_obj[0]))
        assert not test_id == sqldb.test_exists(cursor, sqldb.get_test_info(test_tdms_obj[1]))

    def test_add_obs_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_obs."""
        test_id = sqldb.add_test_info(cursor, test_tdms_obj[0],
                                      sqldb.add_setting_info(cursor, test_tdms_obj[0]))
        for obs_idx in range(len(test_tdms_obj[0].object("Data", "Idx").data)):
            sqldb.add_obs_info(cursor, test_tdms_obj[0], (test_id, 0), obs_idx)
        cursor.execute('SELECT Duty FROM Observation '
                       'WHERE ObservationID = {}'.format(cursor.lastrowid))
        assert cursor.fetchone()[0] == Decimal('0.0')

        test_id = sqldb.add_test_info(cursor, test_tdms_obj[1],
                                      sqldb.add_setting_info(cursor, test_tdms_obj[1]))
        for obs_idx in range(len(test_tdms_obj[1].object("Data", "Idx").data)):
            sqldb.add_obs_info(cursor, test_tdms_obj[1], test_id, obs_idx)
        cursor.execute('SELECT Duty FROM Observation '
                       'WHERE ObservationID = {}'.format(cursor.lastrowid))
        assert cursor.fetchone()[0] == Decimal('0.0')

    def test_add_input(self, cursor):
        """Test overall data insertion, the final table in cascade."""
        sqldb.add_input(cursor, test_const.TEST_DIRECTORY, True)
        cursor.execute("SELECT Temperature FROM TempObservation WHERE"
                       "TempObservationID = '{}'".format(cursor.lastrowid))
        result = cursor.fetchone()[0]
        assert result == Decimal('297.17')


def drop_tables(cur, bol):
    """Drops databese tables if bol is true, does not drop if false"""
    if bol:
        print("Dropping tables...")
        cur.execute("DROP TABLE IF EXISTS " +
                    ", ".join(const.TABLE_NAME_LIST) + ";")
    else:
        print("Tables not dropped.")
