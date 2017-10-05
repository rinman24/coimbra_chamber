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
MOD_SET_01 = dict(L_t=0.03, P=99950, T_DP=288, T_e=295)
MOD_SET_02 = dict(L_t=0.03, P=99950, T_DP=288, T_e=295, eps=[1, 0.95, 1])

REPR = 'settings = dict(L_t=0.03, P=99950, T_DP=288, T_e=295)\n' + \
    "Model(settings, ref='Mills', rule='mean')"

STR = ('------ Settings ------\n'
       'L_t:\t0.03\t[m]\n'
       'P:\t99950\t[Pa]\n'
       'T_DP:\t288\t[K]\n'
       'T_e:\t295\t[K]\n'
       'ref:\tMills\t[-]\n'
       'rule:\tmean\t[-]\n')

PROPS = ('--------------- Properties ---------------\n'
         'alpha_m:\t2.1574e-05\t[m^2 / s]\n'
         'beta_m:\t\t0.00341006\t[1 / K]\n'
         'beta*_m:\t0.603386\t[-]\n'
         'c_pm:\t\t1016.67\t\t[J / kg]\n'
         'D_12:\t\t2.5108e-05\t[m^2 / s]\n'
         'h_fg:\t\t2.45742e+06\t[J / kg]\n'
         'k_m:\t\t0.0258673\t[W / m K]\n'
         'm_1e:\t\t0.0106234\t[-]\n'
         'm_1s:\t\t0.0132943\t[-]\n'
         'mu_m:\t\t1.81069e-05\t[kg / m s]\n'
         'nu_m:\t\t1.53535e-05\t[m^2 / s]\n'
         'rho_m:\t\t1.17934\t\t[kg / m^3]\n'
         'T_s:\t\t291.5\t\t[K]\n'
         'x_1e:\t\t0.0169704\t[-]\n'
         'x_1s:\t\t0.0212028\t[-]\n')

REF_STATE = ('-------- Ref. State --------\n'
             'm_1:\t0.0119577\t[-]\n'
             'T_m:\t293.25\t\t[K]\n'
             'x_1:\t0.0190866\t[-]\n')

PARAMS = ('---- Parameters ----\n'
          'Ra:\t-8252.4\t[-]\n')

SOLUTION_01 = ('------------- Solution -------------\n'
               'mddp:\t1.65264e-06\t[kg / m^2 s]\n'
               'q_cs:\t-4.06602\t[W / m^2]\n'
               'T_s:\t290.276\t\t[K]\n')
