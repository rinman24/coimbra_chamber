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

    Uses environment variables MySqlUserName, MySqlCredentials, MySqlHost, and MySqlDataBase to
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
    """Use a MySQL cursor object and a list of tuples to create tables in the database.

    Uses a list of tuples where the 0 index is the name of the table and the 1 index is a string of
    MySQL DDL used to create the table. A list is required so that the DDL can be executed in order
    so that foreign key constraint errors do not occur.
    
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
    """Use a MySQL cursor object and a setting dictionary to check if a setting already exists.

    Uses the setting dictionary where the keys are the columns in the Setting table and the values
    are the string values. The cursor executes a DML SELECT statement and returns the SettingID if
    the setting exists or False if no setting matching the query exists.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    setting : dict of strings
        Set of setting values to check for. Keys should be column names from the Setting table and
        values should be the value to insert.
        **Note: all values should be type string.**
    
    Returns
    -------
    SettingID : int or False
        This is the primary key for the Setting table if the setting already exists. If the setting
        does not exist in the database the function returns False.
    """
    cur.execute(const.FIND_SETTING, setting)
    result = cur.fetchall()
    if not result:
        return False
    else:
        return result[0][0]

def list_tdms(file_path):
    """Use the file_path to find tdms files.

    This function searces through the argument directory and returns a list of all filenames with
    the tdms extension.
    
    Parameters
    ----------
    file_path : string
        This is the directory to search for tdms files.
    
    Returns
    -------
    file_list : list of strings
        Alphabetically sorted list of filenames with a .tdms extension. Elements of list are type string.
    """
    regex = compile(r".tdms$")
    file_list = [file_name for file_name in os.listdir(file_path)
                 if regex.search(file_name)]
    file_list.sort()
    return file_list

def get_setting_info(tdms_obj):
    """Use a TdmsFile object to return a dictionary containg the initial state of the test.

    This function searces through the TdmsFile object for the initial settings including:
    InitialDewPoint, InitialDuty, InitialMass, InitialPressure, InitialTemp, and TimeStep.
    The function returns a dictionary of settings formatted for the insert_dml method.
    
    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original tdms files were created
        from UCSD Chamber experiments in the Coimbra Lab in SERF 159.
    
    Returns
    -------
    settings : dict of strings
        Set of values to insert into the Setting table. Keys should be column names and values
        should be the value to insert.
    """
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
    """Use a TdmsFile object to find test details.

    Builds a dictionary containing the initial state of Test in the TdmsFile, and formats the data
    to use with insert_dml. Uses a loop to parse through a double linked list to search for 'Author'
    and 'Description' fields.
    
    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original tdms files were created
        from UCSD Chamber experiments in the Coimbra Lab in SERF 159.
    
    Returns
    -------
    tests : dict of strings
        Set of values to insert into the Test table. Keys should be column names and values should
        be the value to insert.
     """
    tests = {'Author': '', 'DateTime': tdms_obj.object().properties['DateTime'],
             'Description': ''}

    for name, value in tdms_obj.object().properties.items():
        if name == "author":
            tests['Author'] = value
        if name == "description":
            tests['Description'] = value
    return tests

def get_obs_info(tdms_obj, idx):
    """Use a TdmsFile object and idx to return a dictionary of observation data.

    Builds a dictionary containing the observation for a given index (time) in the TdmsFile objrct,
    and formats the data for use with insert_dml.
    
    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original tdms files were created
        from UCSD Chamber experiments in the Coimbra Lab in SERF 159.
    idx : int
        This is the index in the tdms file, which represents a single time.
    
    Returns
    -------
    observations : dict of strings
        Set of values to insert into the Observation table. Keys should be column names and values
        should be the value to insert.
    """
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
    """Use a TdmsFile object with data_idx and couple_idx to get a thermocouple observation.

    Returns temperature data for the provided index (time) and thermocouple index provided in the
    argument and returns a dictionary formatted for use with the insert_dml method.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original tdms files were created
        from UCSD Chamber experiments in the Coimbra Lab in SERF 159.
    data_idx : int
        This is the index in the tdms file, which represents a single time.
    couple_idx : int
        This is the thermocouple index for a specific observation in the tdms file, which represents
        a single thermocouple measurement at a single time.
    
    Returns
    -------
    temp : string
        A single value to insert into the TempObservation table. Key should be thermocouple number
        and the value should be the temperature measurement.
    """
    return '{:.2f}'.format(tdms_obj.object("Data", "TC{}".format(couple_idx)).data[data_idx])

def add_setting_info(cur, tdms_obj):
    """Use MySQL cursor and TdmsFile objecs to add the settings for a given test.

    Uses cursor to call insert_dml on a dictionary of Setting data built by the get_setting method.
    Adds the new Setting if the setting doesn't exist and returns the SettingID form the MySQL
    database. If the setting already exists, then the SettingID of that setting is returned.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original tdms files were created
        from UCSD Chamber experiments in the Coimbra Lab in SERF 159.
    
    Returns
    -------
    setting_id : int
        This is the SettingID for the MySQL database. SettingID is the primary key for the Setting
        table.
    """
    setting_info = get_setting_info(tdms_obj)
    setting_id = setting_exists(cur, setting_info)
    if not setting_id:
        cur.execute(const.ADD_SETTING, setting_info)
        setting_id = cur.lastrowid
    return setting_id

def add_test_info(cur, tdms_obj, setting_id):
    """Use MySQL cursor and TdmsFile objects with setting_id to add a test to the database.
    
    Uses cursor  to call insert_dml on a dictionary of Test data built by get_test using the
    argument TdmsFile. Adds the foreign key SettingID to the dictionary before building the MySQL
    query.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original tdms files were created
        from UCSD Chamber experiments in the Coimbra Lab in SERF 159.
    setting_id : int
        This is the SettingID for the MySQL database. SettingID is the primary key for the Setting
        table.
    
    Returns
    -------
    lastrowid : int
        This is the TestID which is the primary key for the Test table.
    """
    test_info = get_test_info(tdms_obj)
    test_info["SettingID"] = setting_id
    test_info["TubeID"] = 1#str(tdms_obj.object("Settings", "TubeID").data[0])
    cur.execute(const.ADD_TEST, test_info)
    return cur.lastrowid

def add_obs_info(cur, tdms_obj, test_id, obs_idx):
    """Use MySQL cursor and TdmsFile objects with test_id and obs_idx to add obs to database.

    Uses cursor to call insert_dml on a dictionary of observation data built by get_obs using the
    argument TdmsFile and index. Adds the foreign key TestID to the dictionary before building the
    MySQL query.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original tdms files were created
        from UCSD Chamber experiments in the Coimbra Lab in SERF 159.
    test_id : int
        This is the TestID for the MySQL database. TestID is the primary key for the Test table.
    obs_idx : int
        This is the index in the tdms file, which represents a single time.
    
    Returns
    -------
    lastrowid : int
        This is the ObservationID which is the primary key for the Observation table.
    """
    obs_info = get_obs_info(tdms_obj, obs_idx)
    obs_info['TestID'] = test_id
    cur.execute(const.ADD_OBS, obs_info)
    return cur.lastrowid

def add_temp(cur, tdms_obj, obs_id, temp_idx):
    """Use MySQL cursor and TdmsFile objects with obs_id and temp_idx to add a temp observation.

    Uses cursor to call insert_dml on a dictionary of TempObservation data built by looping through
    get_temp for each thermocouple using the argument TdmsFile and index. Adds the foreign key
    ObservationID to the dictionary before building the MySQL query.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original tdms files were created
        from UCSD Chamber experiments in the Coimbra Lab in SERF 159.
    obs_id : int
        This is the ObsID for the MySQL database. ObsID is the primary key for the Observation
        table.
    temp_idx : int
        This is the temperature index in the tdms file, which represents a single time.
    """
    temp_data = [(obs_id, couple_idx, get_temp(tdms_obj, temp_idx, couple_idx)) for couple_idx in range(14)]
    cur.executemany(const.ADD_TEMP, temp_data)

def add_input(cur, directory):
    """Use a MySQL cursor object and a directory to insert tdms files into the MySQL database.

    Uses loops to structure calls to add_setting, add_test, add_obs, and add_temp to build and
    execute queries using insert_dml and populate the MySQL database for all tdms files in the
    argument directory. Uses cursor to call insert_dml.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    directory : string
        This is the directory to search for tdms files.
    """
    for file_name in list_tdms(directory):
        tdms_obj = TdmsFile(directory + file_name)
        test_id = add_test_info(cur, tdms_obj, add_setting_info(cur, tdms_obj))
        range_int = len(tdms_obj.object("Data", "Idx").data)
        for obs_idx in range(range_int):
            obs_id = add_obs_info(cur, tdms_obj, test_id, obs_idx)
            add_temp(cur, tdms_obj, obs_id, obs_idx)

# def insert_dml(table, row_data):
#    """Use a table name and dictionay to return a MySQL insert DML query.
#    Use the name of the table and a dictionary called row_data, where the keys are attribute names
#    and the values are row data, to build and return a MySQL DML INSERT query.

#    Parameters
#    ----------
#    table : string
#        Name of the MySQL database table to insert into.
#    row_data : dict of strings
#        Set of values to insert into the table. Keys should be column names and values should be the
#        value to insert.
#        **Note: all values should be type string.**
#    """
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
