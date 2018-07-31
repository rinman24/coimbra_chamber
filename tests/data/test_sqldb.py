"""Test sqldb."""
import configparser
from datetime import datetime
from decimal import Decimal
import os
from pathlib import Path
import pickle as pkl
from shutil import move

from math import isclose

import mysql.connector
import nptdms
import pandas as pd
import pytest

import chamber.const as const
from chamber.analysis import experiments
from chamber.data import sqldb, ddl, dml
import dml_test

config = configparser.ConfigParser()
config.read('config.ini')

# ----------------------------------------------------------------------------
# Test `add_tube_info` global variables
TUBE_TABLE = [(1, Decimal('0.0300000'), Decimal('0.0400000'),
               Decimal('0.0600000'), 'Delrin', Decimal('0.0873832'))]

# ----------------------------------------------------------------------------
# Test `_setting_exists` global variables
SETTINGS_TEST_1 = dict(
    Duty=10, IsMass=1, Pressure=100000, Reservoir=1, Temperature=300,
    TimeStep='1.00', TubeId=1
    )
SETTINGS_TEST_2 = dict(
    Duty=20, IsMass=0, Pressure=110000, Reservoir=0, Temperature=270,
    TimeStep='5.00', TubeId=2
    )

# ----------------------------------------------------------------------------
# Test `_get_temp_info` and `_add_temp_info` global variables
TEST_INDEX = 7
TC_INDEX = 7

# ----------------------------------------------------------------------------
# Test `_get_setting_info` global variables
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

# ----------------------------------------------------------------------------
# Test `_get_test_info` and `_test_exists` global variables
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

# ----------------------------------------------------------------------------
# Test `_get_obs_info` global variables
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

# ----------------------------------------------------------------------------
# Test `_add_setting_info` global variables
TDMS_01_ADD_SETTING = [(
    1, Decimal('0.0'), 0, 100000, Decimal('290.0'), Decimal('1.00'), 0, 1
    )]
TDMS_02_ADD_SETTING = [(
    2, Decimal('5.0'), 1, 100000, Decimal('290.0'), Decimal('1.00'), 0, 1
    )]
TDMS_03_ADD_SETTING = [(
    3, Decimal('0.0'), 0, 100000, Decimal('290.0'), Decimal('1.00'), 1, 1
    )]
TDMS_04_ADD_SETTING = [(
    4, Decimal('5.0'), 1, 100000, Decimal('290.0'), Decimal('1.00'), 1, 1
    )]

# ----------------------------------------------------------------------------
# Test `_add_test_info` global variables
TDMS_01_ADD_TEST = [(1, 'author_1', datetime(2018, 6, 28, 17, 29, 39),
                     'Duty 0; Resevoir Off; IsMass No', 1)]
TDMS_02_ADD_TEST = [(2, 'author_2', datetime(2018, 6, 28, 17, 41, 18),
                     'Duty 5; Resevoir Off; IsMass Yes', 2)]
TDMS_03_ADD_TEST = [(3, 'author_3', datetime(2018, 6, 28, 17, 38, 23),
                     'Duty 0; Resevoir On; IsMass No', 3)]
TDMS_04_ADD_TEST = [(4, 'author_4', datetime(2018, 6, 28, 17, 42, 32),
                     'Duty 5; Resevoir On; IsMass Yes', 4)]

# ----------------------------------------------------------------------------
# Test `_add_obs_info` global variables
OBS_COLS = ['Idx', 'PowOut', 'PowRef', 'Pressure', 'TestId', 'Mass']
OBS_BIT_COLS = ['CapManOk', 'OptidewOk']
OBS_STATS_1 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    CapManOk=[27, 27, 0, 1.0000, 1, 1],
    DewPoint=[27, 7737.23, 0.000705624142660792, 286.564074, 286.52, 286.63],
    Idx=[27, 405, 60.666666666666664, 15.0000, 2, 28],
    Mass=[0, None, None, None, None, None],
    OptidewOk=[27, 27, 0, 1.0000, 1, 1],
    PowOut=[27, 0.0051, 0.000000012839506172839506,
            0.00018889, -0.0001, 0.0004],
    PowRef=[27, -0.0009, 0.00000000888888888888889,
            -0.00003333, -0.0003, 0.0002],
    Pressure=[27, 2698644, 239.28395061728366, 99949.7778, 99929, 99986],
    TestId=[27, 27, 0, 1.0000, 1, 1],
    )
).set_index('idx')
OBS_STATS_2 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    CapManOk=[15, 15, 0, 1.0000, 1, 1],
    DewPoint=[15, 4303.06, 0.00045955555555561106, 286.870667, 286.83, 286.91],
    Idx=[15, 165, 18.666666666666668, 11.0000, 4, 18],
    Mass=[15, 1.4914701, 0.0000000000000024000000004137717, 0.09943134000,
          0.0994313, 0.0994314],
    OptidewOk=[15, 15, 0, 1.0000, 1, 1],
    PowOut=[15, 0.0014, 0.000000009955555555555556, 0.00009333,
            -0.0001, 0.0002],
    PowRef=[15, 0.0002, 0.000000003822222222222223, 0.00001333,
            -0.0001, 0.0001],
    Pressure=[15, 1498947, 439.6266666666366, 99929.8000, 99907, 99981],
    TestId=[15, 30, 0, 2.0000, 2, 2],
    )
).set_index('idx')
OBS_STATS_3 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    CapManOk=[13, 13, 0, 1.0000, 1, 1],
    DewPoint=[13, 3726.87, 0.0007408284023666399, 286.682308, 286.63, 286.72],
    Idx=[13, 104, 14, 8.0000, 2, 14],
    Mass=[0, None, None, None, None, None],
    OptidewOk=[13, 13, 0, 1.0000, 1, 1],
    PowOut=[13, 0.0026, 0.000000009230769230769232, 0.00020000,
            0.0001, 0.0004],
    PowRef=[13, 0.0003, 0.000000004852071005917161, 0.00002308,
            -0.0001, 0.0001],
    Pressure=[13, 1299252, 95.47928994086436, 99942.4615, 99929, 99964],
    TestId=[13, 39, 0, 3.0000, 3, 3],
    )
).set_index('idx')
OBS_STATS_4 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    CapManOk=[14, 14, 0, 1.0000, 1, 1],
    DewPoint=[14, 4017.18, 0.0005408163265310136, 286.941429, 286.91, 286.98],
    Idx=[14, 119, 16.25, 8.5000, 2, 15],
    Mass=[14, 1.3920334, 0.0000000000000024489795920957832, 0.09943095714,
          0.0994309, 0.0994310],
    OptidewOk=[14, 14, 0, 1.0000, 1, 1],
    PowOut=[14, 0.0027, 0.00000000923469387755102, 0.00019286, 0.0000, 0.0003],
    PowRef=[14, 0.0006, 0.00000000816326530612245, 0.00004286,
            -0.0001, 0.0002],
    Pressure=[14, 1398995, 67.02551020410793, 99928.2143, 99911, 99942],
    TestId=[14, 56, 0, 4.0000, 4, 4],
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test `_add_temp_info` global variables
TEMP_OBS_1 = [293.68, 293.03, 293.94, 292.68, 292.02, 291.79, 291.67, 291.96,
              292.07, 291.62, 291.55, 291.6, 291.53, 291.81]
TEMP_OBS_2 = [292.36, 291.85, 291.72, 292.1, 292.34, 291.67, 291.62, 291.64,
              291.58, 291.85]
TEMP_OBS_3 = [293.06, 292.73, 293.02, 292.62, 291.85, 291.78, 291.67, 291.74,
              291.83, 291.61, 291.5, 291.58, 291.49, 291.83]
TEMP_OBS_4 = [292.06, 291.83, 291.7, 291.94, 292.1, 291.64, 291.56, 291.61,
              291.53, 291.83]
TEMP_OBS_STATS_1 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    ThermocoupleNum=[378, 2457, 16.25000000000001, 6.5000, 0, 13],
    Temperature=[378, 110454.30, 0.5940934240362769,
                 292.207143, 291.51, 293.96],
    Idx=[378, 5670, 60.666666666666664, 15.0000, 2, 28],
    TestId=[378, 378, 0, 1.0000, 1, 1],
    )
).set_index('idx')
TEMP_OBS_STATS_2 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    ThermocoupleNum=[150, 1275, 8.25, 8.5000, 4, 13],
    Temperature=[150, 43780.54, 0.0793492622222213,
                 291.870267, 291.56, 292.43],
    Idx=[150, 1650, 18.666666666666675, 11.0000, 4, 18],
    TestId=[150, 300, 0, 2.0000, 2, 2],
    )
).set_index('idx')
TEMP_OBS_STATS_3 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    ThermocoupleNum=[182, 1183, 16.250000000000007, 6.5000, 0, 13],
    Temperature=[182, 53149.04, 0.30165401521555363,
                 292.027692, 291.49, 293.09],
    Idx=[182, 1456, 13.999999999999982, 8.0000, 2, 14],
    TestId=[182, 546, 0, 3.0000, 3, 3],
    )
).set_index('idx')
TEMP_OBS_STATS_4 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    ThermocoupleNum=[140, 1190, 8.25, 8.5000, 4, 13],
    Temperature=[140, 40850.05, 0.03764956632653166,
                 291.786071, 291.53, 292.14],
    Idx=[140, 1190, 16.250000000000007, 8.5000, 2, 15],
    TestId=[140, 560, 0, 4.0000, 4, 4],
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test `_get_test_dict` global variables`
_ = {
    'Temperature': [290.0], 'Pressure': [100000], 'Duty': [0.0],
    'IsMass': [0], 'Reservoir': [0], 'TimeStep': [1.0],
    'DateTime': [pd.Timestamp(datetime(2018, 6, 28, 17, 29, 39))],
    'Author': 'author_1', 'Description': 'Duty 0; Resevoir Off; IsMass No',
    'TubeId': [1], 'TestId': [1], 'SettingId': [1]
}
_ = pd.DataFrame(_)
TEST_1_INFO_DF = _[['Temperature', 'Pressure', 'Duty', 'IsMass', 'Reservoir',
                    'TimeStep', 'DateTime', 'Author', 'Description', 'TubeId',
                    'TestId', 'SettingId']]
TEST_1_STATS_DF = pd.DataFrame(dict(
    idx=['sum', 'mean', 'min', 'max', 'var'],
    TC0=[7929.21, 293.67444444444442, 293.65, 293.71, 0.00031794871794867406],
    TC1=[7911.38, 293.014074, 292.99, 293.04, 0.00014045584045569836],
    TC7=[7882.79, 291.955185, 291.94, 291.98, 0.00011054131054147711],
    TC13=[7878.85, 291.809259, 291.80, 291.81999999999999,
          2.2507122507081566e-05],
    Pressure=[2698644, 99949.7778, 99929, 99986, 248.48717948717953],
    PowOut=[0.0051, 0.00018888888888888883, -0.0001, 0.0004,
            1.3333333333333332e-08],
    PowRef=[-0.0009, -3.3333333333333335e-05, -0.0003, 0.0002,
            9.2307692307692321e-09],
    DewPoint=[7737.23, 286.564074, 286.52, 286.63, 0.00073276353276327522],
    )
).set_index('idx')
TEST_1_DATA_DF_SIZE = (27, 22)

# ----------------------------------------------------------------------------
# Test `get_test_from_set` global variables
FALSE_SETTING = dict(
    Duty='5.0', IsMass=0, Pressure=100000, Reservoir=1, Temperature=290,
    TimeStep='1.00', TubeId=1
    )

# ----------------------------------------------------------------------------
# Test `_add_rh_targets` global variables
RH_TARGET_LIST = [Decimal('{:.2f}'.format(rh/100)) for rh in range(10, 85, 5)]
RH_TARGET_LENGTH = 15
ANALYSIS_DF = pkl.load(open(os.path.join(
    os.getcwd(), 'tests', 'data_test_files', 'analysis_df'), 'rb'))

# ----------------------------------------------------------------------------
# Test `_add_results` global variables`
ANALYSIS_TEST_ID = 1
RESULTS_LIST = [Decimal('0.50'), 1, 0.0988713, 1.36621e-07, -3.07061e-09,
                9.40458e-12, 329.257, Decimal('1.00'), 599]
RESULTS_STATS_DF = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    RH=[203, 113.30, 0.038566939260841114, 0.558128, 0.10, 0.80],
    TestId=[203, 203, 0, 1, 1, 1],
    A=[203, 20.068446189165115, 0.0000000004217527972078824,
       0.09885934083332569, 0.09882460534572601, 0.09888873994350433],
    SigA=[203, 0.00002547581137690713, 0.00000000000007869983827708191,
          0.00000012549660776801542, 0.00000000749269091215865,
          0.000002316897962373332],
    B=[203, -0.0000005678920625973305, 1.2240284969968573e-18,
       -0.0000000027974978453070467, -0.0000000062952878465694084,
       -0.000000001419641071365163],
    SigB=[203, 0.0000000014641018173495394, 1.5663600224894891e-22,
          0.0000000000072123242233967456, 0.00000000000033056150590231315,
          0.00000000004862525659898864],
    Chi2=[203, 294410.082069397, 1582684.6019887875, 1450.2959707852067,
          97.25215148925781, 6133.92626953125],
    Q=[203, 177.95, 0.09717613142760072, 0.876601, 0.00, 1.00],
    Nu=[203, 371997, 1660749.8362008312, 1832.4975, 199, 5599],
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test `_add_best_fit` global variables
BEST_FIT_STATS_DF = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    RH=[15, 6.75, 0.04666666666666666, 0.450000, 0.10, 0.80],
    TestId=[15, 15, 0, 1, 1, 1],
    Nu=[15, 36585, 2049066.666666667, 2439.0000, 199, 5199],
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# `test_tdms_obj` fixture global variables
CORRECT_FILE_LIST = [os.path.join(os.getcwd(), 'tests',
                                               'data_test_files',
                                               'test_01.tdms'),
                     os.path.join(os.getcwd(), 'tests',
                                               'data_test_files',
                                               'tdms_test_folder',
                                               'test_02.tdms'),
                     os.path.join(os.getcwd(), 'tests',
                                               'data_test_files',
                                               'test_03.tdms'),
                     os.path.join(os.getcwd(), 'tests',
                                               'data_test_files',
                                               'tdms_test_folder',
                                               'tdms_test_folder_full',
                                               'test_04.tdms')]


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
def results_cnx():
    """Connect to database with module level fixture."""
    # ------------------------------------------------------------------------
    # Connect
    print("\nConnecting to MySQL Server...")
    results_cnx = sqldb.connect("test_results")
    print("Successfully connected to test_results.")
    yield results_cnx

    # ------------------------------------------------------------------------
    # Cleanup with new cursor
    print("\nClearing results...")
    results_cur = results_cnx.cursor()
    clear_results(results_cur, True)

    print("Disconnecting from MySQL results_cnx...")
    results_cnx.commit()
    assert results_cur.close()
    results_cnx.close()
    print("Connection to MySQL results_cnx closed.")


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
    cur.execute('SHOW TABLES;')
    for row in cur:
        assert row[0] in table_names_set


def test_add_tube_info(cur):
    """Test add_tube_info."""
    # Add the tube the first time and we should get true
    assert sqldb.add_tube_info(cur)

    cur.execute(dml_test.get_tube)
    res = cur.fetchall()
    assert res == TUBE_TABLE

    # Check duplicate entry error
    assert not sqldb.add_tube_info(cur)

    # Check that Tube table is unaffected
    cur.execute(dml_test.get_tube)
    res = cur.fetchall()
    assert res == TUBE_TABLE


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
    cur.execute(dml_test.get_setting.format(cur.lastrowid))
    assert cur.fetchall() == TDMS_01_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 2
    setting_id = sqldb._add_setting_info(cur, test_tdms_obj[1])
    assert setting_id == 2
    cur.execute(dml_test.get_setting.format(cur.lastrowid))
    assert cur.fetchall() == TDMS_02_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 3
    setting_id = sqldb._add_setting_info(cur, test_tdms_obj[2])
    assert setting_id == 3
    cur.execute(dml_test.get_setting.format(cur.lastrowid))
    assert cur.fetchall() == TDMS_03_ADD_SETTING

    # ------------------------------------------------------------------------
    # File 4
    setting_id = sqldb._add_setting_info(cur, test_tdms_obj[3])
    assert setting_id == 4
    cur.execute(dml_test.get_setting.format(4))
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
    cur.execute(dml_test.get_test.format(test_id))
    assert cur.fetchall() == TDMS_01_ADD_TEST

    # ------------------------------------------------------------------------
    # File 2
    test_id = sqldb._add_test_info(cur, test_tdms_obj[1], 2)
    assert test_id == 2
    cur.execute(dml_test.get_test.format(test_id))
    assert cur.fetchall() == TDMS_02_ADD_TEST

    # ------------------------------------------------------------------------
    # File 3
    test_id = sqldb._add_test_info(cur, test_tdms_obj[2], 3)
    assert test_id == 3
    cur.execute(dml_test.get_test.format(test_id))
    assert cur.fetchall() == TDMS_03_ADD_TEST

    # ------------------------------------------------------------------------
    # File 4
    test_id = sqldb._add_test_info(cur, test_tdms_obj[3], 4)
    assert test_id == 4
    cur.execute(dml_test.get_test.format(test_id))
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
    for tdms_idx in range(len(test_tdms_obj[0].object("Data", "Idx").data)):
        assert sqldb._add_obs_info(cur, test_tdms_obj[0], 1, tdms_idx)

    # Check column statistics for the TestId
    for col in OBS_COLS[:-1]:
        # First loop through the coloumn names eg. 'Mass', 'DewPoint', etc...
        cur.execute(dml_test.get_stats_test_id.format(col, 1, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_1)):
            # Loop through the length of the dataframe
            # This allows us to loop through the index values, 'min', 'max', etc...
            val = OBS_STATS_1.index.values[idx]
            # This idx also is used to loop through the querry results
            assert isclose(res[idx], OBS_STATS_1.loc[val, col])

    for col in OBS_BIT_COLS:
        cur.execute(dml_test.get_bit_stats.format(col, 1, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_1)):
            val = OBS_STATS_1.index.values[idx]
            assert isclose(res[idx], OBS_STATS_1.loc[val, col])

    # ------------------------------------------------------------------------
    # File 2
    for tdms_idx in range(len(test_tdms_obj[1].object("Data", "Idx").data)):
        assert sqldb._add_obs_info(cur, test_tdms_obj[1], 2, tdms_idx)

    for col in OBS_COLS:
        cur.execute(dml_test.get_stats_test_id.format(col, 2, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_2)):
            val = OBS_STATS_2.index.values[idx]
            assert isclose(res[idx], OBS_STATS_2.loc[val, col])

    for col in OBS_BIT_COLS:
        cur.execute(dml_test.get_bit_stats.format(col, 2, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_2)):
            val = OBS_STATS_2.index.values[idx]
            assert isclose(res[idx], OBS_STATS_2.loc[val, col])

    # ------------------------------------------------------------------------
    # File 3
    for tdms_idx in range(len(test_tdms_obj[2].object("Data", "Idx").data)):
        assert sqldb._add_obs_info(cur, test_tdms_obj[2], 3, tdms_idx)

    for col in OBS_COLS[:-1]:
        cur.execute(dml_test.get_stats_test_id.format(col, 3, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_3)):
            val = OBS_STATS_3.index.values[idx]
            assert isclose(res[idx], OBS_STATS_3.loc[val, col])

    for col in OBS_BIT_COLS:
        cur.execute(dml_test.get_bit_stats.format(col, 3, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_3)):
            val = OBS_STATS_3.index.values[idx]
            assert isclose(res[idx], OBS_STATS_3.loc[val, col])

    # ------------------------------------------------------------------------
    # File 4
    for tdms_idx in range(len(test_tdms_obj[3].object("Data", "Idx").data)):
        assert sqldb._add_obs_info(cur, test_tdms_obj[3], 4, tdms_idx)

    for col in OBS_COLS:
        cur.execute(dml_test.get_stats_test_id.format(col, 4, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_4)):
            val = OBS_STATS_4.index.values[idx]
            assert isclose(res[idx], OBS_STATS_4.loc[val, col])

    for col in OBS_BIT_COLS:
        cur.execute(dml_test.get_bit_stats.format(col, 4, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_4)):
            val = OBS_STATS_4.index.values[idx]
            assert isclose(res[idx], OBS_STATS_4.loc[val, col])


def test__add_temp_info(cur, test_tdms_obj):
    """Test _add_temp_info."""
    # ------------------------------------------------------------------------
    # File 1

    # Add temps with tdms_idx 7 and Idx 8
    assert sqldb._add_temp_info(cur, test_tdms_obj[0], 1,
                                TEST_INDEX, TEST_INDEX+1)
    cur.execute(dml.get_temp_obs.format(1, TEST_INDEX+1))
    # Now query these with the TestId and Idx
    res = [float(r[0]) for r in cur.fetchall()]
    assert res == TEMP_OBS_1

    # ------------------------------------------------------------------------
    # File 2
    assert sqldb._add_temp_info(cur, test_tdms_obj[1], 2,
                                TEST_INDEX, TEST_INDEX)
    cur.execute(dml.get_temp_obs.format(2, TEST_INDEX))
    res = [float(r[0]) for r in cur.fetchall()]
    assert res == TEMP_OBS_2

    # ------------------------------------------------------------------------
    # File 3
    assert sqldb._add_temp_info(cur, test_tdms_obj[2], 3,
                                TEST_INDEX, TEST_INDEX+1)
    cur.execute(dml.get_temp_obs.format(3, TEST_INDEX+1))
    res = [float(r[0]) for r in cur.fetchall()]
    assert res == TEMP_OBS_3

    # ------------------------------------------------------------------------
    # File 4
    assert sqldb._add_temp_info(cur, test_tdms_obj[3], 4,
                                TEST_INDEX, TEST_INDEX+1)
    cur.execute(dml.get_temp_obs.format(4, TEST_INDEX+1))
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
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # File 1
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[0])

    # Verify the data in the 'Setting' table:
    cur.execute(dml_test.get_setting.format(1))
    assert cur.fetchall() == TDMS_01_ADD_SETTING

    # Verify the data in the 'Test' table:
    cur.execute(dml_test.get_test.format(1))
    assert cur.fetchall() == TDMS_01_ADD_TEST

    # Verify the data in the 'Observation' table
    for col in OBS_COLS[:-1]:
        cur.execute(dml_test.get_stats_test_id.format(col, 1, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_1)):
            val = OBS_STATS_1.index.values[idx]
            assert isclose(res[idx], OBS_STATS_1.loc[val, col])
    for col in OBS_BIT_COLS:
        cur.execute(dml_test.get_bit_stats.format(col, 1, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_1)):
            val = OBS_STATS_1.index.values[idx]
            assert isclose(res[idx], OBS_STATS_1.loc[val, col])

    # Verify the data in the 'TempObservation' table
    for col in TEMP_OBS_STATS_1.columns.values:
        cur.execute(
            dml_test.get_stats_test_id.format(col, 1, 'TempObservation')
            )
        res = cur.fetchall()[0]
        for idx in range(len(TEMP_OBS_STATS_1)):
            val = TEMP_OBS_STATS_1.index.values[idx]
            assert isclose(res[idx], TEMP_OBS_STATS_1.loc[val, col])

    # Commit transaction before next test
    assert cnx.in_transaction
    cnx.commit()
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # File 2
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[1])

    # Verify the data in the 'Setting' table:
    cur.execute(dml_test.get_setting.format(2))
    assert cur.fetchall() == TDMS_02_ADD_SETTING

    # Verify the data in the 'Test' table:
    cur.execute(dml_test.get_test.format(2))
    assert cur.fetchall() == TDMS_02_ADD_TEST

    # Verify the data in the 'Observation' table
    for col in OBS_COLS:
        cur.execute(dml_test.get_stats_test_id.format(col, 2, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_2)):
            val = OBS_STATS_2.index.values[idx]
            assert isclose(res[idx], OBS_STATS_2.loc[val, col])
    for col in OBS_BIT_COLS:
        cur.execute(dml_test.get_bit_stats.format(col, 2, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_2)):
            val = OBS_STATS_2.index.values[idx]
            assert isclose(res[idx], OBS_STATS_2.loc[val, col])

    # Verify the data in the 'TempObservation' table
    for col in TEMP_OBS_STATS_2.columns.values:
        cur.execute(
            dml_test.get_stats_test_id.format(col, 2, 'TempObservation')
            )
        res = cur.fetchall()[0]
        for idx in range(len(TEMP_OBS_STATS_2)):
            val = TEMP_OBS_STATS_2.index.values[idx]
            assert isclose(res[idx], TEMP_OBS_STATS_2.loc[val, col])

    # Commit transaction before next test
    assert cnx.in_transaction
    cnx.commit()
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # File 3
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[2])

    # Verify the data in the 'Setting' table:
    cur.execute(dml_test.get_setting.format(3))
    assert cur.fetchall() == TDMS_03_ADD_SETTING

    # Verify the data in the 'Test' table:
    cur.execute(dml_test.get_test.format(3))
    assert cur.fetchall() == TDMS_03_ADD_TEST

    # Verify the data in the `Observation` table:
    for col in OBS_COLS[:-1]:
        cur.execute(dml_test.get_stats_test_id.format(col, 3, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_3)):
            val = OBS_STATS_3.index.values[idx]
            assert isclose(res[idx], OBS_STATS_3.loc[val, col])
    for col in OBS_BIT_COLS:
        cur.execute(dml_test.get_bit_stats.format(col, 3, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_3)):
            val = OBS_STATS_3.index.values[idx]
            assert isclose(res[idx], OBS_STATS_3.loc[val, col])

    # Verify the data in the 'TempObservation' table
    for col in TEMP_OBS_STATS_3.columns.values:
        cur.execute(
            dml_test.get_stats_test_id.format(col, 3, 'TempObservation')
            )
        res = cur.fetchall()[0]
        for idx in range(len(TEMP_OBS_STATS_3)):
            val = TEMP_OBS_STATS_3.index.values[idx]
            assert isclose(res[idx], TEMP_OBS_STATS_3.loc[val, col])

    # Commit transaction before next test
    assert cnx.in_transaction
    cnx.commit()
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # File 4
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[3])

    # Verify the data in the 'Setting' table:
    cur.execute(dml_test.get_setting.format(4))
    assert cur.fetchall() == TDMS_04_ADD_SETTING

    # Verify the data in the 'Test' table:
    cur.execute(dml_test.get_test.format(4))
    assert cur.fetchall() == TDMS_04_ADD_TEST

    # Verify the data in the `Observation` table:
    for col in OBS_COLS[:-1]:
        cur.execute(dml_test.get_stats_test_id.format(col, 4, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_4)):
            val = OBS_STATS_4.index.values[idx]
            assert isclose(res[idx], OBS_STATS_4.loc[val, col])
    for col in OBS_BIT_COLS:
        cur.execute(dml_test.get_bit_stats.format(col, 4, 'Observation'))
        res = cur.fetchall()[0]
        for idx in range(len(OBS_STATS_4)):
            val = OBS_STATS_4.index.values[idx]
            assert isclose(res[idx], OBS_STATS_4.loc[val, col])

    # Verify the data in the 'TempObservation' table
    for col in TEMP_OBS_STATS_4.columns.values:
        cur.execute(
            dml_test.get_stats_test_id.format(col, 4, 'TempObservation')
            )
        res = cur.fetchall()[0]
        for idx in range(len(TEMP_OBS_STATS_4)):
            val = TEMP_OBS_STATS_4.index.values[idx]
            assert isclose(res[idx], TEMP_OBS_STATS_4.loc[val, col])

    # Commit transaction before next test
    assert cnx.in_transaction
    cnx.commit()
    assert not cnx.in_transaction

    # ------------------------------------------------------------------------
    # Test adding file 4 again
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[3]) is None


def test__get_test_dict(cnx):
    """
    Test get_test_df.

    Test resultant `DataFrame` accuracy and structure.
    """
    test_dict = sqldb._get_test_dict(cnx, 1)
    assert pd.testing.assert_frame_equal(test_dict['info'],
                                         TEST_1_INFO_DF) is None
    assert test_dict['data'].shape == TEST_1_DATA_DF_SIZE
    assert test_dict['data']['Idx'].iloc[3] == 5
    assert test_dict['data']['OptidewOk'].iloc[3] == 1
    assert test_dict['data']['CapManOk'].iloc[17] == 1

    for col in TEST_1_STATS_DF.keys():
        assert isclose(test_dict['data'][col].sum(),
                       TEST_1_STATS_DF.loc['sum', col])
        assert isclose(test_dict['data'][col].mean(),
                       TEST_1_STATS_DF.loc['mean', col])
        assert isclose(test_dict['data'][col].min(),
                       TEST_1_STATS_DF.loc['min', col])
        assert isclose(test_dict['data'][col].max(),
                       TEST_1_STATS_DF.loc['max', col])
        assert isclose(test_dict['data'][col].var(),
                       TEST_1_STATS_DF.loc['var', col])


def test_get_test_from_set(cur):
    """
    Test get_test_test_from_set.

    Test the accuracy of returned TestId lists.
    """
    assert sqldb.get_test_from_set(cur, TDMS_01_SETTING) == [1]
    assert sqldb.get_test_from_set(cur, TDMS_02_SETTING) == [2]
    assert sqldb.get_test_from_set(cur, TDMS_03_SETTING) == [3]
    assert sqldb.get_test_from_set(cur, TDMS_04_SETTING) == [4]
    assert sqldb.get_test_from_set(cur, FALSE_SETTING) is False


def test__add_rh_targets(results_cnx):
    """
    Test add_rh_targets.

    Test the ability to input analysis data into the RHTargets table.
    """
    results_cur = results_cnx.cursor()
    assert sqldb._add_rh_targets(results_cur, ANALYSIS_DF, ANALYSIS_TEST_ID)
    results_cur.execute('SELECT * FROM RHTargets;')
    res = results_cur.fetchall()
    assert len(res) == RH_TARGET_LENGTH
    for idx in range(RH_TARGET_LENGTH):
        assert res[idx][0] == RH_TARGET_LIST[idx]
        assert res[idx][1] == ANALYSIS_TEST_ID
    results_cur.close()


def test__add_results(results_cnx):
    """
    Test add_results.

    Test the ability to input analysis data into the Results table.
    """
    results_cur = results_cnx.cursor()
    assert sqldb._add_results(results_cur, ANALYSIS_DF, ANALYSIS_TEST_ID)

    results_cur.execute(('SELECT * FROM Results WHERE TestId={} AND RH=0.50'
                         ' AND Nu=599').format(ANALYSIS_TEST_ID))
    res = results_cur.fetchall()
    for idx in range(len(res)):
        assert isclose(float(res[idx][0]), float(RESULTS_LIST[idx]))

    for col in RESULTS_STATS_DF.columns.values:
        results_cur.execute(
            dml_test.get_stats_test_id.format(col, ANALYSIS_TEST_ID, 'Results')
            )
        res = results_cur.fetchall()[0]
        for idx in range(len(RESULTS_STATS_DF)):
            val = RESULTS_STATS_DF.index.values[idx]
            assert isclose(res[idx], RESULTS_STATS_DF.loc[val, col])
    results_cur.close()


def test__add_best_fit(results_cnx):
    """Test _add_best_fit."""
    results_cur = results_cnx.cursor()
    # Add best Chi2 results to RHTargets
    assert sqldb._add_best_fit(results_cur, ANALYSIS_TEST_ID)

    # Check accuracy of added data
    for col in BEST_FIT_STATS_DF.columns.values:
        res = results_cur.execute(dml_test.get_stats_test_id.format(
            col, ANALYSIS_TEST_ID, 'RHTargets'))
        res = results_cur.fetchall()[0]
        for idx in range(len(BEST_FIT_STATS_DF)):
            val = BEST_FIT_STATS_DF.index.values[idx]
            assert isclose(res[idx], BEST_FIT_STATS_DF.loc[val, col])
    results_cur.close()


def test_add_analysis(results_cnx):
    """
    Test add_analysis.

    Test the ability to pull, analyze, and insert data into the MySql database.
    """
    # ------------------------------------------------------------------------
    # Clear all of the previous work we have done in the database
    results_cur = results_cnx.cursor()
    clear_results(results_cur, True)
    assert not results_cnx.in_transaction

    assert sqldb.add_analysis(results_cnx, ANALYSIS_TEST_ID)

    # ------------------------------------------------------------------------
    # Test correct RHTargets input
    results_cur.execute('SELECT * FROM RHTargets;')
    res = results_cur.fetchall()
    assert len(res) == RH_TARGET_LENGTH
    for idx in range(RH_TARGET_LENGTH):
        assert res[idx][0] == RH_TARGET_LIST[idx]
        assert res[idx][1] == ANALYSIS_TEST_ID

    # ------------------------------------------------------------------------
    # Test correct Results input
    results_cur.execute(('SELECT * FROM Results WHERE TestId={} AND RH=0.50'
                         ' AND Nu=599').format(ANALYSIS_TEST_ID))
    res = results_cur.fetchall()
    for idx in range(len(res)):
        assert isclose(float(res[idx][0]), float(RESULTS_LIST[idx]))

    for col in RESULTS_STATS_DF.columns.values:
        results_cur.execute(
            dml_test.get_stats_test_id.format(col, ANALYSIS_TEST_ID, 'Results')
            )
        res = results_cur.fetchall()[0]
        for idx in range(len(RESULTS_STATS_DF)):
            val = RESULTS_STATS_DF.index.values[idx]
            assert isclose(res[idx], RESULTS_STATS_DF.loc[val, col])

    # ------------------------------------------------------------------------
    # Test adding the same analysis again
    assert sqldb.add_analysis(results_cnx, ANALYSIS_TEST_ID) is None

    # ------------------------------------------------------------------------
    # Check that the database is uneffected
    for col in RESULTS_STATS_DF.columns.values:
        results_cur.execute(
            dml_test.get_stats_test_id.format(col, ANALYSIS_TEST_ID, 'Results')
            )
        res = results_cur.fetchall()[0]
        for idx in range(len(RESULTS_STATS_DF)):
            val = RESULTS_STATS_DF.index.values[idx]
            assert isclose(res[idx], RESULTS_STATS_DF.loc[val, col])
    results_cur.close()


def drop_tables(cursor, bol):
    """Drop databese tables."""
    if bol:
        print("Dropping tables...")
        cursor.execute("DROP TABLE IF EXISTS " +
                       ", ".join(ddl.table_name_list) +
                       ";")
    else:
        print('Tables not dropped.')


def clear_results(cursor, bol):
    """Drop databese tables."""
    if bol:
        print('Clearing analysis tables...')
        truncate(cursor, 'RHTargets')
        truncate(cursor, 'Results')
        print('Analysis tables cleared.')
    else:
        print('RHTargests and Results not cleared.')


def truncate(cursor, table):
    """Truncate tables."""
    cursor.execute('SET FOREIGN_KEY_CHECKS=0')
    cursor.execute('TRUNCATE {}'.format(table))
    cursor.execute('SET FOREIGN_KEY_CHECKS=1')
