"""Constants for the UCSD Chamber Experiment."""

from datetime import datetime
from decimal import Decimal
from math import log, sqrt

import pytz

# ZnSe port parameters (From Spec Sheet)
D_PORT = 2.286e-2 # 2.286 cm         [X]
R_PORT = 1.143e-2 # 1.143 cm         [X]
A_PORT = 4.104e-4 # 4.104 cm^2       [X]

# Beam Parameters
"""
The cross-sectional area of the beam is chosen to be half of the area of the ZnSe aperature. As a
result, the radius of the beam will be smaller by a factor of 1/sqrt(2).
LAM  : wavelength of radiation
W_0  : beam radius at laser head
POW  : total power transmitted by the beam
Z_0  : Rayleigh length at the laser head
W_COL: beam radius after collimation
D_B  : diamter of the beam after collimation
A_CB : cross-sectional area of the beam after collimation
"""
LAM = 10.59e-6 # 10.59 microns          [X]
W_0 = 0.9e-3 # 0.9 mm                   [X]
POW = 20 # 20 W                         [X]
Z_0 = 24.03e-2 # 24.03 cm               [X]
W_COL = 8.082e-3 # 8.082 mm             [X]
D_B = 1.616e-2 # 1.616 cm               [X]
A_CB = 2.052e-4 # 2.052 cm^2            [X]

# Stefan Tube Dimensions
D_IN_TUBE = 2.286e-2 # 2.286 cm         [X]
R_IN_TUBE = 1.143e-2 # 1.143 cm         [X]
A_C_TUBE = 4.104e-4 # 4.104 cm^2        [X]
D_OUT_TUBE = 3.4e-2 # 3.4 cm            [X]
R_OUT_TUBE = 1.7e-2 # 1.7 cm            [X]
H_IN_TUBE = 4.572e-2 # 4.572 cm         [X]
H_OUT_TUBE = 5.129e-2 # 5.129 cm        [X]
H_TUBE_BASE = 5.57e-3 # 5.57 mm         [X]

# Gaussian Beam Constants
HWHM_COEFF_W = sqrt(2*log(2))/2 # 0.589 [X]

# Liquid Water Optical Properties at 10.59 microns
K_ABS_10P6 = 8.218e4 # 82,180 m^{-1}    []
K_EXT_10P6 = 6.925e-2 # 0.06925         []
L_K_ABS = 1.22e-5 # 12 microns          []

# Liquid Water Thermal Properties
# (273.15 to 373.15 K)
K_L_COEFF = [-2.9064388, 2.692925e-2, -6.8256489e-05, 5.858084e-08]
C_L_COEFF = [1.1844879e+06, -2.1559968e+04, 1.6404218e+02, -6.6524994e-01, 1.5161227e-03,
             -1.8406899e-06, 9.2992482e-10]
RHO_L_COEFF = [-7.2156278e+04, 1.1366432e+03, -7.0513426e+00, 2.1835039e-02, -3.3746407e-05,
               2.0814924e-08]

# MySQL Constants
FIND_SETTING = ("SELECT SettingID FROM Setting WHERE "
                "    InitialDewPoint = %(InitialDewPoint)s AND"
                "    InitialDuty = %(InitialDuty)s AND"
                "    InitialMass = %(InitialMass)s AND"
                "    InitialPressure = %(InitialPressure)s AND"
                "    InitialTemp = %(InitialTemp)s AND"
                "    TimeStep = %(TimeStep)s;")

ADD_SETTING = ("INSERT INTO Setting "
               "(InitialDewPoint, InitialDuty, InitialMass, InitialPressure, InitialTemp, TimeStep)"
               " VALUES "
               "(%(InitialDewPoint)s, %(InitialDuty)s, %(InitialMass)s, %(InitialPressure)s, "
               "%(InitialTemp)s, %(TimeStep)s)")

ADD_TEST = ("INSERT INTO Test "
            "(Author, DateTime, Description, SettingID, TubeID)"
            " VALUES "
            "(%(Author)s, %(DateTime)s, %(Description)s, %(SettingID)s, %(TubeID)s)")

ADD_OBS = ("INSERT INTO Observation "
           "(CapManOk, DewPoint, Duty, Idx, Mass, OptidewOk, PowOut, PowRef, Pressure, TestID)"
           " VALUES "
           "(%(CapManOk)s, %(DewPoint)s, %(Duty)s, %(Idx)s, %(Mass)s, %(OptidewOk)s, %(PowOut)s,"
           " %(PowRef)s, %(Pressure)s, %(TestID)s)")

ADD_TEMP = ("INSERT INTO TempObservation "
            "(ObservationID, ThermocoupleNum, Temperature)"
            " VALUES "
            "(%s, %s, %s)")

# Testing MySQL
TABLES = [('UnitTest',
           "CREATE TABLE UnitTest ("
           "    UnitTestID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
           "    Number DECIMAL(5,2) NULL,"
           "    String VARCHAR(30) NULL,"
           "  PRIMARY KEY (`UnitTestID`)"
           ");")]

SETTINGS_TEST_1 = {'InitialDewPoint': 100,
                   'InitialDuty': 100,
                   'InitialMass': 0.07,
                   'InitialPressure': 100000,
                   'InitialTemp': 290,
                   'TimeStep': 1}

SETTINGS_TEST_2 = {'InitialDewPoint': 500,
                   'InitialDuty': 1000,
                   'InitialMass': 20,
                   'InitialPressure': 8,
                   'InitialTemp': 400,
                   'TimeStep': 20}

TDMS_01_SETTING = {'InitialDewPoint': '292.50',
                   'InitialDuty': '0.0',
                   'InitialMass': '-0.0658138',
                   'InitialPressure': 99977,
                   'InitialTemp': '297.09',
                   'TimeStep': '1.00'}

TDMS_TEST_FILES = ["tests/data_transfer_test_files/tdms_test_files/tdms_test_file_01.tdms",
                   "tests/data_transfer_test_files/tdms_test_files/tdms_test_file_02.tdms",
                   "tests/data_transfer_test_files/tdms_test_files/tdms_test_file_03.tdms"]

CORRECT_FILE_LIST = ["test.tdms", "unit_test_01.tdms", "unit_test_02.tdms", "unit_test_03.tdms"]

INCORRECT_FILE_LIST = ["py.tdmstest", "py.tdmstest.py", "unit_test_01.tdms_index",
                       "unit_test_02.tdms_index", "unit_test_03.tdms_index"]

TDMS_01_DICT_TESTS = {'Author': "ADL",
                      'DateTime': datetime(2017, 8, 3, 19, 33, 9, 217290, pytz.UTC),
                      'Description': ("This is at room temperature, pressure, no laser power, study"
                                      " of boundy development.")}

TDMS_01_OBS_08 = {'CapManOk': 1,
                  'DewPoint': '292.43',
                  'Duty': '0.0',
                  'Idx': 8,
                  'Mass': '-0.0658138',
                  'OptidewOk': 1,
                  'PowOut': '-0.0010',
                  'PowRef': '-0.0015',
                  'Pressure': 99982}

TEST_INDEX = 7

TDMS_01_THM_07 = '296.76'

TC_INDEX = 7

TEST_DIRECTORY = "tests/data_transfer_test_files/tdms_test_files/"
