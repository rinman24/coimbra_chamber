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
    """Use the cursor and a setting dictionary to check if a setting already exists."""
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
    """Returns a list of the .tdms files contained within the argument directory.

    Positional arguments:
    file_path -- string
    """
    regex = compile(".tdms")
    file_list = [file for file in os.listdir(file_path) if regex.match(file, len(file)-5)]
    return file_list

def get_settings(tdms_obj):
    """Returns a dictionary of the initial state of Tests in the TdmsFile object argument.

    Description: Returns Setting data for the provided in the argument
    TdmsFile, tdms_object in a dictionary formatted for insert_dml.
    
    Positional arguments:
    tdms_obj -- nptdms.TdmsFile
    """
    settings = {'InitialDewPoint': "{0:.2f}".format(round(tdms_obj.object("Data", "DewPoint").data[0], 2)),
        'InitialDuty': str(tdms_obj.object("Data", "DutyCycle").data[0]),
        'InitialMass': str(tdms_obj.object("Data", "Mass").data[0]),
        'InitialPressure': str(round(tdms_obj.object("Data", "Pressure").data[0],0)),
        'InitialTemp': "{0:.2f}".format(round(sum(tdms_obj.object("Data", "TC{}".format(x)).data[0] for x in range(3, 14))/11, 2)),
        'TimeStep': "{0:.2f}".format(tdms_obj.object("Settings", "TimeStep").data[0])
        }
    return settings

def get_tests(tdms_obj):
    """Returns a dictionary of the initial state of Settings in the TdmsFile object argument.

    Description: Builds a dictionary containing the initial state of Test in the TdmsFile,
    and formats the data to use with insert_dml. Uses a loop to parse through a double linked
    list to search for "Author" and "Description" data.
    
    Positional arguments:
    tdms_obj -- nptdms.TdmsFile
    """
    tests = { 'Author': "", 'DateTime': str(tdms_obj.object().properties['DateTime']).split(".", 1)[0],
        'Description': ""
        }

    for name, value in tdms_obj.object().properties.items():
        if name == "author":
            tests['Author'] = value
        if name == "description":
            tests['Description'] = value
    return tests

def get_obs(tdms_obj, idx):
    """Returns a dictionary of strings derived from tdms object observation data.
    
    Description: Returns observation data for the provided index, idx, in the argument
    TdmsFile, tdms_object in a dictionary formatted for insert_dml.

    Positional arguments:
    tdms_obj -- nptdms.TdmsFile
    idx -- int
    """
    observations = {'CapManOk': str(tdms_obj.object("Data", "CapManOk").data[idx]),
        'DewPoint': "{0:.2f}".format(round(tdms_obj.object("Data", "DewPoint").data[idx], 2)),
        'Duty': str(tdms_obj.object("Data", "DutyCycle").data[idx]),
        'Idx': str(tdms_obj.object("Data", "Idx").data[idx]),
        'Mass': str(tdms_obj.object("Data", "Mass").data[idx]),
        'OptidewOk': str(tdms_obj.object("Data", "OptidewOk").data[idx]),
        'PowOut': str(tdms_obj.object("Data", "PowOut").data[idx]),
        'PowRef': str(tdms_obj.object("Data", "PowRef").data[idx]),
        'Pressure': str(round(tdms_obj.object("Data", "Pressure").data[idx],0))
        }
    return observations

def get_temp(tdms_obj, data_idx, couple_idx):
    """Returns a dictionary of strings derived from tdms object temperature data.

    Description: Returns temperature data for the provided row index, idx, and thermocouple index,
    couple_idx, in the argument TdmsFile, tdms_object in a dictionary formatted for insert_dml.

    Positional arguments:
    tdms_obj -- nptdms.TdmsFile
    idx -- int
    """
    temp = {'ThermocoupleNum': str(couple_idx), 'Temperature': str(tdms_obj.object("Data", "TC{}".format(couple_idx)).data[data_idx])}
    return temp

def add_input(cur, directory):
    """Adds data from argument directory to the data base using aproreate helper functions.

    Description: Uses loops to structure calls to add_setting, add_test, add_obs, and add_temp
    to build and execute queries using insert_dml and populate the MySQL database for all .tdms
    files in the argument directory. Uses cursor to call insert_dml.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    directory -- string
    """
    cur.execute("SET AUTOCOMMIT=0;")
    for file in list_tdms(directory):
        tdms_obj = TdmsFile(directory + file)
        test_id = add_test(cur, tdms_obj, str(add_setting(cur, tdms_obj)))
        range_int = len(tdms_obj.object("Data", "Idx").data)
        for obs_idx in range(range_int):
            obs_id = add_obs(cur, tdms_obj, str(test_id), obs_idx)
            add_temp(cur, tdms_obj, str(obs_id), obs_idx)

def add_setting(cur, tdms_obj):
    """Uses settings_exist and insert_dml to add settings to the data base and returns the setting id.
    
    Description: Uses cursor, cur to call insert_dml on a dictionary of Setting data
    built by get_setting using the argument TdmsFile, tdms_obj. Adds the new Setting and returns
    the new SettingID to the MySQL database if setting_exists returns false, or else returns
    the SettingID of the identical Setting found in the database.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tdms_obj -- nptdms.TdmsFile
    """
    settings = get_settings(tdms_obj)
    setting_id = setting_exists(cur, settings)
    if not setting_id:
        cur.execute(insert_dml("Setting", settings))
        setting_id = last_insert_id(cur)
    return setting_id

def add_test(cur, tdms_obj, setting_id):
    """Uses insert_dml to build a query for Test sql table and executes.

    Description: Uses cursor, cur to call insert_dml on a dictionary of Test data
    built by get_test using the argument TdmsFile, tdms_obj. Adds the foreign key
    SettingID, setting_id, to the dictionary before building the MySQL query.
    
    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tdms_obj -- nptdms.TdmsFile
    setting_id -- string
    """
    test = get_tests(tdms_obj)
    test["SettingID"] = setting_id
    test["TubeID"] = "1"#str(tdms_obj.object("Settings", "TubeID").data[0])
    cur.execute(insert_dml("Test", test))
    return last_insert_id(cur)

def add_obs(cur, tdms_obj, test_id, obs_idx):
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
    obs = get_obs(tdms_obj, obs_idx)
    obs["TestID"] = test_id
    cur.execute(insert_dml("Observation", obs))
    return last_insert_id(cur)

def add_temp(cur, tdms_obj, obs_id, temp_idx):
    """Uses insert_dml to build a query for Test sql table and executes.
    
    Description: Uses cursor, cur to call insert_dml on a dictionary of TempObservation data
    built by looping through get_temp for each thermocouple using the argument TdmsFile, tdms_obj,
    and index, temp_idx. Adds the foreign key ObservationID, obs_id, to the dictionary before
    building the MySQL query.

    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tdms_obj -- nptdms.TdmsFile
    obs_id -- string
    temp_idx -- int
    """
    temp = {}
    temp["ObservationID"] = obs_id
    for couple_idx in range(14):
        temp.update(get_temp(tdms_obj, temp_idx, couple_idx))
        cur.execute(insert_dml("TempObservation", temp))
