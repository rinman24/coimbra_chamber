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

from chamber.analysis import experiments
from chamber.data import sqldb, ddl, dml
import dml_test

config = configparser.ConfigParser()
config.read('config.ini')

# ----------------------------------------------------------------------------
# Test `create_tables` global variables
BAD_TABLE = [("Tube",
              "CREATE TABLE `Tube` ("
              "  `TubeId` TINYINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,"
              "  `DiameterIn` DECIMAL(7,7) UNSIGNED NOT NULL,"
              "  `DiameterOut` DECIMAL(7,7) UNSIGNED NOT NULL,"
              "  `Length` DECIMAL(4,4) UNSIGNED NOT NULL,"
              "  `Material` VARCHAR(50) NOT NULL,"
              "  `Mass` DECIMAL(7,7) UNSIGNED NOT NULL,"
              "  PRIMARY KEY (`TubeId`))"
              "  ENGINE = InnoDB"
              "  DEFAULT CHARACTER SET = latin1;")]

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
    CapManOk=[27, 27, 0, 1, 1, 1],
    DewPoint=[27, 7737.23, 0.000705624142660792, 286.564074, 286.52, 286.63],
    Idx=[27, 405, 60.666666666666664, 15.0000, 2, 28],
    Mass=[0, None, None, None, None, None],
    OptidewOk=[27, 27, 0, 1, 1, 1],
    PowOut=[27, 5.1e-3, 1.2839506172839506e-8, 1.8889e-4, -1e-4, 4e-4],
    PowRef=[27, -0.0009, 8.88888888888889e-9, -3.333e-5, -3e-4, 2e-4],
    Pressure=[27, 2698654, 235.01508916327026, 99950.1481, 99929, 99986],
    TestId=[27, 27, 0, 1, 1, 1],
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
    Pressure=[15, 1498957, 449.71555555555057, 99930.4667, 99907, 99982],
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
    Pressure=[13, 1299260, 91.30177514793556, 99943.0769, 99929, 99964],
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
    Pressure=[14, 1399006, 67.57142857140576, 99929, 99912, 99942],
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
    Temperature=[378, 110454.42, 0.5943596875787265,
                 292.207460, 291.52, 293.96],
    Idx=[378, 5670, 60.666666666666664, 15.0000, 2, 28],
    TestId=[378, 378, 0, 1.0000, 1, 1],
    )
).set_index('idx')
TEMP_OBS_STATS_2 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    ThermocoupleNum=[150, 1275, 8.25, 8.5000, 4, 13],
    Temperature=[150, 43780.64, 0.0796217955555548,
                 291.870933, 291.56, 292.43],
    Idx=[150, 1650, 18.666666666666675, 11.0000, 4, 18],
    TestId=[150, 300, 0, 2.0000, 2, 2],
    )
).set_index('idx')
TEMP_OBS_STATS_3 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    ThermocoupleNum=[182, 1183, 16.250000000000007, 6.5000, 0, 13],
    Temperature=[182, 53149.14, 0.301965040454052,
                 292.028242, 291.49, 293.09],
    Idx=[182, 1456, 13.999999999999982, 8.0000, 2, 14],
    TestId=[182, 546, 0, 3.0000, 3, 3],
    )
).set_index('idx')
TEMP_OBS_STATS_4 = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    ThermocoupleNum=[140, 1190, 8.25, 8.5000, 4, 13],
    Temperature=[140, 40850.13, 0.03772230102040992,
                 291.786643, 291.53, 292.14],
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
    TC0=[7929.219999999998, 293.67481481481474, 293.65, 293.71,
         3.336182336181693e-4],
    TC1=[7911.41, 293.0151851851852, 292.99, 293.04, 1.4900284900268648e-4],
    TC7=[7882.79, 291.9551851851852, 291.94, 291.98, 0.00011054131054147711],
    TC13=[7878.86000000000015, 291.8096296296297, 291.80, 291.81999999999999,
          2.6780626780578073e-05],
    Pressure=[2698654, 99950.1481, 99929, 99986, 244.05413105413103],
    PowOut=[0.0051, 0.00018888888888888883, -0.0001, 0.0004,
            1.3333333333333332e-08],
    PowRef=[-0.0009, -3.3333333333333335e-05, -0.0003, 0.0002,
            9.2307692307692321e-09],
    DewPoint=[7737.240000000001, 286.56444444444446, 286.52, 286.64,
              7.871794871791728e-4],
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
RH_TARGET_LIST = [Decimal('{:g}'.format(rh/100)) for rh in range(10, 85, 5)]
RH_ERR_LIST = [0.00192007,  0.0028022,  0.00362771,  0.00445247,  0.00527192,
               0.00607349,  0.00682977,  0.00761089,  0.00840709,  0.00913833,
               0.00894471,  0.00937274,  0.00998618,  0.0106339,  0.0112474]
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
    RH=[1099, 563.0, 0.03056339165143929, 0.512284,
        0.10000000000000001, 0.80000000000000004],
    TestId=[1099, 1099, 0, 1, 1, 1],
    A=[1099, 108.65434961020947, 2.9013655607597385e-10, 0.09886656015487667,
       0.09882460534572601, 0.09888922423124313],
    SigA=[1099, 2.8483969686021737e-05, 1.6791311969228083e-14,
          2.5918079787098944e-08, 5.754197673901729e-10,
          2.316897962373332e-06],
    B=[1099, -3.391460006607616e-06, 1.0181455109937529e-18,
       -3.0859508704345916e-09, -6.390378448628553e-09,
       -1.419641071365163e-09],
    SigB=[1099, 1.7167214310265938e-09, 3.639741584914378e-23,
          1.5620759154018142e-12, 4.898612101351084e-14,
          4.862525659898864e-11],
    Chi2=[1099, 3379617267.8442154, 42744441389327.21, 3075174.9479929167,
          97.25215148925781, 54769204.0],
    Q=[1099, 177.95, 0.13367083617251502,
       0.161920, 0.0, 1.00],
    Nu=[1099, 9691301, 32428017.330669552, 8818.2903, 199, 19999]
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test `_get_res_df` global variables
RES_DF_STATS = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    RH=[1099, 563.0, 0.030591227163, 0.512283894449, 0.1, 0.8],
    TestId=[1099, 1099, 0, 1, 1, 1],
    A=[1099, 108.654349, 2.90428639548e-10, 0.0988665595996, 0.0988246,
       0.0988892],
    SigA=[1099, 2.8483974018e-05, 1.68066219103e-14, 2.59180837288e-08,
          5.7542e-10, 2.3169e-06],
    B=[1099, -3.39146005e-06, 1.01907242991e-18, -3.08595090992e-09,
       -6.39038e-09, -1.41964e-09],
    SigB=[1099, 1.7167221368e-09, 3.64306158289e-23, 1.5620765576e-12,
          4.89861e-14, 4.86253e-11],
    Chi2=[1099, 3379617400.1, 4.278336427e+13, 3075175.06833, 97.2522,
          54769200.0],
    Q=[1099, 177.95, 0.13379257646, 0.161919927207, 0, 1],
    Nu=[1099, 9691301, 32457551.0441, 8818.29026388, 199, 19999]
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test `_add_best_fit` global variables
BEST_FIT_STATS_DF = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    RH=[15, 6.75, 0.04666666666666666, 0.450000, 0.10, 0.80],
    TestId=[15, 15, 0, 1, 1, 1],
    Nu=[15, 35585, 2111288.888888889, 2372.3333, 199, 5199],
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# `test_tdms_obj` fixture global variables
EVAP_DF = pd.DataFrame(dict(
  RH=[float(rh) for rh in RH_TARGET_LIST],
  SigRH=RH_ERR_LIST,
  B=[-6.10832e-9, -5.18407e-9, -4.70715e-9, -3.69006e-9, -4.39613e-9,
     -4.15584e-9, -3.69006e-9, -3.45441e-9, -3.17164e-9, -2.85822e-9,
     -2.58906e-9, -2.29717e-9, -1.99432e-9, -1.71475e-9, -1.44389e-9],
  SigB=[4.86253e-11, 1.72558e-11, 3.32917e-12, 2.64237e-12, 2.16304e-12,
        1.81293e-12, 1.54803e-12, 1.3419e-12, 1.17778e-12, 9.34719e-13,
        7.65107e-13, 6.41233e-13, 6.41233e-13, 3.91801e-13, 3.6942e-13]
  )
)[['RH', 'SigRH', 'B', 'SigB']]
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

# ----------------------------------------------------------------------------
# `test_get_rht_results` global variables


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


def test_connect():
        """Test connect."""
        cnx = sqldb.connect('test')
        assert isinstance(cnx, mysql.connector.connection.MySQLConnection)
        assert not cnx.in_transaction
        cnx.close()

        # Database does not exist
        sqldb.connect('fake_db')
        # with pytest.raises(mysql.connector.Error) as err:
        if not os.path.isfile('tests/data_test_files/config.ini'):
            config = configparser.ConfigParser()
            config.read('config.ini')
            host = config['MySQL-Server']['host']
            config['MySQL-Server'] = {
               'host': host,
               'user': 'user',
               'password': 'password'
            }
            with open('tests/data_test_files/config.ini', 'w') as configfile:
                config.write(configfile)
        assert os.path.isfile('tests/data_test_files/config.ini')
        move('config.ini', 'tests/config.ini')
        move('tests/data_test_files/config.ini', 'config.ini')
        sqldb.connect('test')
        move('config.ini', 'tests/data_test_files/config.ini')
        move('tests/config.ini', 'config.ini')


def test_create_tables(cur):
    """Test create_tables."""
    # Create the tables
    assert sqldb.create_tables(cur, ddl.tables)

    # Now check that all tables exist
    table_names_set = set(ddl.table_name_list)
    cur.execute('SHOW TABLES;')
    for row in cur:
        assert row[0] in table_names_set
    assert sqldb.create_tables(cur, BAD_TABLE)


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
    assert sqldb.add_tdms_file(cnx, test_tdms_obj[3]) is True


def test__get_test_dict(cnx):
    """
    Test get_test_df.

    Test resultant `DataFrame` accuracy and structure.
    """
    test_dict = sqldb._get_test_dict(cnx, 1)
    pd.testing.assert_frame_equal(test_dict['info'], TEST_1_INFO_DF)
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
        assert res[idx][1] == RH_ERR_LIST[idx]
        assert res[idx][2] == ANALYSIS_TEST_ID
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


def test__get_res_df(results_cnx):
    """Test _get_res_df."""
    res_df = sqldb._get_res_df(results_cnx, ANALYSIS_TEST_ID)
    for col in RES_DF_STATS.columns.values:
        # Have to lower tolerance due to rounding
        assert isclose(res_df[col].count(), RES_DF_STATS.loc['cnt', col])
        assert isclose(res_df[col].sum(), RES_DF_STATS.loc['sum', col])
        assert isclose(res_df[col].var(), RES_DF_STATS.loc['var', col])
        assert isclose(res_df[col].mean(), RES_DF_STATS.loc['avg', col])
        assert isclose(res_df[col].min(), RES_DF_STATS.loc['min', col])
        assert isclose(res_df[col].max(), RES_DF_STATS.loc['max', col])


def test__add_best_fit(results_cnx):
    """Test _add_best_fit."""
    results_cur = results_cnx.cursor()
    # Add best Chi2 results to RHTargets
    assert sqldb._add_best_fit(results_cnx, ANALYSIS_TEST_ID)

    # Check accuracy of added data
    for col in BEST_FIT_STATS_DF.columns.values:
        res = results_cur.execute(dml_test.get_stats_test_id.format(
            col, ANALYSIS_TEST_ID, 'RHTargets'))
        res = results_cur.fetchall()[0]
        for idx in range(len(BEST_FIT_STATS_DF)):
            val = BEST_FIT_STATS_DF.index.values[idx]
            assert isclose(res[idx], BEST_FIT_STATS_DF.loc[val, col])
    results_cur.close()


def test_get_high_low_testids(results_cnx):
    """Test get_high_low_testids."""
    results_cur = results_cnx.cursor()
    clear_results(results_cur, True)
    results_cur.execute(dml.add_rh_targets, [1, 0.35, 0.0002])
    assert sqldb.get_high_low_testids(results_cur, 40000, 280) == [1]
    results_cur.execute(dml.add_rh_targets, [2, 0.30, 0.0001])
    assert sqldb.get_high_low_testids(results_cur, 40000, 280) == [1, 2]
    clear_results(results_cur, True)
    assert sqldb.get_high_low_testids(results_cur, 40000, 280) == []


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

    assert sqldb.add_analysis(
        results_cnx, ANALYSIS_TEST_ID, steps=100)

    # ------------------------------------------------------------------------
    # Test correct RHTargets input
    results_cur.execute('SELECT * FROM RHTargets WHERE TestId=1;')
    res = results_cur.fetchall()
    assert len(res) == RH_TARGET_LENGTH
    for idx in range(RH_TARGET_LENGTH):
        assert res[idx][0] == RH_TARGET_LIST[idx]
        assert res[idx][1] == RH_ERR_LIST[idx]
        assert res[idx][2] == ANALYSIS_TEST_ID

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
    assert sqldb.add_analysis(
        results_cnx, ANALYSIS_TEST_ID, steps=100) is None

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


def test_get_rht_results(results_cnx):
    """Test get_rht_results."""
    res_df = sqldb.get_rht_results(results_cnx, 1)
    assert pd.testing.assert_frame_equal(
      res_df, EVAP_DF,  check_dtype=False) is None


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
