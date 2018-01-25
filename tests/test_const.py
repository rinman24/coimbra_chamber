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

CORRECT_FILE_LIST_WIN = [getcwd() + "/tests/data_transfer_test_files\\"
                                "test_01.tdms",
                     getcwd() + "/tests/data_transfer_test_files\\"
                                "tdms_test_folder\\"
                                "test_02.tdms",                     
                     getcwd() + "/tests/data_transfer_test_files\\"
                                "tdms_test_folder\\tdms_test_folder_full\\"
                                "test_04.tdms",
                     getcwd() + "/tests/data_transfer_test_files\\"
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

INCORRECT_FILE_LIST_WIN = [getcwd() + "/tests/data_transfer_test_files\\"
                                  "test_01.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files\\"
                                  "test_03.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files\\"
                                  "tdms_test_folder\\"
                                  "test_02.tdms_index",
                       getcwd() + "/tests/data_transfer_test_files\\"
                                  "tdms_test_folder\\tdms_test_folder_full\\"
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
MOD_SET_01 = dict(L_t=0.03, P=99950, T_DP=288, T_e=295)
MOD_SET_02 = dict(L_t=0.03, P=99950, T_DP=288, T_e=295, eps=[1, 0.95, 1])
MOD_SET_03 = dict(L_t=0.03, P=99950, T_DP=288, T_e=295, eps=[1, 0.95, 0.5])
MOD_SET_04 = dict(L_t=0.03, P=99950, T_DP=288, T_e=295,
                  alpha_w=[0.82, 0.74, 0.73], lamb=[3.58, 4.03, 4.30])

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
         'alpha_m:\t2.1316e-05\t[m^2 / s]\n'
         'beta_m:\t\t0.00341006\t[1 / K]\n'
         'beta*_m:\t0.603386\t[-]\n'
         'c_pm:\t\t1028.98\t\t[J / kg]\n'
         'c_p1:\t\t1902.17\t\t[J / kg]\n'
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

RAD_PROPS = ('--- Rad. Props. ---\n'
             'eps_1:\t1\t[-]\n'
             'eps_2:\t1\t[-]\n'
             'eps_3:\t1\t[-]\n')

REF_STATE = ('-------- Ref. State --------\n'
             'm_1:\t0.0119577\t[-]\n'
             'T_m:\t293.25\t\t[K]\n'
             'x_1:\t0.0190866\t[-]\n')

PARAMS = ('-------- Parameters --------\n'
          'Gr_h:\t-13406.1\t[-]\n'
          'Gr_mt:\t1810.19\t\t[-]\n'
          'Ja_v:\t0.00270917\t[-]\n'
          'Le:\t1.17789\t\t[-]\n'
          'Pr:\t0.720278\t[-]\n'
          'Ra:\t-8352.27\t[-]\n'
          'Ra_h:\t-9656.11\t[-]\n'
          'Ra_mt:\t1303.84\t\t[-]\n')

SOLUTION_01 = ('------------- Solution -------------\n'
               'mddp:\t1.65264e-06\t[kg / m^2 s]\n'
               'q_cs:\t-4.06602\t[W / m^2]\n'
               'T_s:\t290.276\t\t[K]\n')

SOLUTION_02 = ('------------- Solution -------------\n'
               'mddp:\t4.31355e-06\t[kg / m^2 s]\n'
               'q_cs:\t-1.37755\t[W / m^2]\n'
               'q_rad:\t-9.20321\t[W / m^2]\n'
               'T_s:\t293.407\t\t[K]\n')
