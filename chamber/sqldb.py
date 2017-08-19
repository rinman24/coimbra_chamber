"""Docstring."""
from decimal import Decimal
import os
from re import compile

import mysql.connector as conn
from mysql.connector import errorcode
from nptdms import TdmsFile

import chamber.const as const

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
                print('already exists.')
            else:
                print(err.msg)
        else:
            print('OK')

def setting_exists(cur, setting):
    """Use the cursor and a setting dictionary to check if a setting already exists"""
    cur.execute(const.FIND_SETTING, setting)
    result = cur.fetchall()
    if not result:
        return False
    else:
        return result[0][0]

def list_tdms(file_path):
    """returns a list of the .tdms files contained within the argument file."""
    regex = compile(".tdms")
    file_list = [file_name for file_name in os.listdir(file_path)
                 if regex.match(file_name, len(file_name)-5)]
    return file_list

def get_setting_info(tdms_obj):
    """returns a dictionary of the initial state of Tests in the TdmsFile object argument"""
    settings = {'InitialDewPoint':
                '{:.2f}'.format(tdms_obj.object("Data", "DewPoint").data[0]),
                'InitialDuty':
                '{:.1f}'.format(tdms_obj.object("Data", "DutyCycle").data[0]),
                'InitialMass':
                '{:.7f}'.format(tdms_obj.object("Data", "Mass").data[0]),
                'InitialPressure': 
                int(tdms_obj.object("Data", "Pressure").data[0]),
                'InitialTemp':
                '{:.2f}'.format(sum(tdms_obj.object("Data", "TC{}".format(x)).data[0]
                                        for x in range(3, 14))/11),
                'TimeStep':
                '{:.2f}'.format(tdms_obj.object("Settings", "TimeStep").data[0])}
    return settings

def get_test_info(tdms_obj):
    """returns a dictionary of the initial state of Settings in the TdmsFile object argument"""
    tests = {'Author': '', 'DateTime': tdms_obj.object().properties['DateTime'],
             'Description': ''}

    for name, value in tdms_obj.object().properties.items():
        if name == "author":
            tests['Author'] = value
        if name == "description":
            tests['Description'] = value
    return tests

def get_obs_info(tdms_obj, idx):
    """returns a dictionary of strings derived from tdms object observation data"""
    observations = {'CapManOk':
                    int(tdms_obj.object("Data", "CapManOk").data[idx]),
                    'DewPoint':
                    '{:.2f}'.format(tdms_obj.object("Data", "DewPoint").data[idx]),
                    'Duty':
                    '{:.1f}'.format(tdms_obj.object("Data", "DutyCycle").data[idx]),
                    'Idx':
                    int(tdms_obj.object("Data", "Idx").data[idx]),
                    'Mass':
                    '{:.7f}'.format(tdms_obj.object("Data", "Mass").data[idx]),
                    'OptidewOk':
                    int(tdms_obj.object("Data", "OptidewOk").data[idx]),
                    'PowOut':
                    '{:.4f}'.format(tdms_obj.object("Data", "PowOut").data[idx]),
                    'PowRef':
                    '{:.4f}'.format(tdms_obj.object("Data", "PowRef").data[idx]),
                    'Pressure':
                    int(tdms_obj.object("Data", "Pressure").data[idx])}
    return observations

def get_temp(tdms_obj, data_idx, couple_idx):
    """Returns a tdms object's temperature data from a specified thermocouple.

    Description: Returns temperature data for the provided row index, idx, and thermocouple index,
    couple_idx, in the argument TdmsFile.

    Positional arguments:
    tdms_obj -- nptdms.TdmsFile
    data_idx -- int
    couple_idx -- int
    """
    return '{:.2f}'.format(tdms_obj.object("Data", "TC{}".format(couple_idx)).data[data_idx])

def add_setting_info(cur, tdms_obj):
    """Uses settings_exist and insert_dml to add settings to the data base and returns the setting id.
    
    Description: Uses cursor, cur to call insert_dml on a dictionary of Setting data
    built by get_setting using the argument TdmsFile, tdms_obj. Adds the new Setting and returns
    the new SettingID to the MySQL database if setting_exists returns false, or else returns
    the SettingID of the identical Setting found in the database.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tdms_obj -- nptdms.TdmsFile
    """
    setting_info = get_setting_info(tdms_obj)
    setting_id = setting_exists(cur, setting_info)
    if not setting_id:
        cur.execute(const.ADD_SETTING, setting_info)
        setting_id = cur.lastrowid
    return setting_id

def add_test_info(cur, tdms_obj, setting_id):
    """Uses insert_dml to build a query for Test sql table and executes.

    Description: Uses cursor, cur to call insert_dml on a dictionary of Test data
    built by get_test using the argument TdmsFile, tdms_obj. Adds the foreign key
    SettingID, setting_id, to the dictionary before building the MySQL query.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tdms_obj -- nptdms.TdmsFile
    setting_id -- string
    """
    test_info = get_test_info(tdms_obj)
    test_info["SettingID"] = setting_id
    test_info["TubeID"] = 1#str(tdms_obj.object("Settings", "TubeID").data[0])
    cur.execute(const.ADD_TEST, test_info)
    return cur.lastrowid

def add_obs_info(cur, tdms_obj, test_id, idx):
    """Uses insert_dml to build a query for Test sql table and executes.

    Description: Uses cursor, cur to call insert_dml on a dictionary of observation data
    built by get_obs using the argument TdmsFile, tdms_obj, and index, obs_idx. Adds the
    foreign key TestID, test_id, to the dictionary before building the MySQL query.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tdms_obj -- nptdms.TdmsFile
    test_id -- string
    obs_idx -- int
    """
    obs_info = get_obs_info(tdms_obj, idx)
    obs_info['TestID'] = test_id
    cur.execute(const.ADD_OBS, obs_info)
    return cur.lastrowid

def add_temp(cur, tdms_obj, obs_id, temp_idx):
    """Uses insert_dml to build a query for Test sql table and executes.

    Description: Uses cursor, cur and cursor function executemany to input TempObservation data
    by looping through get_temp for each thermocouple using the argument TdmsFile, tdms_obj,
    and index, temp_idx. Adds the foreign key ObservationID, obs_id, to the values list before
    building the MySQL query.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tdms_obj -- nptdms.TdmsFile
    obs_id -- string
    temp_idx -- int
    """
    temp_data = [(obs_id, couple_idx, get_temp(tdms_obj, temp_idx, couple_idx)) for couple_idx in range(14)]
    #values = []
    #for couple_idx in range(14):
    #    values.append((obs_id, couple_idx, get_temp(tdms_obj, temp_idx, couple_idx)))
    cur.executemany(const.ADD_TEMP, temp_data)

def add_input(cur, directory):
    """Adds data from argument directory to the data base using aproreate helper functions.

    Description: Uses loops to structure calls to add_setting, add_test, add_obs, and add_temp
    to build and execute queries using insert_dml and populate the MySQL database for all .tdms
    files in the argument directory. Uses cursor to call insert_dml.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    directory -- string
    """
    for file_name in list_tdms(directory):
        tdms_obj = TdmsFile(directory + file_name)
        test_id = add_test_info(cur, tdms_obj, add_setting_info(cur, tdms_obj))
        range_int = len(tdms_obj.object("Data", "Idx").data)
        for obs_idx in range(range_int):
            obs_id = add_obs_info(cur, tdms_obj, test_id, obs_idx)
            add_temp(cur, tdms_obj, obs_id, obs_idx)

# def insert_dml(table, row_data):
#     """Use a table name and dictionay to return a MySQL insert DML query.

#     Description: Use the name of the table and a dictionary called row_data, where the keys are
#     attribute names and the values are row data, to build and return a MySQL DML INSERT query.
#     Please note that all the values in the row_data dictionary should be string types.

#     Positional arguments:
#     table -- string
#     row_data -- dict of strings
#     """
#     query = (
#         "INSERT INTO " + table + " "
#         "    (" + ', '.join(row_data.keys()) + ")"
#         "  VALUES"
#         "    ('" + "', '".join(row_data.values()) + "');")
#     return query

# def last_insert_id(cur):
#     """Use the last SELECT LAST_INSERT_ID() query to return the last inserted id.

#     Positional arguments:
#     cur -- mysql.connector.cursor.MySQLCursor
#     """
#     cur.execute("SELECT LAST_INSERT_ID();")
#     return cur.fetchone()[0]
