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
    return (TdmsFile(test_const.CORRECT_FILE_LIST[0]), # IsMass 0 IsSteady 0
            TdmsFile(test_const.CORRECT_FILE_LIST[1]), # IsMass 0 IsSteady 1
            TdmsFile(test_const.CORRECT_FILE_LIST[2]), # IsMass 1 IsSteady 0
            TdmsFile(test_const.CORRECT_FILE_LIST[3])) # IsMass 1 IsSteady 1


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
        cursor.execute(const.ADD_SETTING, test_const.SETTINGS_TEST_1)
        assert sqldb.setting_exists(cursor, test_const.SETTINGS_TEST_1)
        assert not sqldb.setting_exists(cursor, test_const.SETTINGS_TEST_2)
        truncate(cursor, 'Setting')

    def test_list_tdms(self):
        """Test correct output of all .tdms files contained in argument."""
        files = sqldb.list_tdms(test_const.TEST_DIRECTORY)
        assert len(files) == len(test_const.CORRECT_FILE_LIST)
        for file in files:
            assert file not in test_const.INCORRECT_FILE_LIST or file not in test_const.INCORRECT_FILE_LIST_WIN
            assert file in test_const.CORRECT_FILE_LIST or file in test_const.CORRECT_FILE_LIST_WIN

    def test_move_files(self):
        """Test that files are removed from the directory and into user."""
        try:
            assert path.exists(test_const.CORRECT_FILE_LIST[2])
            sqldb.move_files(path.split(test_const.CORRECT_FILE_LIST[2])[0])
            assert not path.exists(test_const.CORRECT_FILE_LIST[2])
            new_path = path.join(
                path.join(str(Path.home()), "read_files"),
                path.relpath(test_const.CORRECT_FILE_LIST[2])[3:])
            assert path.exists(new_path)
            move(new_path, path.split(test_const.CORRECT_FILE_LIST[2])[0])
        except FileNotFoundError:
            assert False

    def test_get_setting_info(self, test_tdms_obj):
        """Test output when reading .tdms files for settings"""
        assert test_const.TDMS_FF_SETTING == sqldb.get_setting_info(
                                                         test_tdms_obj[0])
        assert test_const.TDMS_FT_SETTING == sqldb.get_setting_info(
                                                         test_tdms_obj[1])
        assert test_const.TDMS_TF_SETTING == sqldb.get_setting_info(
                                                         test_tdms_obj[2])
        assert test_const.TDMS_TT_SETTING == sqldb.get_setting_info(
                                                         test_tdms_obj[3])

    def test_get_test_info(self, test_tdms_obj):
        """Test dictionary output when reading .tdms files for tests"""
        assert test_const.TDMS_FF_TEST== sqldb.get_test_info(
                                                         test_tdms_obj[0])
        assert test_const.TDMS_FT_TEST == sqldb.get_test_info(
                                                         test_tdms_obj[1])
        assert test_const.TDMS_TF_TEST == sqldb.get_test_info(
                                                         test_tdms_obj[2])
        assert test_const.TDMS_TT_TEST == sqldb.get_test_info(
                                                         test_tdms_obj[3])

    def test_get_obs_info(self, test_tdms_obj):
        """Test output when converting Observation data to a dict of strs"""
        assert test_const.TDMS_FF_OBS_07 == sqldb.get_obs_info(
                                                         test_tdms_obj[0], test_const.TEST_INDEX)
        assert test_const.TDMS_FT_OBS_07 == sqldb.get_obs_info(
                                                         test_tdms_obj[1], test_const.TEST_INDEX)
        assert test_const.TDMS_TF_OBS_07 == sqldb.get_obs_info(
                                                         test_tdms_obj[2], test_const.TEST_INDEX)
        assert test_const.TDMS_TT_OBS_07 == sqldb.get_obs_info(
                                                         test_tdms_obj[3], test_const.TEST_INDEX)

    def test_get_temp_info(self, test_tdms_obj):
        """Test output when converting temperature data to a dict of strings"""
        assert test_const.TDMS_FF_THM_07 == sqldb.get_temp_info(
                                                        test_tdms_obj[0],
                                                        test_const.TEST_INDEX,
                                                        test_const.TC_INDEX)
        assert test_const.TDMS_FT_THM_07 == sqldb.get_temp_info(
                                                        test_tdms_obj[1],
                                                        test_const.TEST_INDEX,
                                                        test_const.TC_INDEX)
        assert test_const.TDMS_TF_THM_07 == sqldb.get_temp_info(
                                                        test_tdms_obj[2],
                                                        test_const.TEST_INDEX,
                                                        test_const.TC_INDEX)
        assert test_const.TDMS_TT_THM_07 == sqldb.get_temp_info(
                                                        test_tdms_obj[3],
                                                        test_const.TEST_INDEX,
                                                        test_const.TC_INDEX)

    def test_add_tube_info(self, cursor):
        """Tets data insertion into Tube and handling of dulicate tubes"""
        sqldb.add_tube_info(cursor)
        cursor.execute("SELECT TubeID FROM Tube;")
        assert cursor.fetchone()[0] == 1
        cursor.execute("SELECT TubeID FROM Tube;")
        assert len(cursor.fetchall()) == 1

    def test_add_setting_info(self, cursor, test_tdms_obj):
        """Test data insertion and condition handling in add_setting."""
        sqldb.add_setting_info(cursor, test_tdms_obj[0])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(
                                                    test_tdms_obj[0]))
        assert setting_id == 1

        sqldb.add_setting_info(cursor, test_tdms_obj[1])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(
                                                    test_tdms_obj[1]))
        assert setting_id == 2

        sqldb.add_setting_info(cursor, test_tdms_obj[2])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(
                                                    test_tdms_obj[2]))
        assert setting_id == 3

        sqldb.add_setting_info(cursor, test_tdms_obj[3])
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(
                                                    test_tdms_obj[3]))
        assert setting_id == 4

    def test_add_test_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_test."""
        sqldb.add_test_info(cursor, test_tdms_obj[0], 1)
        cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                       cursor.lastrowid))
        assert cursor.fetchall() == test_const.TDMS_FF_ADD_TEST

        sqldb.add_test_info(cursor, test_tdms_obj[1], 2)
        cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                       cursor.lastrowid))
        assert cursor.fetchall() == test_const.TDMS_FT_ADD_TEST

        sqldb.add_test_info(cursor, test_tdms_obj[2], 3)
        cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                       cursor.lastrowid))
        assert cursor.fetchall() == test_const.TDMS_TF_ADD_TEST

        sqldb.add_test_info(cursor, test_tdms_obj[3], 4)
        cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                       cursor.lastrowid))
        assert cursor.fetchall() == test_const.TDMS_TT_ADD_TEST

    def test_test_exists(self, cursor, test_tdms_obj):
        """Test that you can find tests that already exist."""
        assert 1 == sqldb.test_exists(cursor, test_const.TDMS_FF_TEST)
        assert 2 == sqldb.test_exists(cursor, test_const.TDMS_FT_TEST)
        assert 3 == sqldb.test_exists(cursor, test_const.TDMS_TF_TEST)
        assert 4 == sqldb.test_exists(cursor, test_const.TDMS_TT_TEST)
        assert not 5 == sqldb.test_exists(cursor, test_const.TEST_EXISTS_CONST)
        assert not 6 == sqldb.test_exists(cursor, '')

    def test_add_obs_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_obs."""
        for obs_idx in range(len(test_tdms_obj[0].object("Data", "Idx").data)):
            sqldb.add_obs_info(cursor, test_tdms_obj[0], 1, obs_idx)
        cursor.execute('SELECT DewPoint FROM Observation '
                       'WHERE ObservationID={}'.format(cursor.lastrowid))
        assert cursor.fetchall()[0][0] == Decimal('285.72')

        for obs_idx in range(len(test_tdms_obj[1].object("Data", "Idx").data)):
            sqldb.add_obs_info(cursor, test_tdms_obj[1], 2, obs_idx)
        cursor.execute('SELECT DewPoint FROM Observation '
                       'WHERE ObservationID={}'.format(cursor.lastrowid))
        assert cursor.fetchall()[0][0] == Decimal('285.66')

        for obs_idx in range(len(test_tdms_obj[2].object("Data", "Idx").data)):
            sqldb.add_obs_info(cursor, test_tdms_obj[2], 3, obs_idx)
        cursor.execute('SELECT DewPoint FROM Observation '
                       'WHERE ObservationID={}'.format(cursor.lastrowid))
        assert cursor.fetchall()[0][0] == Decimal('286.62')

        for obs_idx in range(len(test_tdms_obj[3].object("Data", "Idx").data)):
            sqldb.add_obs_info(cursor, test_tdms_obj[3], 4, obs_idx)
        cursor.execute('SELECT DewPoint FROM Observation '
                       'WHERE ObservationID={}'.format(cursor.lastrowid))
        assert cursor.fetchall()[0][0] == Decimal('285.79')

    def test_add_input(self, cursor):
        """Test overall data insertion, the final table in cascade."""
        truncate(cursor, 'Observation')
        truncate(cursor, 'Test')
        truncate(cursor, 'Setting')
        sqldb.add_input(cursor, test_const.TEST_DIRECTORY, True)
        cursor.execute(
            "SELECT Temperature FROM TempObservation WHERE TempObservationID="
            "'{}'".format(cursor.lastrowid))
        assert cursor.fetchall()[0][0] == Decimal('299.45')

    def test_normalize_mass(self, cursor):
        """Test normalize mass querry for results table input"""



def drop_tables(cursor, bol):
    """Drops databese tables if bol is true, does not drop if false"""
    if bol:
        print("Dropping tables...")
        cursor.execute("DROP TABLE IF EXISTS " +
                       ", ".join(const.TABLE_NAME_LIST) + ";")
    else:
        print("Tables not dropped.")


def truncate(cursor, table):
        cursor.execute('SET FOREIGN_KEY_CHECKS=0')
        cursor.execute('TRUNCATE {}'.format(table))
        cursor.execute('SET FOREIGN_KEY_CHECKS=1')
