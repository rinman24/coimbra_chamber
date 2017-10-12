"""Constants for the UCSD Chamber Experiment."""
from datetime import datetime
from os import getcwd


# Constants for test_sqldb.py
SETTINGS_TEST_1 = {'Duty': 10,
                   'Pressure': 100000,
                   'Temperature': 300,
                   'IsSteady': 1}

SETTINGS_TEST_2 = {'Duty': 20,
                   'Pressure': 110000,
                   'Temperature': 270,
                   'IsSteady': 0}


TEST_DIRECTORY = getcwd() + "/tests/data_transfer_test_files"

CORRECT_FILE_LIST = [getcwd() + "/tests/data_transfer_test_files/"
                                "test_01.tdms",
                     getcwd() + "/tests/data_transfer_test_files/"
                                "tdms_test_folder/"
                                "test_02.tdms",                     
                     getcwd() + "/tests/data_transfer_test_files"
                                "/tdms_test_folder/tdms_test_folder_full/"
                                "test_04.tdms",
                     getcwd() + "/tests/data_transfer_test_files/"
                                "test_03.tdms"]

INCORRECT_FILE_LIST = [getcwd() + "/tests/data_transfer_test_files/"
                                  "test_01.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "test_03.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "tdms_test_folder/"
                                  "test_02.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "tdms_test_folder/tdms_test_folder_full/"
                                  "test_04.tdms_index"]


TDMS_FF_SETTING = {'Duty': '1.0',
                   'Pressure': 100000,
                   'Temperature': 300,
                   'IsSteady': 0}

TDMS_FT_SETTING = {'Duty': '2.0',
                   'Pressure': 100000,
                   'Temperature': 300,
                   'IsSteady': 1}

TDMS_TF_SETTING = {'Duty': '4.0',
                   'Pressure': 100000,
                   'Temperature': 300,
                   'IsSteady': 0}

TDMS_TT_SETTING = {'Duty': '3.0',
                   'Pressure': 100000,
                   'Temperature': 300,
                   'IsSteady': 1}

TDMS_FF_TEST = {'Author': 'TEST',
                'DateTime':
                    datetime(2017, 10, 2, 16, 23, 57),
                'Description': 'Description for test 1',
                'IsMass': 0,
                'TimeStep': 1}

TDMS_FT_TEST = {'Author': 'TEST',
                'DateTime':
                    datetime(2017, 10, 2, 16, 25, 4),
                'Description': 'Description for test 2',
                'IsMass': 0,
                'TimeStep': 1}

TDMS_TF_TEST = {'Author': 'TEST',
                'DateTime':
                    datetime(2017, 10, 2, 16, 27, 51),
                'Description': 'Description for test 4',
                'IsMass': 1,
                'TimeStep': 1}

TDMS_TT_TEST = {'Author': 'TEST',
                'DateTime':
                     datetime(2017, 10, 2, 16, 27, 3),
                'Description': 'Description for test 3',
                'IsMass': 1,
                'TimeStep': 1}

TEST_EXISTS_CONST = {'Author': 'TEST',
                     'DateTime':
                          datetime(2017, 11, 2, 15, 27, 3),
                     'Description': 'Description for test 3',
                     'IsMass': 1,
                     'TimeStep': 1}

TDMS_FF_ADD_TEST = [(1, 'TEST', datetime(2017, 10, 2, 16, 23, 57),
                     'Description for test 1', 0, 1.00, 1, 1)]

TDMS_FT_ADD_TEST = [(2, 'TEST', datetime(2017, 10, 2, 16, 25, 4),
                     'Description for test 2', 0, 1.00, 2, 1)]

TDMS_TF_ADD_TEST = [(3, 'TEST', datetime(2017, 10, 2, 16, 27, 51),
                     'Description for test 4', 1, 1.00, 3, 1)]

TDMS_TT_ADD_TEST = [(4, 'TEST', datetime(2017, 10, 2, 16, 27, 3),
                     'Description for test 3', 1, 1.00, 4, 1)]

TDMS_FF_OBS_07 = {'CapManOk': 1,
                  'DewPoint': '285.75',
                  'Idx': 7,
                  'OptidewOk': 1,
                  'PowOut': '0.0002',
                  'PowRef': '0.0004',
                  'Pressure': 99430}

TDMS_FT_OBS_07 = {'CapManOk': 1,
                  'DewPoint': '285.57',
                  'Idx': 7,
                  'OptidewOk': 1,
                  'PowOut': '-0.0003',
                  'PowRef': '0.0002',
                  'Pressure': 99426}

TDMS_TF_OBS_07 = {'CapManOk': 1,
                  'DewPoint': '286.59',
                  'Idx': 8,
                  'Mass': '0.0988093',
                  'OptidewOk': 1,
                  'PowOut': '0.0002',
                  'PowRef': '-0.0001',
                  'Pressure': 99465}

TDMS_TT_OBS_07 = {'CapManOk': 1,
                  'DewPoint': '285.82',
                  'Idx': 7,
                  'Mass': '0.0988097',
                  'OptidewOk': 1,
                  'PowOut': '-0.0003',
                  'PowRef': '-0.0001',
                  'Pressure': 99518}

TDMS_FF_THM_07 = '299.49'

TDMS_FT_THM_07 = '299.55'

TDMS_TF_THM_07 = '299.57'

TDMS_TT_THM_07 = '299.56'

TEST_INDEX = 7
TC_INDEX = 7

# Constants for test_results.py
NORM_TEST = [1, 3, 5, 4, 7]
NORM_TEST_RESULT = [0, 1 / 3, 2 / 3, 1 / 2, 1]

# Constants for test_models.py
SETTINGS = dict(length=0.03, pressure=99950, temp_dp=288, temp_e=295)

REPR = 'settings = dict(length=0.03, pressure=99950, temp_dp=288, \
temp_e=295)\n' + "Model(settings, ref='Mills', rule='mean')"

STR = ('--------- Settings ---------\n' +
       'Length:\t\t0.03\n' +
       'Pressure:\t99950\n' +
       'Reference:\tMills\n' +
       'Rule:\t\tmean\n' +
       'Temp_DP:\t288\n' +
       'Temp_e:\t\t295\n' +
       'Temp_s:\t\t291.5\n' +
       '-------- Properties --------\n' +
       'alpha_m:\t2.1574e-05\n' +
       'beta_m:\t\t0.00341006\n' +
       'beta_star_m:\t0.603386\n' +
       'cp_m:\t\t1016.67\n' +
       'D_12:\t\t2.5108e-05\n' +
       'h_fg:\t\t2.45742e+06\n' +
       'k_m:\t\t0.0258673\n' +
       'm_1e:\t\t0.0106234\n' +
       'm_1s:\t\t0.0132943\n' +
       'mu_m:\t\t1.81069e-05\n' +
       'nu_m:\t\t1.53535e-05\n' +
       'rho_m:\t\t1.17934\n' +
       '-------- Dim. Param --------\n' +
       'Ra:\t\t-8252.4')
