"""Docstring."""
import os
from re import compile

import mysql.connector as conn
from mysql.connector import errorcode
from nptdms import TdmsFile

def connect_sqldb():
    """Use connect constructor to connect to a MySQL server.

    Description: Uses environment variables MySqlUserName, MySqlCredentials, MySqlHost, and
    MySqlDataBase to connect to a MySQL server. The function returns both the connection object as well as the cursor object. If these variables are not already available use,
    for example, $ export MySqlUserName=user in the shell.
    """
    config = {'user': os.environ['MySqlUserName'],
              'password': os.environ['MySqlCredentials'],
              'host': os.environ['MySqlHost'],
              'database': os.environ['MySqlDataBase']}
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

def create_tables(cur, tables):
    """Use cur and a list of tuples of names and DDL queries to create tables in the database.

    Description: Uses a list of tuples where the 0 index is the name of the table and the 1 index is
    a string of MySQL DDL used to create the table. A list is required so that the DDL can be
    executed in order so that foreign key constraint errors do not occur.
    
    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tables -- list
    """
    for table in tables:
        name, ddl = table
        try:
            #print("\tCreating table {}: ".format(name), end='')
            cur.execute(ddl)
        except conn.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

def insert_dml(table, row_data):
    """Use a table name and dictionay to return a MySQL insert DML query.

    Description: Use the name of the table and a dictionary called row_data, where the keys are
    attribute names and the values are row data, to build and return a MySQL DML INSERT query.
    Please note that all the values in the row_data dictionary should be string types.

    Positional arguments:
    table -- string
    row_data -- dict of strings
    """
    query = (
        "INSERT INTO " + table + " "
        "    (" + ', '.join(row_data.keys()) + ")"
        "  VALUES"
        "    ('" + "', '".join(row_data.values()) + "');")
    return query

def last_insert_id(cur):
    """Use the last SELECT LAST_INSERT_ID() query to return the last inserted id.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    """
    cur.execute("SELECT LAST_INSERT_ID();")
    return cur.fetchone()[0]

def setting_exists(cur, setting):
    """Use the cursor and a setting dictionary to check if a setting already exists"""
    query = (
        "SELECT SettingID FROM Setting"
        "  WHERE"
        "    InitialDewPoint = " + setting['InitialDewPoint'] + " AND"
        "    InitialDuty = " + setting['InitialDuty'] + " AND"
        "    InitialMass = " + setting['InitialMass'] + " AND"
        "    InitialPressure = " + setting['InitialPressure'] + " AND"
        "    InitialTemp = " + setting['InitialTemp'] + " AND"
        "    TimeStep = " + setting['TimeStep'] + ";")
    cur.execute(query)
    result = cur.fetchall()
    if not result:
        return False
    else:
        return result[0][0]

def list_tdms(file_path):
    """returns a list of the .tdms files contained within the argument file."""
    regex = compile(".tdms")
    file_list = [file for file in os.listdir(file_path) if regex.match(file, len(file)-5)]
    return file_list

def get_settings(tdms_obj):
    """returns a dictionary of the initial state of Tests in the TdmsFile object argument"""
    settings = {'initial_dew_point': tdms_obj.object("Data", "DewPoint").data[0],
        'initial_duty': tdms_obj.object("Data", "DutyCycle").data[0],
        'initial_mass': tdms_obj.object("Data", "Mass").data[0],
        'initial_pressure': tdms_obj.object("Data", "Pressure").data[0],
        'initial_temp': sum(tdms_obj.object("Data", "TC{}".format(x)).data[0] for x in range(3,14))/11
        }
    return settings

def get_tests(tdms_obj):
    """returns a dictionary of the initial state of Settings in the TdmsFile object argument"""
    tests = { 'author': "", 'date_time': tdms_obj.object().properties['DateTime'],
        'description': "", 'time_step': tdms_obj.object("Settings", "TimeStep").data[0]
        }

    for name, value in tdms_obj.object().properties.items():
        if name == "author":
            tests['author'] = value
        if name == "description":
            tests['description'] = value
    return tests

def get_obs(tdms_obj, idx):
    """returns a dictionary of strings derived from tdms object observation data"""
    observations = {'cap_man_ok': str(tdms_obj.object("Data", "CapManOk").data[idx]),
        'dew_point': str(tdms_obj.object("Data", "DewPoint").data[idx]),
        'duty_cycle': str(tdms_obj.object("Data", "DutyCycle").data[idx]),
        'idx': str(tdms_obj.object("Data", "Idx").data[idx]),
        'mass': str(tdms_obj.object("Data", "Mass").data[idx]),
        'optidew_ok': str(tdms_obj.object("Data", "OptidewOk").data[idx]),
        'pow_out': str(tdms_obj.object("Data", "PowOut").data[idx]),
        'pow_ref': str(tdms_obj.object("Data", "PowRef").data[idx]),
        'pressure': str(tdms_obj.object("Data", "Pressure").data[idx]),
        }
    return observations

def get_temp(tdms_obj, idx):
    """returns a dictionary of strings derived from tdms object temperature data"""
    temp = {'TC_num': str(idx), 'temp': str(tdms_obj.object("Data", "TC{}".format(idx)).data[idx])}
    return temp
