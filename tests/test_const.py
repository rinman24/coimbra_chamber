"""Constants for the UCSD Chamber Experiment."""
from datetime import datetime
from os import getcwd

import pytz

# Constants for test_sqldb.py
SETTINGS_TEST_1 = {'IsMass': 1,
                   'InitialDewPoint': 100,
                   'InitialDuty': 100,
                   'InitialMass': 0.07,
                   'InitialPressure': 100000,
                   'InitialTemp': 290,
                   'TimeStep': 1}

SETTINGS_TEST_2 = {'IsMass': 1,
                   'InitialDewPoint': 500,
                   'InitialDuty': 1000,
                   'InitialMass': 20,
                   'InitialPressure': 8,
                   'InitialTemp': 400,
                   'TimeStep': 20}

SETTINGS_TEST_3 = {'IsMass': 0,
                   'InitialDewPoint': 100,
                   'InitialDuty': 100,
                   'InitialPressure': 100000,
                   'InitialTemp': 290,
                   'TimeStep': 1}


TEST_DIRECTORY = getcwd() + "/tests/data_transfer_test_files"

CORRECT_FILE_LIST = [getcwd() + "/tests/data_transfer_test_files/"
                                "ismass_test_0_01.tdms",
                     getcwd() + "/tests/data_transfer_test_files/"
                                "ismass_test_1_02.tdms",
                     getcwd() + "/tests/data_transfer_test_files/"
                                "tdms_test_folder/ismass_test_1_04.tdms",
                     getcwd() + "/tests/data_transfer_test_files/"
                                "tdms_test_folder/tdms_test_folder_full/"
                                "ismass_test_0_03.tdms"]

INCORRECT_FILE_LIST = [getcwd() + "/tests/data_transfer_test_files/"
                                  "py.tdmstest",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "ismass_test_0_01.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "ismass_test_1_02.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "tdms_test_folder/"
                                  "ismass_test_1_04.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files/"
                                  "tdms_test_folder/tdms_test_folder_full/"
                                  "ismass_test_0_03.tdms_index"]

TDMS_TEST_FILE_MF = getcwd() + ("/tests/data_transfer_test_files/"
                                "ismass_test_0_01.tdms")

TDMS_TEST_FILE_MF_SETTING = {'IsMass': 0,
                             'InitialDewPoint': '289.70',
                             'InitialDuty': '0.0',
                             'InitialPressure': 99649,
                             'InitialTemp': '296.57',
                             'TimeStep': '1.00'}

TDMS_TEST_FILE_MF_TESTS = {'Author': "ADL",
                           'DateTime':
                           datetime(2017, 9, 11, 21, 25, 55, 23629, pytz.UTC),
                           'Description':
                           ("This is the Stefan Tube on the balance with no "
                            "water in it and the thermocouples disconnected. "
                            "The point of this study is to determine if the "
                            "tube is stable with the thermocouple ports on "
                            "without the thermocouple wires conected.")}

TDMS_TEST_FILE_MF_OBS_09 = {'CapManOk': 1,
                            'DewPoint': '289.71',
                            'Duty': '0.0',
                            'Idx': 9,
                            'OptidewOk': 1,
                            'PowOut': '-0.0013',
                            'PowRef': '-0.0016',
                            'Pressure': 99684}

TDMS_TEST_FILE_MF_THM_07 = '296.60'

TDMS_TEST_FILE_MT = getcwd() + ("/tests/data_transfer_test_files/"
                                "ismass_test_1_02.tdms")

TDMS_TEST_FILE_MT_SETTING = {'IsMass': 1,
                             'InitialDewPoint': '289.73',
                             'InitialDuty': '0.0',
                             'InitialMass': '0.0874270',
                             'InitialPressure': 99662,
                             'InitialTemp': '296.57',
                             'TimeStep': '1.00'}

TDMS_TEST_FILE_MT_TESTS = {'Author': "ADL",
                           'DateTime':
                           datetime(2017, 9, 11, 21, 26, 59, 523318, pytz.UTC),
                           'Description':
                           ("This is the Stefan Tube on the balance with no "
                            "water in it and the thermocouples disconnected. "
                            "The point of this study is to determine if the "
                            "tube is stable with the thermocouple ports on "
                            "without the thermocouple wires conected.")}

TDMS_TEST_FILE_MT_OBS_09 = {'CapManOk': 1,
                            'DewPoint': '289.71',
                            'Duty': '0.0',
                            'Idx': 9,
                            'Mass': '0.0874270',
                            'OptidewOk': 1,
                            'PowOut': '-0.0013',
                            'PowRef': '-0.0015',
                            'Pressure': 99640}

TDMS_TEST_FILE_MT_THM_07 = '296.59'

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
       'D_12:\t\t2.5108e-05\n' +
       'h_fg:\t\t2.45742e+06\n' +
       'm_1e:\t\t0.0106234\n' +
       'm_1s:\t\t0.0132943\n' +
       'rho_m:\t\t1.17934')
