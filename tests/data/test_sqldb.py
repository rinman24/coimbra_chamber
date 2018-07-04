"""Docstring."""
import configparser
from datetime import datetime
from decimal import Decimal
import os
from pathlib import Path
from shutil import move

from math import isclose

import mysql.connector as conn
from mysql.connector.cursor import MySQLCursor
from mysql.connector import errorcode
import nptdms
import pytest

import chamber.const as const
from chamber.data import sqldb, ddl, dml

config = configparser.ConfigParser()
config.read('config.ini')

# ----------------------------------------------------------------------------
# Global variables
CORRECT_FILE_LIST = [os.path.join(os.getcwd(), 'tests',
                                               'data_transfer_test_files',
                                               'test_01.tdms'),
                     os.path.join(os.getcwd(), 'tests',
                                               'data_transfer_test_files',
                                               'tdms_test_folder',
                                               'test_02.tdms'),
                     os.path.join(os.getcwd(), 'tests',
                                               'data_transfer_test_files',
                                               'test_03.tdms'),
                     os.path.join(os.getcwd(), 'tests',
                                               'data_transfer_test_files',
                                               'tdms_test_folder',
                                               'tdms_test_folder_full',
                                               'test_04.tdms')]

SETTINGS_TEST_1 = dict(Duty=10, Pressure=100000, Temperature=300)
SETTINGS_TEST_2 = dict(Duty=20, Pressure=110000, Temperature=270)

TDMS_01_THM_07 = '284.66'
TDMS_02_THM_07 = '283.55'
TDMS_03_THM_07 = '282.43'
TDMS_04_THM_07 = '282.29'

TDMS_01_SETTING = dict(Duty='5.0', Pressure=100000, Temperature=285)
TDMS_02_SETTING = dict(Duty='0.0', Pressure=100000, Temperature=280)
TDMS_03_SETTING = dict(Duty='5.0', Pressure=100000, Temperature=280)

TEST_INDEX = 7
TC_INDEX = 7

TDMS_01_OBS_07 = dict(CapManOk=1, DewPoint='270.69', Idx=8, OptidewOk=1,
                      PowOut='-0.0003', PowRef='-0.0003', Pressure=100393,
                      Mass='0.0985090')
TDMS_02_OBS_07 = dict(CapManOk=1, DewPoint='270.93', Idx=7, OptidewOk=1,
                      PowOut='-0.0004', PowRef='-0.0001', Pressure=100428,
                      Mass='0.0985083')
TDMS_03_OBS_07 = dict(CapManOk=1, DewPoint='270.12', Idx=8, OptidewOk=1,
                      PowOut='-0.0002', PowRef='-0.0000', Pressure=100463)
TDMS_04_OBS_07 = dict(CapManOk=1, DewPoint='270.22', Idx=8, OptidewOk=1,
                      PowOut='-0.0003', PowRef='0.0001', Pressure=100520)

TDMS_01_TEST = dict(Author='author_01',
                    DateTime=datetime(2018, 1, 29, 17, 54, 12),
                    Description='description_01', IsMass=1, TimeStep=1,
                    TubeID=1)
TDMS_02_TEST = dict(Author='author_02',
                    DateTime=datetime(2018, 1, 29, 17, 55, 10),
                    Description='description_02', IsMass=1, TimeStep=1,
                    TubeID=1)
TDMS_03_TEST = dict(Author='author_03',
                    DateTime=datetime(2018, 1, 29, 17, 50, 58),
                    Description='description_03', IsMass=0, TimeStep=1,
                    TubeID=1)
TDMS_04_TEST = dict(Author='author_04',
                    DateTime=datetime(2018, 1, 29, 17, 52, 24),
                    Description='description_04', IsMass=0, TimeStep=1,
                    TubeID=1)

TDMS_01_ADD_SETTING = [(1, Decimal('5.0'), 100000, Decimal('285.0'))]
TDMS_02_ADD_SETTING = [(2, Decimal('0.0'), 100000, Decimal('280.0'))]
TDMS_03_ADD_SETTING = [(3, Decimal('5.0'), 100000, Decimal('280.0'))]

TDMS_01_ADD_TEST = [(1, 'author_01', datetime(2018, 1, 29, 17, 54, 12),
                     'description_01', 1, 1.00, 1, 1)]
TDMS_02_ADD_TEST = [(2, 'author_02', datetime(2018, 1, 29, 17, 55, 10),
                     'description_02', 1, 1.00, 2, 1)]
TDMS_03_ADD_TEST = [(3, 'author_03', datetime(2018, 1, 29, 17, 50, 58),
                     'description_03', 0, 1.00, 3, 1)]
TDMS_04_ADD_TEST = [(4, 'author_04', datetime(2018, 1, 29, 17, 52, 24),
                     'description_04', 0, 1.00, 2, 1)]

TEMP_OBS_1 = [284.61, 280.93, 281.07, 284.66, 286.26,
              281.23, 280.92, 281.32, 280.82, 284.86]
TEMP_OBS_2 = [283.44, 280.71, 280.9, 283.55, 284.4,
              280.96, 280.59, 280.9, 280.56, 283.65]
TEMP_OBS_3 = [283.59, 283.46, 283.34, 283.48, 282.84, 280.51, 280.82,
              282.43, 282.56, 280.85, 280.37, 280.76, 280.39, 282.42]
TEMP_OBS_4 = [283.54, 283.41, 283.28, 283.44, 282.59, 280.51, 280.81,
              282.29, 282.41, 280.84, 280.33, 280.71, 280.37, 282.27]

OBS_DATA_1 = (1, 270.7, 9.8509e-2, 1, -3e-4, 0, 100353)
OBS_DATA_2 = (1, 270.93, 9.85083e-2, 1, -4e-4, -1e-4, 100428)
OBS_DATA_3 = (1, 270.09, 1, -3e-4, -1e-4, 100458)
OBS_DATA_4 = (1, 270.28, 1, -3e-4, -0e-4, 100472)


@pytest.fixture(scope='module')
def cursor():
    """Cursor Fixture at module level so that only one connection is made."""
    print("\nConnecting to MySQL...")
    cnx, cur = sqldb.connect("test")
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
    """Fixture to instantiate only one nptdms.TdmsFile object for testing."""
    return (  # IsMass 1 Duty 5%
            nptdms.TdmsFile(CORRECT_FILE_LIST[0]),
            # IsMass 1 Duty 0%
            nptdms.TdmsFile(CORRECT_FILE_LIST[1]),
            # IsMass 0 Duty 5%
            nptdms.TdmsFile(CORRECT_FILE_LIST[2]),
            # IsMass 0 Duty 0%
            nptdms.TdmsFile(CORRECT_FILE_LIST[3]))


def test_connect(cursor):
        """Test connection to database."""
        assert cursor
        assert isinstance(cursor, MySQLCursor)


def test_create_tables(cursor):
    """Test creation of tables."""
    # Create the tables
    assert sqldb.create_tables(cursor, ddl.tables)

    # Now check that all tables exist
    table_names_set = set(ddl.table_name_list)
    cursor.execute("SHOW TABLES;")
    for row in cursor:
        assert row[0] in table_names_set


def test__setting_exists(cursor):
    """Test _setting_exists."""
    # ------------------------------------------------------------------------
    # Manually add a setting and assert the setting id is 1
    cursor.execute(dml.add_setting, SETTINGS_TEST_1)
    assert 1 == sqldb._setting_exists(cursor, SETTINGS_TEST_1)

    # ------------------------------------------------------------------------
    # Assert that other settings do not exist
    assert not sqldb._setting_exists(cursor, SETTINGS_TEST_2)

    # ------------------------------------------------------------------------
    # Truncate table so it can be used in subsequent tests
    truncate(cursor, 'Setting')


def test__get_temp_info(test_tdms_obj):
    """Test get_temp_info."""
    # ------------------------------------------------------------------------
    # File 1
    assert (
        TDMS_01_THM_07 ==
        sqldb._get_temp_info(test_tdms_obj[0], TEST_INDEX, TC_INDEX)
        )

    # ------------------------------------------------------------------------
    # File 2
    assert (
        TDMS_02_THM_07 ==
        sqldb._get_temp_info(test_tdms_obj[1], TEST_INDEX, TC_INDEX)
        )

    # ------------------------------------------------------------------------
    # File 3
    assert (
        TDMS_03_THM_07 ==
        sqldb._get_temp_info(test_tdms_obj[2], TEST_INDEX, TC_INDEX)
        )

    # ------------------------------------------------------------------------
    # File 4
    assert (
        TDMS_04_THM_07 ==
        sqldb._get_temp_info(test_tdms_obj[3], TEST_INDEX, TC_INDEX)
        )


def test__get_setting_info(test_tdms_obj):
        """Test _get_setting_info."""
        # --------------------------------------------------------------------
        # File 1
        assert TDMS_01_SETTING == sqldb._get_setting_info(test_tdms_obj[0])

        # --------------------------------------------------------------------
        # File 2
        assert TDMS_02_SETTING == sqldb._get_setting_info(test_tdms_obj[1])

        # --------------------------------------------------------------------
        # File 3
        assert TDMS_03_SETTING == sqldb._get_setting_info(test_tdms_obj[2])

        # --------------------------------------------------------------------
        # File 4: This is the same setting at File 2
        assert TDMS_02_SETTING == sqldb._get_setting_info(test_tdms_obj[3])


def test__get_test_info(test_tdms_obj):
        """Test _get_test_info."""
        # --------------------------------------------------------------------
        # File 1
        assert TDMS_01_TEST == sqldb._get_test_info(test_tdms_obj[0])

        # --------------------------------------------------------------------
        # File 2
        assert TDMS_02_TEST == sqldb._get_test_info(test_tdms_obj[1])

        # --------------------------------------------------------------------
        # File 3
        assert TDMS_03_TEST == sqldb._get_test_info(test_tdms_obj[2])

        # --------------------------------------------------------------------
        # File 4
        assert TDMS_04_TEST == sqldb._get_test_info(test_tdms_obj[3])


def test__get_obs_info(test_tdms_obj):
        """Test get_obs_info."""
        # --------------------------------------------------------------------
        # File 1
        assert (
            TDMS_01_OBS_07 ==
            sqldb._get_obs_info(test_tdms_obj[0], TEST_INDEX)
            )

        # --------------------------------------------------------------------
        # File 2
        assert (
            TDMS_02_OBS_07 ==
            sqldb._get_obs_info(test_tdms_obj[1], TEST_INDEX)
            )

        # --------------------------------------------------------------------
        # File 3
        assert (
            TDMS_03_OBS_07 ==
            sqldb._get_obs_info(test_tdms_obj[2], TEST_INDEX)
            )

        # --------------------------------------------------------------------
        # File 4
        assert (
            TDMS_04_OBS_07 ==
            sqldb._get_obs_info(test_tdms_obj[3], TEST_INDEX)
            )


def test_add_tube_info(cursor):
    """Test add_tube_info."""
    # Add the tube the first time and we should get true
    assert sqldb.add_tube_info(cursor)

    # Check that there is one and only one tube with this id
    cursor.execute("SELECT TubeID FROM Tube;")
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT TubeID FROM Tube;")
    assert len(cursor.fetchall()) == 1

    cursor.execute("SELECT DiameterIn FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == Decimal('0.0300000')

    cursor.execute("SELECT DiameterOut FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == Decimal('0.0400000')

    cursor.execute("SELECT Length FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == Decimal('0.0600000')

    cursor.execute("SELECT Material FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == 'Delrin'

    cursor.execute("SELECT Mass FROM Tube WHERE TubeID=1;")
    assert cursor.fetchone()[0] == Decimal('0.0873832')

    # Now that it is added, we should get a False indicating that it could not
    # be added
    assert not sqldb.add_tube_info(cursor)


def test__add_setting_info(cursor, test_tdms_obj):
    """Test _add_setting_info."""
    # ------------------------------------------------------------------------
    # File 1
    # Add a new setting and assert that its id is 1
    setting_id = sqldb._add_setting_info(cursor, test_tdms_obj[0])
    assert setting_id == 1
    # Query the new setting and check the results
    cursor.execute('SELECT * FROM Setting WHERE SettingID={}'.format(
                   cursor.lastrowid))
    assert cursor.fetchall() == TDMS_01_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 2
    setting_id = sqldb._add_setting_info(cursor, test_tdms_obj[1])
    assert setting_id == 2
    cursor.execute('SELECT * FROM Setting WHERE SettingID={}'.format(
                   cursor.lastrowid))
    assert cursor.fetchall() == TDMS_02_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 3
    setting_id = sqldb._add_setting_info(cursor, test_tdms_obj[2])
    assert setting_id == 3
    cursor.execute('SELECT * FROM Setting WHERE SettingID={}'.format(
                   cursor.lastrowid))
    assert cursor.fetchall() == TDMS_03_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 4
    setting_id = sqldb._add_setting_info(cursor, test_tdms_obj[3])
    assert setting_id == 2  # This test has the same setting at 2
    cursor.execute('SELECT * FROM Setting WHERE SettingID={}'.format(2))
    assert cursor.fetchall() == TDMS_02_ADD_SETTING


def test__add_test_info(cursor, test_tdms_obj):
    """Test _add_test_info."""
    # ------------------------------------------------------------------------
    # File 1
    # Add a new test and assert that its id is 1
    test_id = sqldb._add_test_info(cursor, test_tdms_obj[0], 1)
    assert test_id == 1
    # Query the new test and check the results
    cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                   test_id))
    assert cursor.fetchall() == TDMS_01_ADD_TEST

    # ------------------------------------------------------------------------
    # File 2
    test_id = sqldb._add_test_info(cursor, test_tdms_obj[1], 2)
    assert test_id == 2
    cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                   test_id))
    assert cursor.fetchall() == TDMS_02_ADD_TEST

    # ------------------------------------------------------------------------
    # File 3
    test_id = sqldb._add_test_info(cursor, test_tdms_obj[2], 3)
    assert test_id == 3
    cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                   test_id))
    assert cursor.fetchall() == TDMS_03_ADD_TEST

    # ------------------------------------------------------------------------
    # File 4
    test_id = sqldb._add_test_info(cursor, test_tdms_obj[3], 2)
    assert test_id == 4
    cursor.execute('SELECT * FROM Test WHERE TestID={}'.format(
                   test_id))
    assert cursor.fetchall() == TDMS_04_ADD_TEST


def test__test_exists(cursor, test_tdms_obj):
    """
    Test _test_exists.

    The tests were previously added. All that is left to do is to assert that
    the tests exist.

    Files 1-4 should exist. However, 5 and 6 shouldn't exist.
    """
    # ------------------------------------------------------------------------
    # File 1
    assert 1 == sqldb._test_exists(cursor, TDMS_01_TEST)

    # ------------------------------------------------------------------------
    # File 2
    assert 2 == sqldb._test_exists(cursor, TDMS_02_TEST)

    # ------------------------------------------------------------------------
    # File 3
    assert 3 == sqldb._test_exists(cursor, TDMS_03_TEST)

    # ------------------------------------------------------------------------
    # File 4
    assert 4 == sqldb._test_exists(cursor, TDMS_04_TEST)

    # ------------------------------------------------------------------------
    # File 5: Should not exist
    assert not 5 == sqldb._test_exists(cursor, TDMS_01_TEST)

    # ------------------------------------------------------------------------
    # File 6: Should not exist
    assert not 6 == sqldb._test_exists(cursor, '')


def test__add_obs_info(cursor, test_tdms_obj):
    """Test _add_obs_info."""
    # ------------------------------------------------------------------------
    # File 1
    # For every index in the data enter all of the data
    for tdms_idx in range(
            len(test_tdms_obj[0].object("Data", "Idx").data)
            ):
        assert sqldb._add_obs_info(cursor, test_tdms_obj[0], 1, tdms_idx)
    # Then check that you can get the last dew point correct
    cursor.execute(dml.get_last_dew_point.format(1))
    assert cursor.fetchall()[0][0] == Decimal('270.78')

    # ------------------------------------------------------------------------
    # File 2
    for tdms_idx in range(
            len(test_tdms_obj[1].object("Data", "Idx").data)
            ):
        assert sqldb._add_obs_info(cursor, test_tdms_obj[1], 2, tdms_idx)
    cursor.execute(dml.get_last_dew_point.format(2))
    assert cursor.fetchall()[0][0] == Decimal('270.93')

    # ------------------------------------------------------------------------
    # File 3
    for tdms_idx in range(
            len(test_tdms_obj[2].object("Data", "Idx").data)
            ):
        assert sqldb._add_obs_info(cursor, test_tdms_obj[2], 3, tdms_idx)
    cursor.execute(dml.get_last_dew_point.format(3))
    assert cursor.fetchall()[0][0] == Decimal('270.20')

    # ------------------------------------------------------------------------
    # File 4
    for tdms_idx in range(
            len(test_tdms_obj[3].object("Data", "Idx").data)
            ):
        assert sqldb._add_obs_info(cursor, test_tdms_obj[3], 4, tdms_idx)
    cursor.execute(dml.get_last_dew_point.format(4))
    assert cursor.fetchall()[0][0] == Decimal('270.32')


def test__add_temp_info(cursor, test_tdms_obj):
    """Test _add_temp_info."""
    # ------------------------------------------------------------------------
    # File 1

    # Add temps with tdms_idx 7 and Idx 8
    assert sqldb._add_temp_info(
        cursor, test_tdms_obj[0], 1, TEST_INDEX, TEST_INDEX+1
        )
    # Now query these with the TestId and Idx
    cursor.execute(
        dml.get_temp_obs.format(1, TEST_INDEX+1)
        )
    res = [float(r[0]) for r in cursor.fetchall()]
    assert res == TEMP_OBS_1

    # ------------------------------------------------------------------------
    # File 2
    assert sqldb._add_temp_info(
        cursor, test_tdms_obj[1], 2, TEST_INDEX, TEST_INDEX
        )
    cursor.execute(
        dml.get_temp_obs.format(2, TEST_INDEX)
        )
    res = [float(r[0]) for r in cursor.fetchall()]
    assert res == TEMP_OBS_2

    # ------------------------------------------------------------------------
    # File 3
    assert sqldb._add_temp_info(
        cursor, test_tdms_obj[2], 3, TEST_INDEX, TEST_INDEX+1
        )
    cursor.execute(
        dml.get_temp_obs.format(3, TEST_INDEX+1)
        )
    res = [float(r[0]) for r in cursor.fetchall()]
    assert res == TEMP_OBS_3

    # ------------------------------------------------------------------------
    # File 4
    assert sqldb._add_temp_info(
        cursor, test_tdms_obj[3], 4, TEST_INDEX, TEST_INDEX+1
        )
    cursor.execute(
        dml.get_temp_obs.format(4, TEST_INDEX+1)
        )
    res = [float(r[0]) for r in cursor.fetchall()]
    assert res == TEMP_OBS_4


def test_add_tdms_file(cursor, test_tdms_obj):
    """
    Test add_tdms_file.

    Test overall data insertion, the final table in cascade.
    """
    # ------------------------------------------------------------------------
    # Clear all of the previous work we have done in the database
    truncate(cursor, 'TempObservation')
    truncate(cursor, 'Observation')
    truncate(cursor, 'Test')
    truncate(cursor, 'Setting')

    # ------------------------------------------------------------------------
    # File 1
    assert sqldb.add_tdms_file(cursor, test_tdms_obj[0])
    # Verify the data in the 'Setting' table:
    cursor.execute('SELECT * FROM Setting WHERE SettingID=1;')
    assert cursor.fetchall() == TDMS_01_ADD_SETTING
    # Verify the data in the 'Test' table:
    cursor.execute('SELECT * FROM Test WHERE TestID=1;')
    assert cursor.fetchall() == TDMS_01_ADD_TEST
    # Verify the data in the `Observation` table:
    cursor.execute(dml.get_obs_data_m.format(1, TEST_INDEX))
    res = cursor.fetchall()[0]
    for i in range(len(res)):
        assert isclose(res[i], OBS_DATA_1[i])
    # Verify the data in the 'TempObservation` table:
    cursor.execute(dml.get_temp_obs_data.format(1, TEST_INDEX, TEST_INDEX))
    res = cursor.fetchall()[0][0]
    assert isclose(res, 284.69)

    # ------------------------------------------------------------------------
    # File 2
    assert sqldb.add_tdms_file(cursor, test_tdms_obj[1])
    # Verify the data in the 'Setting' table:
    cursor.execute('SELECT * FROM Setting WHERE SettingID=2;')
    assert cursor.fetchall() == TDMS_02_ADD_SETTING
    # Verify the data in the 'Test' table:
    cursor.execute('SELECT * FROM Test WHERE TestID=2;')
    assert cursor.fetchall() == TDMS_02_ADD_TEST
    # Verify the data in the `Observation` table:
    cursor.execute(dml.get_obs_data_m.format(2, TEST_INDEX))
    res = cursor.fetchall()[0]
    for i in range(len(res)):
        assert isclose(res[i], OBS_DATA_2[i])
    # Verify the data in the 'TempObservation` table:
    cursor.execute(dml.get_temp_obs_data.format(2, TEST_INDEX, TEST_INDEX))
    res = cursor.fetchall()[0][0]
    assert isclose(res, 283.55)

    # ------------------------------------------------------------------------
    # File 3
    assert sqldb.add_tdms_file(cursor, test_tdms_obj[2])
    # Verify the data in the 'Setting' table:
    cursor.execute('SELECT * FROM Setting WHERE SettingID=3;')
    assert cursor.fetchall() == TDMS_03_ADD_SETTING
    # Verify the data in the 'Test' table:
    cursor.execute('SELECT * FROM Test WHERE TestID=3;')
    assert cursor.fetchall() == TDMS_03_ADD_TEST
    # Verify the data in the `Observation` table:
    cursor.execute(dml.get_obs_data_t.format(3, TEST_INDEX))
    res = cursor.fetchall()[0]
    for i in range(len(res)):
        assert isclose(res[i], OBS_DATA_3[i])
    # Verify the data in the 'TempObservation` table:
    cursor.execute(dml.get_temp_obs_data.format(3, TEST_INDEX, TEST_INDEX))
    res = cursor.fetchall()[0][0]
    assert isclose(res, 282.45)

    # ------------------------------------------------------------------------
    # File 4
    assert sqldb.add_tdms_file(cursor, test_tdms_obj[3])
    # Verify the data in the 'Setting' table:
    cursor.execute('SELECT * FROM Setting WHERE SettingID=2;')
    assert cursor.fetchall() == TDMS_02_ADD_SETTING
    # Verify the data in the 'Test' table:
    cursor.execute('SELECT * FROM Test WHERE TestID=4;')
    assert cursor.fetchall() == TDMS_04_ADD_TEST
    # Verify the data in the `Observation` table:
    cursor.execute(dml.get_obs_data_t.format(4, TEST_INDEX))
    res = cursor.fetchall()[0]
    for i in range(len(res)):
        assert isclose(res[i], OBS_DATA_4[i])
    # Verify the data in the 'TempObservation` table:
    cursor.execute(dml.get_temp_obs_data.format(4, TEST_INDEX, TEST_INDEX))
    res = cursor.fetchall()[0][0]
    assert isclose(res, 282.28)


def drop_tables(cursor, bol):
    """Drop databese tables if bol is true."""
    if bol:
        print("Dropping tables...")
        cursor.execute("DROP TABLE IF EXISTS " +
                       ", ".join(ddl.table_name_list) + ";")
    else:
        print("Tables not dropped.")


def truncate(cursor, table):
    """Truncate tables."""
    cursor.execute('SET FOREIGN_KEY_CHECKS=0')
    cursor.execute('TRUNCATE {}'.format(table))
    cursor.execute('SET FOREIGN_KEY_CHECKS=1')
