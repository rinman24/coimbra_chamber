"""Docstring."""
import numpy as np
import os

import mysql.connector as conn
from mysql.connector import errorcode

#import chamber.const as const
import const
#import chamber.sqldb as sqldb
import sqldb

def connect_sqldb_chamber():
    """Use sqldb.connect_sqldb() to a MySQL server.

    Returns
    -------
    cnx : MySQLConnection
        Returns the MySQL connection object"""
    cnx = sqldb.connect_sqldb()
    return cnx

def connect_sqldb_results():
    """Use connect constructor to connect to a MySQL server.

    Uses environment variables MySqlUserName, MySqlCredentials, MySqlHost, and MySqlDataBase2 to
    connect to a MySQL server. If the environment variables are not already available use, execute
    the follwing command, for example, in the terminal:
    
    $ export MySqlUserName=user
    
    Returns
    -------
    cnx : MySQLConnection
        Returns the MySQL connection object
    """
    config = {'user': os.environ['MySqlUserName'],
              'password': os.environ['MySqlCredentials'],
              'host': os.environ['MySqlHost'],
              'database': os.environ['MySqlDataBase2']}
    try:
        cnx = conn.connect(**config)
    except conn.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return cnx


def create_views(cur_re, views):
    """Uses sqldb.create_tables to create tables in the database.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tables : list
        List of table names and DDL query language. For example:
        [('UnitTest',
        "CREATE TABLE UnitTest ("
        "    UnitTestID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
        "    Number DECIMAL(5,2) NULL,"
        "    String VARCHAR(30) NULL,"
        "  PRIMARY KEY (`UnitTestID`)"
        ");"))]
    """
    sqldb.create_tables(cur_re, views)

def normalized_mass(cur_ch, cur_re, test_id):
    """Use a TestID to calculate and write the normalized mass for a given test.

    This function searches the chamber database for the masses recorded for the given TestID.
    This function then calculates the normalized masses for the test and records the masses in the
    results database.

    Parameters
    ----------
    cur_ch : MySQLCursor
        Cursor used to interact with the chamber MySQL database.
    cur_re : MySQLCursor
        Cursor used to interact with the results MySQL database.
    test_id : int
        The TestID which normalized mass will be calculated and recorded for.
    """
    #cur_re.execute("SELECT TestID FROM NormalizedMass WHERE TestID = %s", test_id)
    cur_re.execute("SELECT TestID FROM NormalizedMass WHERE TestID={} LIMIT 1".format(test_id))
    if not cur_re.fetchall():
        cur_ch.execute("SELECT mass FROM Observation WHERE TestID={}".format(test_id))
        mass = [mass[0] for mass in cur_ch.fetchall()]
        mass = np.array(mass)
        norm_mass = (mass-min(mass))/(max(mass)-min(mass))
        nm_id = [(test_id, '{:.7f}'.format(round(mass, 7))) for mass in norm_mass]
        cur_re.executemany(const.ADD_NORM_MASS, nm_id)
