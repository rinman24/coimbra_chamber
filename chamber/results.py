"""Docstring."""
import numpy as np
import os
from scipy import stats

from CoolProp.HumidAirProp import HAPropsSI
import mysql.connector as conn
from mysql.connector import errorcode

import chamber.const as const
# import const
import chamber.sqldb as sqldb
# import sqldb


def connect_sqldb_chamber():
    """Use sqldb.connect_sqldb() to a MySQL server.

    Returns
    -------
    cnx : MySQLConnection
        Returns the MySQL connection object"""
    cnx = sqldb.connect_sqldb("test_chamber")
    return cnx


def normalized_mass(cur, test_id):
    """Use a TestID to calculate and write the normalized mass for a given test.

    This function uses a MySql querry to calculate and write the normalized mass
    from the observation table to the results table in the chamber database.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.
        Note: TestID must be for a IsMass True test.
    """
    cur.execute(const.NORMALIZE_MASS.format(const.GET_TEST_ID_NM.format(test_id)))


def get_mass(cur, test_id):
    """Use a TestID to get the mass observations from a given test.

    This function searches the chamber database for the masses recorded for the
    given TestID.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.

    Returns
    -------
    mass : list of floats
        List of mass observations for the given TestID.
    """
    cur.execute(const.GET_MASS.format(test_id))
    mass = [float(mass[0]) for mass in cur.fetchall()]
    return mass


def get_dew_point(cur, test_id):
    """Use a TestID to get the dew point observations from a given test.

    This function searches the chamber database for the dew points recorded for
    the given TestID.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.

    Returns
    -------
    dew_point : list of floats
        List of dew point observations for the given TestID.
    """
    cur.execute(const.GET_DEW_POINT.format(test_id))
    dew_point = [float(dp[0]) for dp in cur.fetchall()]
    return dew_point


def get_pressure(cur, test_id):
    """Use a TestID to get the pressure observations from a given test.

    This function searches the chamber database for the pressures recorded for
    the given TestID.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.

    Returns
    -------
    pressure : list of floats
        List of pressure observations for the given TestID.
    """
    cur.execute(const.GET_PRESSURE.format(test_id))
    pressure = [float(pa[0]) for pa in cur.fetchall()]
    return pressure


def get_avg_temp(cur, test_id):
    """Use a TestID to get the average of each TempObservation from a given test.

    This function searches the chamber database for the average
    TempObservations recorded for the given TestID.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.

    Returns
    -------
    avg_temp : list of floats
        List of temperature observations averaged over the thermocouples each
        observation for the given TestID.
    """
    cur.execute(const.GET_AVG_TEMP.format(test_id))
    avg_temp = [float(temp[0]) for temp in cur.fetchall()]
    return avg_temp


def get_rel_hum(cur, test_id):
    """Get the relative humidity calcilated for observations in a given test.

    This finction uses the CoolProp module to calculate the realative humidity
    for each observation in the test mathcing the give TestID.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.

    Returns
    -------
    hum : list of floats
        List of relative humidity percentages for each observation in the given
        test.
    """
    hum = []
    cur.execute(const.GET_AVG_TPDP.format(test_id))
    avg_temp, pressure, dew_point = cur.fetchall()
    for idx in range(len(pressure)):
        hum.append(HAPropsSI('RH', 'P', pressure[idx],
                             'T', avg_temp[idx], 'D', dew_point[idx]))
    return hum


def normalize(vals):
    """Normalizes the argument list.

    Parameters
    ----------
    vals : list
        List of data that will be normalized.

    Returns
    -------
    norm_vals : np.array()
        Array of normalized values.
    """
    vals = np.array(vals)
    norm_vals = (vals-min(vals))/(max(vals)-min(vals))
    return norm_vals
