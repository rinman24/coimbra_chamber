"""Test sqldb."""
import configparser
from datetime import datetime
from decimal import Decimal
import os
import pandas as pd
from pathlib import Path
from shutil import move

from math import isclose

import mysql.connector
import nptdms
import pytest

import chamber.const as const
from chamber.data import sqldb, ddl, dml

config = configparser.ConfigParser()
config.read('config.ini')

# ----------------------------------------------------------------------------
# Global test variables
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

# ----------------------------------------------------------------------------
# Settings global
SETTINGS_TEST_1 = dict(
    Duty=10, IsMass=1, Pressure=100000, Reservoir=1, Temperature=300,
    TimeStep='1.00', TubeId=1
    )
SETTINGS_TEST_2 = dict(
    Duty=20, IsMass=0, Pressure=110000, Reservoir=0, Temperature=270,
    TimeStep='5.00', TubeId=2
    )

TDMS_01_SETTING = dict(
    Duty='0.0', IsMass=0, Pressure=100000, Reservoir=0, Temperature=290,
    TimeStep='1.00', TubeId=1
    )
TDMS_02_SETTING = dict(
    Duty='5.0', IsMass=1, Pressure=100000, Reservoir=0, Temperature=290,
    TimeStep='1.00', TubeId=1
    )
TDMS_03_SETTING = dict(
    Duty='0.0', IsMass=0, Pressure=100000, Reservoir=1, Temperature=290,
    TimeStep='1.00', TubeId=1
    )
TDMS_04_SETTING = dict(
    Duty='5.0', IsMass=1, Pressure=100000, Reservoir=1, Temperature=290,
    TimeStep='1.00', TubeId=1
    )

TDMS_01_ADD_SETTING = [
    (
        1, Decimal('0.0'), 0, 100000, Decimal('290.0'),
        Decimal('1.00'), 0, 1
        )
    ]
TDMS_02_ADD_SETTING = [
        (
            2, Decimal('5.0'), 1, 100000, Decimal('290.0'), Decimal('1.00'),
            0, 1
        )
    ]
TDMS_03_ADD_SETTING = [
        (
            3, Decimal('0.0'), 0, 100000, Decimal('290.0'), Decimal('1.00'),
            1, 1
        )
    ]
TDMS_04_ADD_SETTING = [
        (
            4, Decimal('5.0'), 1, 100000, Decimal('290.0'), Decimal('1.00'),
            1, 1
        )
    ]

# ----------------------------------------------------------------------------
# Test globals
TDMS_01_TEST = dict(Author='author_1',
                    DateTime=datetime(2018, 6, 28, 17, 29, 39),
                    Description='Duty 0; Resevoir Off; IsMass No')
TDMS_02_TEST = dict(Author='author_2',
                    DateTime=datetime(2018, 6, 28, 17, 41, 18),
                    Description='Duty 5; Resevoir Off; IsMass Yes')
TDMS_03_TEST = dict(Author='author_3',
                    DateTime=datetime(2018, 6, 28, 17, 38, 23),
                    Description='Duty 0; Resevoir On; IsMass No')
TDMS_04_TEST = dict(Author='author_4',
                    DateTime=datetime(2018, 6, 28, 17, 42, 32),
                    Description='Duty 5; Resevoir On; IsMass Yes')

TDMS_01_ADD_TEST = [(1, 'author_1', datetime(2018, 6, 28, 17, 29, 39),
                     'Duty 0; Resevoir Off; IsMass No', 1)]
TDMS_02_ADD_TEST = [(2, 'author_2', datetime(2018, 6, 28, 17, 41, 18),
                     'Duty 5; Resevoir Off; IsMass Yes', 2)]
TDMS_03_ADD_TEST = [(3, 'author_3', datetime(2018, 6, 28, 17, 38, 23),
                     'Duty 0; Resevoir On; IsMass No', 3)]
TDMS_04_ADD_TEST = [(4, 'author_4', datetime(2018, 6, 28, 17, 42, 32),
                     'Duty 5; Resevoir On; IsMass Yes', 4)]

# ----------------------------------------------------------------------------
# Observation globals
TDMS_01_OBS_07 = dict(CapManOk=1, DewPoint='286.57', Idx=9, OptidewOk=1,
                      PowOut='0.0002', PowRef='-0.0001', Pressure=99942)
TDMS_02_OBS_07 = dict(CapManOk=1, DewPoint='286.84', Idx=11, OptidewOk=1,
                      PowOut='0.0002', PowRef='0.0000', Pressure=99929,
                      Mass='0.0994313')
TDMS_03_OBS_07 = dict(CapManOk=1, DewPoint='286.69', Idx=9, OptidewOk=1,
                      PowOut='0.0001', PowRef='0.0001', Pressure=99933)
TDMS_04_OBS_07 = dict(CapManOk=1, DewPoint='286.94', Idx=9, OptidewOk=1,
                      PowOut='0.0003', PowRef='0.0000', Pressure=99924,
                      Mass='0.0994310')

OBS_DATA_1 = (
    1, Decimal('286.54'), 1, Decimal('0.0000'), Decimal('0.0000'), 99933
    )
OBS_DATA_2 = (
    1, Decimal('286.90'), Decimal('0.0994314'), 1, Decimal('0.0002'),
    Decimal('0.0000'), 99946
    )
OBS_DATA_3 = (
    1, Decimal('286.71'), 1, Decimal('0.0001'), Decimal('0.0001'), 99964
    )
OBS_DATA_4 = (
    1, Decimal('286.98'), Decimal('0.0994310'), 1, Decimal('0.0001'),
    Decimal('0.0001'), 99937
    )

# ----------------------------------------------------------------------------
# TempObservation globals
TEMP_OBS_1 = [
    293.68, 293.03, 293.94, 292.68, 292.02, 291.79, 291.67, 291.96, 292.07,
    291.62, 291.55, 291.6, 291.53, 291.81
    ]
TEMP_OBS_2 = [
    292.36, 291.85, 291.72, 292.1, 292.34, 291.67, 291.62, 291.64, 291.58,
    291.85
    ]
TEMP_OBS_3 = [
    293.06, 292.73, 293.02, 292.62, 291.85, 291.78, 291.67, 291.74, 291.83,
    291.61, 291.5, 291.58, 291.49, 291.83
    ]
TEMP_OBS_4 = [
    292.06, 291.83, 291.7, 291.94, 292.1, 291.64, 291.56, 291.61, 291.53,
    291.83
    ]

# ----------------------------------------------------------------------------
# Indexes
TEST_INDEX = 7
TC_INDEX = 7


@pytest.fixture(scope='module')
def cnx():
    """Connect to database with module level fixture."""
    # ------------------------------------------------------------------------
    # Connect
    print("\nConnecting to MySQL Server...")
    cnx = sqldb.connect("test")
    print("Successfully connected.")
    yield cnx

    # ------------------------------------------------------------------------
    # Cleanup with new cursor
    print("\nCleaning up test database...")
    cur = cnx.cursor()

    drop_tables(cur, True)
    print("Disconnecting from MySQL...")
    cnx.commit()
    assert cur.close()
    cnx.close()
    print("Connection to MySQL closed.")


@pytest.fixture(scope='module')
def cur(cnx):
    """Obtain a cursor to use at the module level."""
    # ------------------------------------------------------------------------
    # Get cursor
    print("\nObtaining a cursor for the connection...")
    cur = cnx.cursor()
    print("Cursor obtained.")
    yield cur

    # ------------------------------------------------------------------------
    # Close cursor
    print("\nClosing module level cursor...")
    assert cur.close()
    print("Module level cursor closed.")


@pytest.fixture(scope='module')
def test_tdms_obj():
    """Construct list of nptdms.TdmsFile as module level fixture."""
    return (  # IsMass 1 Duty 5%
            nptdms.TdmsFile(CORRECT_FILE_LIST[0]),
            # IsMass 1 Duty 0%
            nptdms.TdmsFile(CORRECT_FILE_LIST[1]),
            # IsMass 0 Duty 5%
            nptdms.TdmsFile(CORRECT_FILE_LIST[2]),
            # IsMass 0 Duty 0%
            nptdms.TdmsFile(CORRECT_FILE_LIST[3]))


def test_connect(cnx):
        """Test connection to database."""
        assert cnx
        assert isinstance(cnx, mysql.connector.connection.MySQLConnection)
        assert not cnx.in_transaction


def test_create_tables(cur):
    """Test create_tables."""
    # Create the tables
    assert sqldb.create_tables(cur, ddl.tables)

    # Now check that all tables exist
    table_names_set = set(ddl.table_name_list)
    cur.execute("SHOW TABLES;")
    for row in cur:
        assert row[0] in table_names_set


def test_add_tube_info(cur):
    """Test add_tube_info."""
    # Add the tube the first time and we should get true
    assert sqldb.add_tube_info(cur)

    # Check that there is one and only one tube with this id
    cur.execute("SELECT TubeID FROM Tube;")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT TubeID FROM Tube;")
    assert len(cur.fetchall()) == 1

    cur.execute("SELECT DiameterIn FROM Tube WHERE TubeID=1;")
    assert cur.fetchone()[0] == Decimal('0.0300000')

    cur.execute("SELECT DiameterOut FROM Tube WHERE TubeID=1;")
    assert cur.fetchone()[0] == Decimal('0.0400000')

    cur.execute("SELECT Length FROM Tube WHERE TubeID=1;")
    assert cur.fetchone()[0] == Decimal('0.0600000')

    cur.execute("SELECT Material FROM Tube WHERE TubeID=1;")
    assert cur.fetchone()[0] == 'Delrin'

    cur.execute("SELECT Mass FROM Tube WHERE TubeID=1;")
    assert cur.fetchone()[0] == Decimal('0.0873832')

    # Now that it is added, we should get a False indicating that it could not
    # be added
    assert not sqldb.add_tube_info(cur)


def test__setting_exists(cur):
    """Test _setting_exists."""
    # ------------------------------------------------------------------------
    # Manually add a setting and assert the setting id is 1
    cur.execute(dml.add_setting, SETTINGS_TEST_1)
    assert 1 == sqldb._setting_exists(cur, SETTINGS_TEST_1)

    # ------------------------------------------------------------------------
    # Assert that other settings do not exist
    assert not sqldb._setting_exists(cur, SETTINGS_TEST_2)

    # ------------------------------------------------------------------------
    # Truncate table so it can be used in subsequent tests
    truncate(cur, 'Setting')


def test__get_temp_info(test_tdms_obj):
    """
    Test get_temp_info.

    NOTE: Dependencies require this test to be run before
    test__get_setting_info.
    """
    # ------------------------------------------------------------------------
    # File 1
    assert (
        '291.96' ==
        sqldb._get_temp_info(test_tdms_obj[0], TEST_INDEX, TC_INDEX)
        )

    # ------------------------------------------------------------------------
    # File 2
    assert (
        '292.10' ==
        sqldb._get_temp_info(test_tdms_obj[1], TEST_INDEX, TC_INDEX)
        )

    # ------------------------------------------------------------------------
    # File 3
    assert (
        '291.74' ==
        sqldb._get_temp_info(test_tdms_obj[2], TEST_INDEX, TC_INDEX)
        )

    # ------------------------------------------------------------------------
    # File 4
    assert (
        '291.94' ==
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
        assert TDMS_04_SETTING == sqldb._get_setting_info(test_tdms_obj[3])


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


def test__add_setting_info(cur, test_tdms_obj):
    """Test _add_setting_info."""
    # ------------------------------------------------------------------------
    # File 1
    # Add a new setting and assert that its id is 1
    setting_id = sqldb._add_setting_info(cur, test_tdms_obj[0])
    assert setting_id == 1
    # Query the new setting and check the results
    cur.execute('SELECT * FROM Setting WHERE SettingID={}'.format(
                   cur.lastrowid))
    assert cur.fetchall() == TDMS_01_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 2
    setting_id = sqldb._add_setting_info(cur, test_tdms_obj[1])
    assert setting_id == 2
    cur.execute('SELECT * FROM Setting WHERE SettingID={}'.format(
                   cur.lastrowid))
    assert cur.fetchall() == TDMS_02_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 3
    setting_id = sqldb._add_setting_info(cur, test_tdms_obj[2])
    assert setting_id == 3
    cur.execute('SELECT * FROM Setting WHERE SettingID={}'.format(
                   cur.lastrowid))
    assert cur.fetchall() == TDMS_03_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 4
    setting_id = sqldb._add_setting_info(cur, test_tdms_obj[3])
    assert setting_id == 4
    cur.execute('SELECT * FROM Setting WHERE SettingID={}'.format(4))
    assert cur.fetchall() == TDMS_04_ADD_SETTING


def test__add_test_info(cur, test_tdms_obj):
    """
    Test _add_test_info.

    NOTE: This must be run before test__test_exists in order to populate the
    Test table.
    """
    # ------------------------------------------------------------------------
    # File 1
    # Add a new test and assert that its id is 1
    test_id = sqldb._add_test_info(cur, test_tdms_obj[0], 1)
    assert test_id == 1
    # Query the new test and check the results
    cur.execute('SELECT * FROM Test WHERE TestID={}'.format(
                   test_id))
    assert cur.fetchall() == TDMS_01_ADD_TEST

    # ------------------------------------------------------------------------
    # File 2
    test_id = sqldb._add_test_info(cur, test_tdms_obj[1], 2)
    assert test_id == 2
    cur.execute('SELECT * FROM Test WHERE TestID={}'.format(
                   test_id))
    assert cur.fetchall() == TDMS_02_ADD_TEST

    # ------------------------------------------------------------------------
    # File 3
    test_id = sqldb._add_test_info(cur, test_tdms_obj[2], 3)
    assert test_id == 3
    cur.execute('SELECT * FROM Test WHERE TestID={}'.format(
                   test_id))
    assert cur.fetchall() == TDMS_03_ADD_TEST

    # ------------------------------------------------------------------------
    # File 4
    test_id = sqldb._add_test_info(cur, test_tdms_obj[3], 4)
    assert test_id == 4
    cur.execute('SELECT * FROM Test WHERE TestID={}'.format(
                   test_id))
    assert cur.fetchall() == TDMS_04_ADD_TEST


def test__test_exists(cur, test_tdms_obj):
    """
    Test _test_exists.

    NOTE: The tests were previously added. All that is left to do is to assert
    that the tests exist.

    Files 1-4 should exist. However, 5 and 6 shouldn't exist.
    """
    # ------------------------------------------------------------------------
    # File 1
    assert 1 == sqldb._test_exists(cur, TDMS_01_TEST)

    # ------------------------------------------------------------------------
    # File 2
    assert 2 == sqldb._test_exists(cur, TDMS_02_TEST)

    # ------------------------------------------------------------------------
    # File 3
    assert 3 == sqldb._test_exists(cur, TDMS_03_TEST)

    # ------------------------------------------------------------------------
    # File 4
    assert 4 == sqldb._test_exists(cur, TDMS_04_TEST)

    # ------------------------------------------------------------------------
    # File 5: Should not exist
    assert not 5 == sqldb._test_exists(cur, TDMS_01_TEST)

    # ------------------------------------------------------------------------
    # File 6: Should not exist
    assert not 6 == sqldb._test_exists(cur, '')


def test__add_obs_info(cur, test_tdms_obj):
    """Test _add_obs_info."""
    # ------------------------------------------------------------------------
    # File 1
    # For every index in the data enter all of the data
    for tdms_idx in range(
            len(test_tdms_obj[0].object("Data", "Idx").data)
            ):
        assert sqldb._add_obs_info(cur, test_tdms_obj[0], 1, tdms_idx)
    # Then check that you can get the last dew point correct
    cur.execute(dml.get_last_dew_point.format(1))
    assert cur.fetchall()[0][0] == Decimal('286.53')

    # ------------------------------------------------------------------------
    # File 2
    for tdms_idx in range(
            len(test_tdms_obj[1].object("Data", "Idx").data)
            ):
        assert sqldb._add_obs_info(cur, test_tdms_obj[1], 2, tdms_idx)
    cur.execute(dml.get_last_dew_point.format(2))
    assert cur.fetchall()[0][0] == Decimal('286.91')

    # ------------------------------------------------------------------------
    # File 3
    for tdms_idx in range(
            len(test_tdms_obj[2].object("Data", "Idx").data)
            ):
        assert sqldb._add_obs_info(cur, test_tdms_obj[2], 3, tdms_idx)
    cur.execute(dml.get_last_dew_point.format(3))
    assert cur.fetchall()[0][0] == Decimal('286.70')

    # ------------------------------------------------------------------------
    # File 4
    for tdms_idx in range(
            len(test_tdms_obj[3].object("Data", "Idx").data)
            ):
        assert sqldb._add_obs_info(cur, test_tdms_obj[3], 4, tdms_idx)
    cur.execute(dml.get_last_dew_point.format(4))
    assert cur.fetchall()[0][0] == Decimal('286.91')


def test__add_temp_info(cur, test_tdms_obj):
    """Test _add_temp_info."""
    # ------------------------------------------------------------------------
    # File 1

    # Add temps with tdms_idx 7 and Idx 8
    assert sqldb._add_temp_info(
        cur, test_tdms_obj[0], 1, TEST_INDEX, TEST_INDEX+1
        )
    # Now query these with the TestId and Idx
    cur.execute(
        dml.get_temp_obs.format(1, TEST_INDEX+1)
        )
    res = [float(r[0]) for r in cur.fetchall()]
    assert res == TEMP_OBS_1

    # ------------------------------------------------------------------------
    # File 2
    assert sqldb._add_temp_info(
        cur, test_tdms_obj[1], 2, TEST_INDEX, TEST_INDEX
        )
    cur.execute(
        dml.get_temp_obs.format(2, TEST_INDEX)
        )
    res = [float(r[0]) for r in cur.fetchall()]
    assert res == TEMP_OBS_2

    # ------------------------------------------------------------------------
    # File 3
    assert sqldb._add_temp_info(
        cur, test_tdms_obj[2], 3, TEST_INDEX, TEST_INDEX+1
        )
    cur.execute(
        dml.get_temp_obs.format(3, TEST_INDEX+1)
        )
    res = [float(r[0]) for r in cur.fetchall()]
    assert res == TEMP_OBS_3

    # ------------------------------------------------------------------------
    # File 4
    assert sqldb._add_temp_info(
        cur, test_tdms_obj[3], 4, TEST_INDEX, TEST_INDEX+1
        )
    cur.execute(
        dml.get_temp_obs.format(4, TEST_INDEX+1)
        )
    res = [float(r[0]) for r in cur.fetchall()]
    assert res == TEMP_OBS_4


def test_add_tdms_file(cnx, cur, test_tdms_obj):
    """
    Test add_tdms_file.

    Test overall data insertion, the final table in cascade.
    """
    # ------------------------------------------------------------------------
    # Clear all of the previous work we have done in the database
    truncate(cur, 'TempObservation')
    truncate(cur, 'Observation')
    truncate(cur, 'Test')
    truncate(cur, 'Setting')
    # assert cnx.in_transaction
    # cnx.commit()
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # File 1
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[0])
    # Verify the data in the 'Setting' table:
    cur.execute('SELECT * FROM Setting WHERE SettingID=1;')
    assert cur.fetchall() == TDMS_01_ADD_SETTING
    # Verify the data in the 'Test' table:
    cur.execute('SELECT * FROM Test WHERE TestID=1;')
    assert cur.fetchall() == TDMS_01_ADD_TEST
    # Verify the data in the `Observation` table:
    cur.execute(dml.get_obs_data_t.format(1, TEST_INDEX))
    res = cur.fetchall()[0]
    for i in range(len(res)):
        assert isclose(res[i], OBS_DATA_1[i])
    # Verify the data in the 'TempObservation` table:
    cur.execute(dml.get_temp_obs_data.format(1, TEST_INDEX, TEST_INDEX))
    res = cur.fetchall()[0][0]
    assert isclose(res, Decimal('291.97'))
    # Commit transaction before next test
    assert cnx.in_transaction
    cnx.commit()
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # File 2
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[1])
    # Verify the data in the 'Setting' table:
    cur.execute('SELECT * FROM Setting WHERE SettingID=2;')
    assert cur.fetchall() == TDMS_02_ADD_SETTING
    # Verify the data in the 'Test' table:
    cur.execute('SELECT * FROM Test WHERE TestID=2;')
    assert cur.fetchall() == TDMS_02_ADD_TEST
    # Verify the data in the `Observation` table:
    cur.execute(dml.get_obs_data_m.format(2, TEST_INDEX))
    res = cur.fetchall()[0]
    for i in range(len(res)):
        assert isclose(res[i], OBS_DATA_2[i])
    # Verify the data in the 'TempObservation` table:
    cur.execute(dml.get_temp_obs_data.format(2, TEST_INDEX, TEST_INDEX))
    res = cur.fetchall()[0][0]
    assert isclose(res, Decimal('292.12'))
    # Commit transaction before next test
    assert cnx.in_transaction
    cnx.commit()
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # File 3
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[2])
    # Verify the data in the 'Setting' table:
    cur.execute('SELECT * FROM Setting WHERE SettingID=3;')
    assert cur.fetchall() == TDMS_03_ADD_SETTING
    # Verify the data in the 'Test' table:
    cur.execute('SELECT * FROM Test WHERE TestID=3;')
    assert cur.fetchall() == TDMS_03_ADD_TEST
    # Verify the data in the `Observation` table:
    cur.execute(dml.get_obs_data_t.format(3, TEST_INDEX))
    res = cur.fetchall()[0]
    for i in range(len(res)):
        assert isclose(res[i], OBS_DATA_3[i])
    # Verify the data in the 'TempObservation` table:
    cur.execute(dml.get_temp_obs_data.format(3, TEST_INDEX, TEST_INDEX))
    res = cur.fetchall()[0][0]
    assert isclose(res, Decimal('291.75'))
    # Commit transaction before next test
    assert cnx.in_transaction
    cnx.commit()
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # File 4
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[3])
    # Verify the data in the 'Setting' table:
    cur.execute('SELECT * FROM Setting WHERE SettingID=2;')
    assert cur.fetchall() == TDMS_02_ADD_SETTING
    # Verify the data in the 'Test' table:
    cur.execute('SELECT * FROM Test WHERE TestID=4;')
    assert cur.fetchall() == TDMS_04_ADD_TEST
    # Verify the data in the `Observation` table:
    cur.execute(dml.get_obs_data_m.format(4, TEST_INDEX))
    res = cur.fetchall()[0]
    for i in range(len(res)):
        assert isclose(res[i], OBS_DATA_4[i])
    # Verify the data in the 'TempObservation` table:
    cur.execute(dml.get_temp_obs_data.format(4, TEST_INDEX, TEST_INDEX))
    res = cur.fetchall()[0][0]
    assert isclose(res, Decimal('291.95'))
    # Commit transaction before next test
    assert cnx.in_transaction
    cnx.commit()
    assert not cnx.in_transaction


def test_get_test_df(cnx):
    """
    Test get_test_df.

    Test resultant `DataFrame` accuracy and structure.
    """
    test_dict = sqldb.get_test_df(1, cnx)
    settings_df = pd.DataFrame(TDMS_01_SETTING, index=[0])
    test_info_df = pd.DataFrame(TDMS_01_TEST, index=[0])
    info_results_df = settings_df.join(test_info_df)
    info_results_df['TestId'] = 1
    info_results_df['SettingId'] = 1
    assert test_dict['info']['Duty'].iloc[0] == Decimal(info_results_df['Duty'].iloc[0])
    assert test_dict['info']['Author'].iloc[0] == info_results_df['Author'].iloc[0]


def drop_tables(cursor, bol):
    """Drop databese tables."""
    print("Dropping tables...")
    cursor.execute("DROP TABLE IF EXISTS " +
                   ", ".join(ddl.table_name_list) +
                   ";")


def truncate(cursor, table):
    """Truncate tables."""
    cursor.execute('SET FOREIGN_KEY_CHECKS=0')
    cursor.execute('TRUNCATE {}'.format(table))
    cursor.execute('SET FOREIGN_KEY_CHECKS=1')
