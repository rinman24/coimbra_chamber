"""Constants for the UCSD Chamber Experiment."""
from datetime import datetime
import os


# Constants for test_sqldb.py
TEST_DIRECTORY = os.path.join(os.getcwd(), 'tests', 'data_transfer_test_files')

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

INCORRECT_FILE_LIST = [os.path.join(os.getcwd(), 'tests',
                                                 'data_transfer_test_files',
                                                 'test_01.tdms_index'),
                       os.path.join(os.getcwd(), 'tests',
                                                 'data_transfer_test_files',
                                                 'test_03.tdms_index'),
                       os.path.join(os.getcwd(), 'tests',
                                                 'data_transfer_test_files',
                                                 'tdms_test_folder',
                                                 'test_02.tdms_index'),
                       os.path.join(os.getcwd(), 'tests',
                                                 'data_transfer_test_files',
                                                 'tdms_test_folder',
                                                 'tdms_test_folder_full',
                                                 'test_04.tdms_index')]

TDMS_01_SETTING = {'Duty': '5.0',
                   'Pressure': 100000,
                   'Temperature': 285}

TDMS_02_SETTING = {'Duty': '0.0',
                   'Pressure': 100000,
                   'Temperature': 280}

TDMS_03_SETTING = {'Duty': '5.0',
                   'Pressure': 100000,
                   'Temperature': 280}


TDMS_01_ADD_TEST = [(1, 'author_01', datetime(2018, 1, 29, 17, 54, 12),
                     'description_01', 1, 1.00, 1, 1)]

TDMS_02_ADD_TEST = [(2, 'author_02', datetime(2018, 1, 29, 17, 55, 10),
                     'description_02', 1, 1.00, 2, 1)]

TDMS_03_ADD_TEST = [(3, 'author_03', datetime(2018, 1, 29, 17, 50, 58),
                     'description_03', 0, 1.00, 3, 1)]

TDMS_04_ADD_TEST = [(4, 'author_04', datetime(2018, 1, 29, 17, 52, 24),
                     'description_04', 0, 1.00, 2, 1)]

GET_LAST_DEW_POINT = (
    'SELECT'
    '    DewPoint '
    'FROM'
    '    Observation '
    'WHERE'
    '    TestID={} '
    'ORDER BY Idx DESC '
    'LIMIT 1;')

GET_TEMP_OBS = ("SELECT"
                "    Temperature, ThermocoupleNum "
                "FROM"
                "    TempObservation "
                "WHERE"
                "    TestId={} "
                "AND"
                "    Idx={} "
                "ORDER BY ThermocoupleNum ASC;")

GET_OBS_DATA_M = ("SELECT"
                  "    CapManOk, DewPoint, Mass,"
                  "    OptidewOk, PowOut, PowRef, Pressure "
                  "FROM"
                  "    Observation "
                  "WHERE"
                  "    TestId={} "
                  "AND"
                  "    Idx ={};")

GET_OBS_DATA_T = ("SELECT"
                  "    CapManOk, DewPoint, OptidewOk,"
                  "    PowOut, PowRef, Pressure "
                  "FROM"
                  "    Observation "
                  "WHERE"
                  "    TestId={} "
                  "AND"
                  "    Idx ={};")

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

# Constants for test_results.py
NORM_TEST = [1, 3, 5, 4, 7]
NORM_TEST_RESULT = [0, 1 / 3, 2 / 3, 1 / 2, 1]

# Constants for test_models.py
MOD_SET_01 = dict(L_t=0.03, P=99950, T_DP=288, T_e=295)
MOD_SET_01_RH = dict(L_t=0.03, P=99950, RH=0.6444402431157594, T_e=295)
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

SOLUTION_03 = ('------------- Solution -------------\n'
               'mddp:\t1.65893e-06\t[kg / m^2 s]\n'
               'T_s:\t290.258\t\t[K]\n')

SOLUTION_04 = ('------------- Solution -------------\n'
               'mddp:\t4.36207e-06\t[kg / m^2 s]\n'
               'q_rs:\t9.30681\t[W / m^2]\n'
               'T_s:\t293.389\t\t[K]\n')

SOLUTION_05 = ('------------- Solution -------------\n'
               'mddp:\t4.36519e-06\t[kg / m^2 s]\n'
               'q_cu:\t0.0293693\t[W / m^2]\n'
               'q_rs:\t9.28791\t[W / m^2]\n'
               'T_s:\t293.392\t\t[K]\n')
