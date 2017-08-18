"""Docstring."""
from datetime import datetime
from math import isclose

import mysql.connector as conn
from mysql.connector import errorcode
from nptdms import TdmsFile
import pytest
import pytz

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
CORRECT_FILE_LIST = ["test.tdms", "unit_test_01.tdms", "unit_test_02.tdms",
    "unit_test_03.tdms"
    ]
INCORRECT_FILE_LIST = ["py.tdmstest", "py.tdmstest.py", "unit_test_01.tdms_index",
    "unit_test_02.tdms_index", "unit_test_03.tdms_index"
    ]
TDMS_TEST_FILES = ["tests/data_transfer_test_files/tdms_test_files/tdms_test_file_01.tdms",
    "tests/data_transfer_test_files/tdms_test_files/tdms_test_file_02.tdms",
    "tests/data_transfer_test_files/tdms_test_files/tdms_test_file_03.tdms"
    ]
TDMS_01_DICT_SETS = {'initial_dew_point': 292.501, 'initial_duty': 0, 'initial_mass': -0.0658138,
    'initial_pressure': 99977, 'initial_temp': (297.302+297.27
    +297.284+296.835+296.753+297.094+297.054+296.928+296.86+297.318+297.325)/11
    }
TDMS_01_DICT_TESTS = {'author': "ADL", 'date_time': datetime(2017, 8, 3, 19, 33, 9, 217290, pytz.UTC),
    'description': "This is at room temperature, pressure, no laser power, study of boundy development.",
    'time_step': 1
    }

TDMS_01_THM_07 = 296.762
TDMS_01_OBS_08 = {'CapManOk': "1.0", 'DewPoint': "292.43", 'Duty': "0.0", 'Idx': "8.0",
    'Mass': "-0.0658138", 'OptidewOk': "1.0", 'PowOut': "-0.001", 'PowRef': "-0.0015", 'Pressure': "99982.0"
    }
TEST_DIRECTORY = "tests/data_transfer_test_files/tdms_test_files/"
TEST_DICTIONARY = {'InitialDewPoint': '292.50', 'InitialDuty': '0.0', 'InitialMass': '-0.0658138',
    'InitialPressure': '99977.0', 'InitialTemp': '297.093', 'TimeStep': '1.0'
    }
TEST_INDEX = 7

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
    return TdmsFile(TDMS_TEST_FILES[0])


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

    def test_list_tdms(self):
        """Test correct output of all .tdms files contained in argument file."""
        files = sqldb.list_tdms("tests/data_transfer_test_files")

        for file in INCORRECT_FILE_LIST:
            assert file not in files
        for file in CORRECT_FILE_LIST:
            assert file in files

    def test_get_settings(self, test_tdms_obj):
        """Test correct dictionary output when reading .tdms files for settings"""
        assert TDMS_01_DICT_SETS == sqldb.get_settings(test_tdms_obj)

    def test_get_tests(self, test_tdms_obj):
        """Test correct dictionary output when reading .tdms files for tests"""
        assert TDMS_01_DICT_TESTS == sqldb.get_tests(test_tdms_obj)
    
    def test_fixture(self, test_tdms_obj):
        """Test existence of test_tdms_obj fixture"""
        assert test_tdms_obj

    def test_get_temp(self, test_tdms_obj):
        """Test correcct output when converting tdms obj temperature data to dictionary of strings"""
        assert TDMS_01_THM_07 == sqldb.get_temp(test_tdms_obj, TEST_INDEX)

    def test_get_obs(self, test_tdms_obj):
        """Test correcct output when converting tdms obj observation data to dictionary of strings"""
        assert TDMS_01_OBS_08 == sqldb.get_obs(test_tdms_obj, TEST_INDEX)

    def test_add_input(self, cursor):
        """Test correct data insertion through checking add_temp, the final table in cascade."""
        clear_sqldb(cursor)
        sqldb.add_input(cursor, TEST_DIRECTORY)
        cursor.execute("Select Temperature FROM TempObservation WHERE TempObservationID = '{}'".format(sqldb.last_insert_id(cursor)))
        res = cursor.fetchone()
        assert res[0] == Decimal('297.36')
        clear_sqldb(cursor)

    def test_add_setting(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_setting."""
        clear_sqldb(cursor)
        sqldb.add_setting(cursor, test_tdms_obj)
        setting_id = sqldb.setting_exists(cursor, sqldb.get_settings(test_tdms_obj))
        assert isinstance(setting_id, int)
        assert sqldb.add_setting(cursor, test_tdms_obj) == setting_id
        cursor.execute('DELETE FROM Setting;')

    def test_add_test(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_test."""
        clear_sqldb(cursor)
        setting_id = sqldb.add_setting(cursor, test_tdms_obj)
        sqldb.add_test(cursor, test_tdms_obj, str(setting_id))
        cursor.execute("Select Author FROM Test WHERE TestID = '{}'".format(sqldb.last_insert_id(cursor)))
        assert cursor.fetchone()[0] == "ADL"
        clear_sqldb(cursor)

    def test_add_obs(self, cursor, test_tdms_obj):
        """Test correct data insertion and condition handling in add_obs."""
        clear_sqldb(cursor)
        test_id = sqldb.add_test(cursor, test_tdms_obj, str(sqldb.add_setting(cursor, test_tdms_obj)))
        for obs_idx in range(len(test_tdms_obj.object("Data", "Idx").data)):
            sqldb.add_obs(cursor, test_tdms_obj, str(test_id), obs_idx)
        cursor.execute("Select Duty FROM Observation WHERE ObservationID = '{}'".format(sqldb.last_insert_id(cursor)))
        assert cursor.fetchone()[0] == Decimal('0.0')
        clear_sqldb(cursor)


def clear_sqldb(cursor):
    """Clears test database."""
    cursor.execute('DELETE FROM TempObservation;')
    cursor.execute('DELETE FROM Observation;')
    cursor.execute('DELETE FROM Test;') 
    cursor.execute('DELETE FROM Setting;')
