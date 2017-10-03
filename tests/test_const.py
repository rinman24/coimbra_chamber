"""Constants for the UCSD Chamber Experiment."""
from datetime import datetime
from os import getcwd


# Constants for test_sqldb.py
SETTINGS_TEST_1 = {'Duty': 10,
                   'Pressure': 100000,
                   'Temperature': 300}

SETTINGS_TEST_2 = {'Duty': 20,
                   'Pressure': 110000,
                   'Temperature': 270}


TEST_DIRECTORY = getcwd() + "/tests/data_transfer_test_files"

CORRECT_FILE_LIST = [getcwd() + "/tests/data_transfer_test_files"
                                "/tdms_test_folder/tdms_test_folder_full/"
                                "New_Test_Structure_1.tdms",
                     getcwd() + "/tests/data_transfer_test_files/"
                                "New_Test_Structure_2.tdms"]

INCORRECT_FILE_LIST = [getcwd() + "/tests/data_transfer_test_files/"
                                  "ismass_test_0_01.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "ismass_test_1_02.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "tdms_test_folder/"
                                  "ismass_test_1_04.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "tdms_test_folder/tdms_test_folder_full/"
                                  "ismass_test_0_03.tdms_index"]


TDMS_MT_SETTING = {'Duty': 10,
                   'Pressure': 100000,
                   'Temperature': 300}

TDMS_MF_SETTING = {'Duty': 20,
                   'Pressure': 100000,
                   'Temperature': 300}

TDMS_MT_TEST = {'Author': 'RHI',
                'DateTime':
                    datetime(2017, 9, 28, 15, 58, 7),
                'Description': 'Test description one.',
                'IsMass': 1,
                'TimeStep': 1}

TDMS_MF_TEST = {'Author': 'RHI',
                'DateTime':
                    datetime(2017, 9, 28, 16, 0, 52),
                'Description': 'Test description two.',
                'IsMass': 0,
                'TimeStep': 1}

TDMS_MT_ADD_TEST = [(1, 'RHI', datetime(2017, 9, 28, 15, 58, 7),
                     'Test description one.', 1, 1.00, 2, 1)]

TDMS_MF_ADD_TEST = [(2, 'RHI', datetime(2017, 9, 28, 16, 0, 52),
                     'Test description two.', 0, 1.00, 1, 1)]

TDMS_MT_OBS_07 = {'CapManOk': 1,
                  'DewPoint': '285.99',
                  'Idx': 7,
                  'Mass': '0.0000000',
                  'OptidewOk': 1,
                  'PowOut': '0.0003',
                  'PowRef': '-0.0008',
                  'Pressure': 99789}

TDMS_MF_OBS_07 = {'CapManOk': 1,
                  'DewPoint': '287.82',
                  'Idx': 7,
                  'OptidewOk': 1,
                  'PowOut': '0.0002',
                  'PowRef': '-0.0007',
                  'Pressure': 99846}

TDMS_MT_THM_07 = '299.77'

TDMS_MF_THM_07 = '299.70'

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
