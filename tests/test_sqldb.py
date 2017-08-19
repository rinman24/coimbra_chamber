"""Docstring."""
from datetime import datetime
from decimal import Decimal

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
    cur.execute("DROP TABLE UnitTest;")
    print("Disconnecting from MySQL...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL closed.")

@pytest.fixture(scope='module')
def test_tdms_obj():
    """fixture to instantiate only one TdmsFile object for testing"""
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
        assert not cursor.fetchone()

    def test_setting_exists(self, cursor):
        """Test that you can find settings that already exist."""
        #cursor.execute(sqldb.insert_dml('Setting', SETTINGS_1))
        cursor.execute(const.ADD_SETTING, const.SETTINGS_TEST_1)
        assert sqldb.setting_exists(cursor, const.SETTINGS_TEST_1)
        assert not sqldb.setting_exists(cursor, const.SETTINGS_TEST_2)
        setting_id = cursor.lastrowid
        cursor.execute("DELETE FROM Setting WHERE SettingID = {};".format(setting_id))

    def test_list_tdms(self):
        """Test correct output of all .tdms files contained in argument file."""
        files = sqldb.list_tdms("tests/data_transfer_test_files")
        for tdms_file in const.INCORRECT_FILE_LIST:
            assert tdms_file not in files
        for tdms_file in const.CORRECT_FILE_LIST:
            assert tdms_file in files

    def test_get_setting_info(self, test_tdms_obj):
        """Test correct dictionary output when reading .tdms files for settings"""
        assert const.TDMS_01_SETTING == sqldb.get_setting_info(test_tdms_obj)

    def test_get_test_info(self, test_tdms_obj):
        """Test correct dictionary output when reading .tdms files for tests"""
        assert const.TDMS_01_DICT_TESTS == sqldb.get_test_info(test_tdms_obj)

    def test_get_obs_info(self, test_tdms_obj):
        """Test correcct output when converting tdms obj observation data to dictionary of strings"""
        assert const.TDMS_01_OBS_08 == sqldb.get_obs_info(test_tdms_obj, const.TEST_INDEX)

    def test_get_temp(self, test_tdms_obj):
        """Test correcct output when converting tdms obj temperature data to dictionary of strings"""
        assert const.TDMS_01_THM_07 == sqldb.get_temp(test_tdms_obj, const.TEST_INDEX,
                                                      const.TC_INDEX)

    def test_add_setting_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_setting."""
        sqldb.add_setting_info(cursor, test_tdms_obj)
        setting_id = sqldb.setting_exists(cursor, sqldb.get_setting_info(test_tdms_obj))
        assert isinstance(setting_id, int)
        assert sqldb.add_setting_info(cursor, test_tdms_obj) == setting_id

    def test_add_test_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_test."""
        #clear_sqldb(cursor)
        setting_id = sqldb.add_setting_info(cursor, test_tdms_obj)
        sqldb.add_test_info(cursor, test_tdms_obj, setting_id)
        cursor.execute("Select Author FROM Test WHERE TestID = '{}'".format(cursor.lastrowid))
        assert cursor.fetchone()[0] == "ADL"
        #clear_sqldb(cursor)

    def test_add_obs_info(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_obs."""
        #clear_sqldb(cursor)
        test_id = sqldb.add_test_info(cursor, test_tdms_obj,
                                      sqldb.add_setting_info(cursor, test_tdms_obj))
        for obs_idx in range(len(test_tdms_obj.object("Data", "Idx").data)):
            sqldb.add_obs_info(cursor, test_tdms_obj, test_id, obs_idx)
        cursor.execute('SELECT Duty FROM Observation '
                       'WHERE ObservationID = {}'.format(cursor.lastrowid))
        assert cursor.fetchone()[0] == Decimal('0.0')
        #clear_sqldb(cursor)

    def test_add_input(self, cursor):
        """Test correct data insertion through checking add_temp, the final table in cascade."""
        #clear_sqldb(cursor)
        sqldb.add_input(cursor, const.TEST_DIRECTORY)
        cursor.execute("Select Temperature FROM TempObservation WHERE TempObservationID = '{}'".format(cursor.lastrowid))
        res = cursor.fetchone()
        assert res[0] == Decimal('297.33')
        #clear_sqldb(cursor)

    # def test_enter_into_table(self, cursor):
    #     """Test DDL for row insertion."""
    #     cursor.execute(sqldb.insert_dml('UnitTest', ROW_DATA_2))
    #     cursor.execute("SELECT Number FROM UnitTest WHERE String = 'more testing';")
    #     assert isclose(float(cursor.fetchall()[0][0]), 99.9)
    
    # def test_fixture(self, test_tdms_obj):
    #     """Test existence of test_tdms_obj fixture"""
    #     assert test_tdms_obj

    
    # def test_insert_dml(self):
    #     """Test DML for INSERT statements."""
    #     query = sqldb.insert_dml('UnitTest', ROW_DATA_1)
    #     ref = "INSERT INTO UnitTest     (String)  VALUES    ('unit testing');"
    #     assert ref == query

    # def test_last_insert_id(self, cursor):
    #     """Test retrevial of last insert id."""
    #     assert isinstance(sqldb.last_insert_id(cursor), int)

# def clear_sqldb(cursor):
#     """Clears test database."""
#     cursor.execute('DELETE FROM TempObservation;')
#     cursor.execute('DELETE FROM Observation;')
#     cursor.execute('DELETE FROM Test;') 
#     cursor.execute('DELETE FROM Setting;')