"""Constants for the UCSD Chamber Experiment."""
from datetime import datetime
from decimal import Decimal
from math import log, sqrt, pi
from os import getcwd


# Constants for laser.py
# ZnSe port parameters (From Spec Sheet)
D_PORT = 2.286e-2    # 2.286 cm
R_PORT = 1.143e-2    # 1.143 cm
A_PORT = 4.104e-4    # 4.104 cm^2

# Beam Parameters
"""
The cross-sectional area of the beam is chosen to be half of the area of the
ZnSe aperature. As a result, the radius of the beam will be smaller by a factor
of 1/sqrt(2).
LAM  : wavelength of radiation
W_0  : beam radius at laser head
POW  : total power transmitted by the beam
Z_0  : Rayleigh length at the laser head
W_COL: beam radius after collimation
D_B  : diamter of the beam after collimation
A_CB : cross-sectional area of the beam after collimation
"""
LAM = 10.59e-6      # 10.59 microns
W_0 = 0.9e-3        # 0.9 mm
POW = 20            # 20 W
Z_0 = 24.03e-2      # 24.03 cm
W_COL = 8.082e-3    # 8.082 mm
D_B = 1.616e-2      # 1.616 cm
A_CB = 2.052e-4     # 2.052 cm^2

# Stefan Tube Dimensions
D_IN_TUBE = 2.286e-2     # 2.286 cm
R_IN_TUBE = 1.143e-2     # 1.143 cm
A_C_TUBE = 4.104e-4      # 4.104 cm^2
D_OUT_TUBE = 3.4e-2      # 3.4 cm
R_OUT_TUBE = 1.7e-2      # 1.7 cm
H_IN_TUBE = 4.572e-2     # 4.572 cm
H_OUT_TUBE = 5.129e-2    # 5.129 cm
H_TUBE_BASE = 5.57e-3    # 5.57 mm

# Gaussian Beam Constants
HWHM_COEFF_W = sqrt(2 * log(2)) / 2    # 0.589


# CONSTANTS FOR water.py
# Liquid Water Optical Properties at 10.59 microns
K_ABS_10P6 = 8.218e4     # 82,180 m^{-1}
K_EXT_10P6 = 6.925e-2    # 0.06925
L_K_ABS = 1.22e-5        # 12 microns


# Molecular weights
M1 = 18.015
M2 = 28.964

# Gravitational acceleration
ACC_GRAV = 9.80665  # m/s^2

# CONSTANTS FOR sqldb.py
# MySQL querry Constants
ADD_SETTING = ("INSERT INTO Setting "
               "(Duty, Pressure, Temperature)"
               " VALUES "
               "(%(Duty)s, %(Pressure)s, %(Temperature)s)")

ADD_TEST = ("INSERT INTO Test "
            "(Author, DateTime, Description, IsMass, TimeStep,"
            " SettingID, TubeID)"
            " VALUES "
            "(%(Author)s, %(DateTime)s, %(Description)s, %(IsMass)s,"
            " %(TimeStep)s, %(SettingID)s, %(TubeID)s)")

ADD_OBS_M_T = ("INSERT INTO Observation "
               "(CapManOk, DewPoint, Idx, Mass, OptidewOk, PowOut, PowRef,"
               " Pressure, TestID)"
               " VALUES "
               "(%(CapManOk)s, %(DewPoint)s, %(Idx)s, %(Mass)s, %(OptidewOk)s,"
               " %(PowOut)s, %(PowRef)s, %(Pressure)s, %(TestId)s)")

ADD_OBS_M_F = ("INSERT INTO Observation "
               "(CapManOk, DewPoint, Idx, OptidewOk, PowOut, PowRef,"
               " Pressure, TestID)"
               " VALUES "
               "(%(CapManOk)s, %(DewPoint)s, %(Idx)s, %(OptidewOk)s,"
               " %(PowOut)s, %(PowRef)s, %(Pressure)s, %(TestId)s)")

ADD_TEMP = ("INSERT INTO TempObservation "
            "(ThermocoupleNum, Temperature, Idx, TestId)"
            " VALUES "
            "(%s, %s, %s, %s)")

ADD_TUBE = ("INSERT INTO Tube "
            "(DiameterIn, DiameterOut, Length, Material, Mass)"
            " VALUES "
            "(%(DiameterIn)s, %(DiameterOut)s, %(Length)s,"
            " %(Material)s, %(Mass)s)")

ADD_UNIT = ("INSERT INTO Unit "
            "(Duty, Length, Mass, Power, Pressure, Temperature, Time)"
            " VALUES "
            "(%(Duty)s, %(Length)s, %(Mass)s, %(Power)s, %(Pressure)s,"
            " %(Temperature)s, %(Time)s)")

FIND_SETTING = ("SELECT SettingID FROM Setting WHERE "
                "    Duty = %(Duty)s AND"
                "    Pressure = %(Pressure)s AND"
                "    Temperature = %(Temperature)s;")

FIND_TEST = ("SELECT TestID FROM Test WHERE "
             "    DateTime='{}'")

FIND_TUBE = ("SELECT TubeID FROM Tube WHERE "
             "    DiameterIn = %(DiameterIn)s AND"
             "    DiameterOut = %(DiameterOut)s AND"
             "    Length = %(Length)s AND"
             "    Material = %(Material)s AND"
             "    Mass = %(Mass)s")


# MySql Tube and Unit Constants
TUBE_DATA = {'DiameterIn': 0.03, 'DiameterOut': 0.04, 'Length': 0.06,
             'Material': 'Delrin', 'Mass': 0.0657957}

UNIT_DATA = {'Duty': 'Percent', 'Length': 'Meter', 'Mass': 'Kilogram',
             'Power': 'Watt', 'Pressure': 'Pascal', 'Temperature': 'Kelvin',
             'Time': 'Second'}


# Constants for views.py
# MySql Querries for views.py

ADD_NORM_MASS = ("INSERT INTO Results (NormalizedMass) SELECT"
                 " ROUND((Mass-(SELECT MIN(Mass) FROM Observation WHERE"
                 " TestID={0}))/(SELECT MAX(Mass)-MIN(Mass) FROM Observation"
                 " WHERE TestID={0}), 7) FROM Observation WHERE TestID={0};")

GET_TEST_ID_NM = "SELECT TestID FROM NormalizedMass WHERE TestID={} LIMIT 1"

GET_MASS = "SELECT Mass FROM Observation WHERE TestID={}"

GET_DEW_POINT = "SELECT DewPoint FROM Observation WHERE TestID={}"

GET_PRESSURE = "SELECT Pressure FROM Observation WHERE TestID={}"

GET_SUM_TEMP = ("SELECT SUM(Temperature) "
                "FROM TempObservation "
                "WHERE ObservationID={}")

GET_OBS_ID = "SELECT ObservationID FROM Observation WHERE TestID={}"

GET_AVG_TEMP = ("SELECT AVG(Temperature) "
                "FROM TempObservation AS Temp INNER JOIN Observation "
                "AS Obs ON Temp.ObservationID=Obs.ObservationID "
                "INNER JOIN Test ON Obs.TestID=Test.TestID "
                "WHERE Test.TestID={} GROUP BY Obs.ObservationID")

GET_AVG_TPDP = ("SELECT ("
                "SELECT ROUND(AVG(Temperature), 2) "
                "FROM TempObservation AS Temp"
                " INNER JOIN Observation AS Obs ON"
                " Temp.ObservationID=Obs.ObservationID WHERE Obs.TestID={0}"
                "), ROUND(AVG(Pressure)), ROUND(AVG(PowOut), 4), "
                "ROUND(AVG(DewPoint), 2) FROM"
                " Observation WHERE TestID={0};")

GET_TPDP = ("SELECT ("
            "SELECT ROUND(AVG(Temperature), 2) "
            "FROM TempObservation AS Temp "
            "INNER JOIN Observation AS Obs ON"
            " Temp.ObservationID=Obs.ObservationID WHERE Obs.TestID={0}"
            "), Pressure, DewPoint FROM"
            " Observation WHERE TestID={0};")

TUBE_RADIUS = 0.015    # [m]
TUBE_AREA = pi * pow(TUBE_RADIUS, 2)
TUBE_CIRCUM = 2 * pi * TUBE_RADIUS

# Radiative Properties
SIGMA = 5.670367e-8

C_2 = 1.4389e4  # [mu*m K]
