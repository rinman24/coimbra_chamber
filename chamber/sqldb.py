"""Docstring."""

import os
import re

import mysql.connector as conn
from mysql.connector import errorcode
from nptdms import TdmsFile


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
            print('Something is wrong with your user name or password')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
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
            print('\tCreating table {}: '.format(name), end='')
            cur.execute(ddl)
        except conn.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print('already exists.')
            else:
                print(err.msg)
        else:
            print('OK')

def insert_dml(table, row_data):
    """Use a table name and dictionay to return a MySQL insert DML query.

    Use the name of the table and a dictionary called row_data, where the keys are attribute names
    and the values are row data, to build and return a MySQL DML INSERT query.

    Parameters
    ----------
    table : string
        Name of the MySQL database table to insert into.
    row_data : dict of strings
        Set of values to insert into the table. Keys should be column names and values should be the
        value to insert.
        **Note: all values should be type string.**
    """
    query = ("INSERT INTO " + table + " "
             "    (" + ', '.join(row_data.keys()) + ")"
             "  VALUES"
             "    ('" + "', '".join(row_data.values()) + "');")
    return query

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
        List of filenames with a tdms extension. Elements of list are type string.
    """
    regex = re.compile('.tdms')
    file_list = [tdms for tdms in os.listdir(file_path) if regex.match(tdms, len(tdms)-5)]
    return file_list

def get_settings(tdms_obj):
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
        **Note: all values should be type string.**
    """
    settings = {'InitialDewPoint':
                '{0:.2f}'.format(round(tdms_obj.object('Data', 'DewPoint').data[0], 2)),
                'InitialDuty':
                str(tdms_obj.object('Data', 'DutyCycle').data[0]),
                'InitialMass':
                str(tdms_obj.object('Data', 'Mass').data[0]),
                'InitialPressure':
                str(round(tdms_obj.object('Data', 'Pressure').data[0], 0)),
                'InitialTemp':
                '{0:.2f}'.format(round(sum(tdms_obj.object('Data', 'TC{}'.format(x)).data[0]
                                           for x in range(3, 14))/11, 2)),
                'TimeStep':
                '{0:.2f}'.format(tdms_obj.object('Settings', 'TimeStep').data[0])
               }
    return settings

def get_test_cols(tdms_obj):
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
    test_cols : dict of strings
        Set of values to insert into the Test table. Keys should be column names and values should
        be the value to insert.
        **Note: all values should be type string.**
    """
    test_cols = {'Author': '',
                 'DateTime': str(tdms_obj.object().properties['DateTime']).split('.', 1)[0],
                 'Description': ''
                }

    for name, value in tdms_obj.object().properties.items():
        if name == 'author':
            test_cols['Author'] = value
        if name == 'description':
            test_cols['Description'] = value
    return test_cols

def get_obs(tdms_obj, idx):
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
        **Note: all values should be type string.**
    """
    observations = {'CapManOk':
                    str(tdms_obj.object('Data', 'CapManOk').data[idx]),
                    'DewPoint':
                    '{0:.2f}'.format(round(tdms_obj.object('Data', 'DewPoint').data[idx], 2)),
                    'Duty':
                    str(tdms_obj.object('Data', 'DutyCycle').data[idx]),
                    'Idx':
                    str(tdms_obj.object('Data', 'Idx').data[idx]),
                    'Mass':
                    str(tdms_obj.object('Data', 'Mass').data[idx]),
                    'OptidewOk':
                    str(tdms_obj.object('Data', 'OptidewOk').data[idx]),
                    'PowOut':
                    str(tdms_obj.object('Data', 'PowOut').data[idx]),
                    'PowRef':
                    str(tdms_obj.object('Data', 'PowRef').data[idx]),
                    'Pressure':
                    str(round(tdms_obj.object('Data', 'Pressure').data[idx], 0))
                   }
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
    temp : dict of strings
        A single value to insert into the TempObservation table. Key should be thermocouple number
        and the value should be the temperature measurement.
        **Note: all values should be type string.**
    """
    temp = {'ThermocoupleNum':
            str(couple_idx),
            'Temperature':
            str(tdms_obj.object('Data', 'TC{}'.format(couple_idx)).data[data_idx])}
    return temp

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
    cur.execute('SET AUTOCOMMIT=0;')
    for file_obj in list_tdms(directory):
        tdms_obj = TdmsFile(directory + file_obj)
        test_id = add_test(cur, tdms_obj, str(add_setting(cur, tdms_obj)))
        range_int = len(tdms_obj.object('Data', 'Idx').data)
        for obs_idx in range(range_int):
            obs_id = add_obs(cur, tdms_obj, str(test_id), obs_idx)
            add_temp(cur, tdms_obj, str(obs_id), obs_idx)

def add_setting(cur, tdms_obj):
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
    settings = get_settings(tdms_obj)
    setting_id = setting_exists(cur, settings)
    if not setting_id:
        cur.execute(insert_dml('Setting', settings))
        setting_id = cur.lastrowid
    return setting_id

def add_test(cur, tdms_obj, setting_id):
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
    test = get_test_cols(tdms_obj)
    test['SettingID'] = setting_id
    test['TubeID'] = '1'#str(tdms_obj.object('Settings', 'TubeID').data[0])
    cur.execute(insert_dml('Test', test))
    return cur.lastrowid

def add_obs(cur, tdms_obj, test_id, obs_idx):
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
    obs = get_obs(tdms_obj, obs_idx)
    obs['TestID'] = test_id
    cur.execute(insert_dml('Observation', obs))
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
    temp = {}
    temp['ObservationID'] = obs_id
    for couple_idx in range(14):
        temp.update(get_temp(tdms_obj, temp_idx, couple_idx))
        cur.execute(insert_dml('TempObservation', temp))
