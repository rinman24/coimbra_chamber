"""Docstring."""
from decimal import Decimal
import numpy as np
import os
from pathlib import Path
from re import compile
from scipy import stats
import shutil

from CoolProp.HumidAirProp import HAPropsSI
import mysql.connector as conn
from mysql.connector import errorcode
from nptdms import TdmsFile

import chamber.const as const


def connect_sqldb(database):
    """
    Use connect constructor to connect to a MySQL server.

    Uses environment variables MySqlUserName, MySqlCredentials, MySqlHost to
    connect to a MySQL server. If the environment variables are not already
    available use, execute the follwing command, for example, in the terminal:

    $ export MySqlUserName=user

    Parameters
    ----------
    database : str
        The name of the desired database to connect to.
    Returns
    -------
    cnx : MySQLConnection
        Returns the MySQL connection object

    """
    config = {'user': os.environ['MYSQLUSERNAME'],
              'password': os.environ['MYSQLCREDENTIALS'],
              'host': os.environ['MYSQLHOST'],
              'database': database}
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
    """
    Use a MySQL cursor and a list of tuples to create tables in the database.

    Uses a list of tuples where the 0 index is the name of the table and the 1
    index is a string of MySQL DDL used to create the table. A list is required
    so that the DDL can be executed in order so that foreign key constraint
    errors do not occur.

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
    print('Setting up tables...')
    for table in tables:
        name, ddl = table
        try:
            cur.execute(ddl)
        except conn.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(name, 'already exists.')
            else:
                print(err.msg)
        else:
            print(table[0], ' OK')


def setting_exists(cur, setting_info):
    """
    Check if a setting already exists.

    Uses the setting dictionary where the keys are the columns in the Setting
    table and the values are the string values. The cursor executes a DML
    SELECT statement and returns the SettingID if the setting exists or False
    if no setting matching the query exists.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    setting_info : dict of strings
        Set of setting values to check for. Keys should be column names from
        the Setting table and values should be the value to insert.

    Returns
    -------
    setting_id : tuple or False
        SettingID[0] is the SettingID for the MySQL database. SettingID is the
        primary key for the Setting table. Setting_ID[1] is the value of
        IsMass. If the setting does not exist in the database the function
        returns False.

    """
    cur.execute(const.FIND_SETTING, setting_info)
    result = cur.fetchall()
    if not result:
        return False
    else:
        setting_id = result[0][0]
        return setting_id


# def list_tdms(file_path, file_list=None):
#     """Use the file_path to find tdms files.

#     This function recursively searches through the argument directory and
#     returns a list of all filepaths for files with the tdms extension.

#     Parameters
#     ----------
#     file_path : string
#         This is the directory to search for tdms files.
#     file_list : empty list
#         This is an empty list when the function is called with only a
# directory
#         argument. File_list is then populated recursively.

#     Returns
#     -------
#     file_list : list of strings
#         List of absolute filepaths of files with a .tdms extension. Elements
# of
#         list are type string.
#     """
#     if file_list is None:
#         file_list = []
#     try:
#         for file_name in os.listdir(file_path):
#             list_tdms(os.path.join(file_path, file_name), file_list)
#     except NotADirectoryError:
#         regex = compile(r".tdms$")
#         if regex.search(file_path):
#             return file_list.append(file_path)
#     return file_list


def test_exists(cur, test_info):
    """
    Check if a test already exists.

    Uses the test_info dictionary where the keys are the columns in the Test
    table and the values are the string values. The cursor executes a DML
    SELECT statement and returns the TestID if the test exists or False if no
    test matching the query exists.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    test_info : dict of strings
        Set of setting values to check for. Keys should be column names from
        the Test table and values should be the value to insert.

    Returns
    -------
    TestID : int or False
        This is the primary key for the Test table if the test already exists.
        If the test does not exist in the database the function returns False.

    """
    if not test_info:
        print("File Unable to Transfer")
        return False
    cur.execute(const.FIND_TEST.format(
        test_info['DateTime'].replace(microsecond=0).replace(tzinfo=None)))
    result = cur.fetchall()
    if not result:
        return False
    else:
        return result[0][0]


# def move_files(directory):
#     """Move all tdms files into new directory maintaining file structure.

#     This function moves all tdms files in directory into the directory
#     '/home/user/read_files/'.

#     Parameters
#     ----------
#     directory : string
#         This is the directory to move tdms files from.
#     """
#     for file_path in list_tdms(directory):
#         if not os.stat(file_path).st_size == 0:
#             new_file_path = os.path.join(os.path.join(
#                             str(Path.home()), "read_files"),
#                             os.path.relpath(file_path)[3:])
#             if not os.path.exists(os.path.split(new_file_path)[0]):
#                 os.makedirs(os.path.split(new_file_path)[0])
#             shutil.move(file_path, new_file_path)


def get_setting_info(tdms_obj):
    """
    Return a dictionary containg the initial state of the test.

    This function searches through the TdmsFile object for the initial settings
    including: Duty, Mass, Pressure, Temp, and TimeStep. The function returns a
    dictionary of settings formatted for use with the ADD_SETTING querry in
    const.py.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original
        tdms files were created from UCSD Chamber experiments in the Coimbra
        Lab in SERF 159.

    Returns
    -------
    setting_info : dict
        Set of values to insert into the Setting table. Keys should be column
        names and values should be the value to insert.

    """
    temp_list = [float(get_temp_info(tdms_obj, 0, x)) for x in range(4, 14)]
    duty = tdms_obj.object('Settings', 'DutyCycle').data[0]
    pressure = tdms_obj.object('Data', 'Pressure').data[0]
    setting_info = {'Duty': '{:.1f}'.format(round(duty, 1)),
                    'Pressure': 5000*round(float(pressure)/5000),
                    'Temperature': 5*round(float(np.mean(temp_list))/5)}
    return setting_info


def get_test_info(tdms_obj):
    """
    Use a TdmsFile object to find test details.

    Builds a dictionary containing the initial state of Test in the TdmsFile,
    and formats the data for use with the ADD_TEST querry in const.py. Uses a
    loop to parse through a double linked list to search for 'Author' and
    'Description' fields.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original
        tdms files were created from UCSD Chamber experiments in the Coimbra
        Lab in SERF 159.

    Returns
    -------
    test_info : dict of strings
        Set of values to insert into the Test table. Keys should be column
        names and values should be the value to insert.

     """
    test_info = {'Author': '',
                 'DateTime': tdms_obj.object().properties['DateTime'].replace(
                                 microsecond=0).replace(tzinfo=None),
                 'Description': '',
                 'IsMass': int(
                    tdms_obj.object("Settings", "IsMass").data[0]),
                 'TimeStep': int(
                    tdms_obj.object("Settings", "TimeStep").data[0])}

    for name, value in tdms_obj.object().properties.items():
        if name == "author":
            test_info['Author'] = value
        if name == "description":
            test_info['Description'] = value[:500]
    return test_info


def get_obs_info(tdms_obj, tdms_idx):
    """
    Return a dictionary of observation data.

    Builds a dictionary containing the observation for a given index (time) in
    the TdmsFile objrct, and formats the data for use with the ADD_OBS querry
    in const.py.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original
        tdms files were created from UCSD Chamber experiments in the Coimbra
        Lab in SERF 159.
    tdms_idx : int
        This is the index in the tdms file, which represents a single time.

    Returns
    -------
    obs_info : dict
        Set of values to insert into the Observation table. Keys should be
        column names and values
        should be the value to insert.

    """
    obs_info = {'CapManOk': int(
                    tdms_obj.object("Data", "CapManOk").data[tdms_idx]),
                'DewPoint': '{:.2f}'.format(
                    tdms_obj.object("Data", "DewPoint").data[tdms_idx]),
                'Idx': int(
                    tdms_obj.object("Data", "Idx").data[tdms_idx]),
                'OptidewOk': int(
                    tdms_obj.object("Data", "OptidewOk").data[tdms_idx]),
                'PowOut': '{:.4f}'.format(
                    tdms_obj.object("Data", "PowOut").data[tdms_idx]),
                'PowRef': '{:.4f}'.format(
                    tdms_obj.object("Data", "PowRef").data[tdms_idx]),
                'Pressure': int(
                    tdms_obj.object("Data", "Pressure").data[tdms_idx])}
    if tdms_obj.object("Settings", "IsMass").data[0] == 1:
        obs_info['Mass'] = '{:.7f}'.format(
            tdms_obj.object("Data", "Mass").data[tdms_idx])
    return obs_info


def get_temp_info(tdms_obj, tdms_idx, couple_idx):
    """
    Get a thermocouple observation.

    Returns temperature data for the provided index (time) and thermocouple
    index provided in the argument and returns a dictionary formatted for use
    with the ADD_TEMP querry in const.py. Does nothing if temperature exceeds
    database limits is (1000.00 kelvin or above) or IsMass is set to 0.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original
        tdms files were created from UCSD Chamber experiments in the Coimbra
        Lab in SERF 159.
    tdms_idx : int
        This is the index in the tdms file, which represents a single time.
    couple_idx : int
        This is the thermocouple index for a specific observation in the tdms
        file, which represents a single thermocouple measurement at a single
        time.

    Returns
    -------
    temp_info : string
        A single value to insert into the TempObservation table. Key should be
        thermocouple number and the value should be the temperature
        measurement.

    """
    regex = compile(r'^(\d){3}.(\d){2}$')
    temp_info = '{:.2f}'.format(
        tdms_obj.object("Data", "TC{}".format(couple_idx)).data[tdms_idx])
    if not regex.search(temp_info):
        return
    return temp_info


def add_tube_info(cur):
    """
    Use MySQL cursor to add the test-independant Tube information.

    Uses cursor .execute function on the ADD_TUBE and TUBE_DATA constants in
    const.py. Adds the new Tube if the Tube doesn't exist. If the Tube already
    exists, then the function does nothing.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.

    """
    cur.execute(const.FIND_TUBE, const.TUBE_DATA)
    if not cur.fetchall():
        cur.execute(const.ADD_TUBE, const.TUBE_DATA)


def add_setting_info(cur, tdms_obj):
    """
    Use MySQL cursor and TdmsFile objecs to add the settings for a given test.

    Uses cursor's .execute function on a MySQL insert query and dictionary of
    Setting data built by the get_setting method. Adds the new Setting if the
    setting doesn't exist and returns the SettingID form the MySQL database.
    If the setting already exists, then the SettingID of that setting is
    returned.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original
        tdms files were created from UCSD Chamber experiments in the Coimbra
        Lab in SERF 159.

    Returns
    -------
    setting_id : tuple
        SettingID[0] is the SettingID for the MySQL database. SettingID is the
        primary key for the Setting table. Setting_ID[1] is the value of
        IsMass.

    """
    setting_info = get_setting_info(tdms_obj)
    setting_id = setting_exists(cur, setting_info)
    if not setting_id:
        cur.execute(const.ADD_SETTING, setting_info)
        setting_id = cur.lastrowid
    return setting_id


def add_test_info(cur, tdms_obj, setting_id):
    """
    Add a Test to the database.

    Uses cursor's .execute function on a MySQL insert query and dictionary of
    Test data built by get_test using the argument TdmsFile. Adds the foreign
    key SettingID to the dictionary before executing the MySQL query.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original
        tdms files were created from UCSD Chamber experiments in the Coimbra
        Lab in SERF 159.
    setting_id : tuple
        SettingID[0] is the SettingID for the MySQL database. SettingID is the
        primary key for the Setting table. Setting_ID[1] is the value of
        IsMass.

    Returns
    -------
    test_id : tuple
        TestID[0] is the primary key for the Test table. TestID[1] is the value
        of IsMass.

    """
    test_info = get_test_info(tdms_obj)
    test_id = test_exists(cur, test_info)
    if not test_id:
        test_info["SettingID"] = setting_id
        test_info["TubeID"] = str(
            tdms_obj.object("Settings", "TubeID").data[0])
        cur.execute(const.ADD_TEST, test_info)
        test_id = cur.lastrowid
    return test_id


def add_obs_info(cur, tdms_obj, test_id, tdms_idx):
    """
    Add an Observation to the database.

    Uses cursor's .execute function on a MySQL insert query and dictionary of
    observation data built by get_obs using the argument TdmsFile and index.
    Adds the foreign key TestID to the dictionary before executing the MySQL
    query.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original
        tdms files were created from UCSD Chamber experiments in the Coimbra
        Lab in SERF 159.
    test_id : tuple
        TestID[0] is the primary key for the Test table. TestID[1] is the value
        of IsMass.
    obs_idx : int
        This is the index in the tdms file, which represents a single time.

    Returns
    -------
    obs_id : tuple
        obs_id[0] is the ObservationID which is the primary key for the
        Observation table. obs_id[1] is the boolean representation of IsMass.

    """
    obs_info = get_obs_info(tdms_obj, tdms_idx)
    obs_info['TestId'] = test_id
    if tdms_obj.object("Settings", "IsMass").data[0] == 1:
        cur.execute(const.ADD_OBS_M_T, obs_info)
    else:
        cur.execute(const.ADD_OBS_M_F, obs_info)


def add_temp_info(cur, tdms_obj, test_id, tdms_idx, idx):
    """
    Add a TempObservation to the database.

    Uses cursor's .execute function on a MySQL insert query and dictionary of
    TempObservation data built by looping through get_temp_info for each
    thermocouple using the argument TdmsFile and index. Adds the foreign key
    ObservationID to the dictionary before executing the MySQL query.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tdms_obj : nptdms.TdmsFile
        TdmsFile object containg the data from the tdms test file. Original
        tdms files were created from UCSD Chamber experiments in the Coimbra
        Lab in SERF 159.
    obs_id : tuple
        obs_id[0] is the ObservationID which is the primary key for the
        Observation table.
        obs_id[1] is the boolean representation of IsMass.
    temp_idx : int
        This is the temperature index in the tdms file, which represents a
        single time.

    """
    if tdms_obj.object("Settings", "IsMass").data[0] == 1:
        temp_data = [(couple_idx,
                      get_temp_info(tdms_obj, tdms_idx, couple_idx),
                      idx,
                      test_id) for couple_idx in range(4, 14)]
    else:
        temp_data = [(couple_idx,
                      get_temp_info(tdms_obj, tdms_idx, couple_idx),
                      idx,
                      test_id) for couple_idx in range(14)]

    cur.executemany(const.ADD_TEMP, temp_data)


def add_data(cur, file_name, test=False):
    """
    Insert tdms files into the MySQL database from argument directory.

    Uses loops to structure calls to add_setting, add_test, add_obs, and
    add_temp to build and execute queries using constants in const.py and
    populate the MySQL database for all tdms files in the argument directory.
    Passes cursor into helper functions.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    directory : string
        This is the directory to search for tdms files.

    """
    tdms_obj = TdmsFile(file_name)
    if not test_exists(cur, get_test_info(tdms_obj)):
        # print("WE GOT IN THE LOOP")
        test_id = add_test_info(cur, tdms_obj, add_setting_info(cur, tdms_obj))
        # print("TestID = ", test_id)
        for tdms_idx in range(len(tdms_obj.object("Data", "Idx").data)):
            add_obs_info(cur, tdms_obj, test_id, tdms_idx)
        #   add_temp(cur, tdms_obj, obs_id, obs_idx)
    # if not test:
    #    move_files(directory)


# def add_input(cur, directory, test=False):
#     """Insert tdms files into the MySQL database from argument directory.

#     Uses loops to structure calls to add_setting, add_test, add_obs, and
#     add_temp to build and execute queries using constants in const.py and
#     populate the MySQL database for all tdms files in the argument directory.
#     Passes cursor into helper functions.

#     Parameters
#     ----------
#     cur : MySQLCursor
#         Cursor used to interact with the MySQL database.
#     directory : string
#         This is the directory to search for tdms files.
#     """
#     for file_name in list_tdms(directory):
#         # print(file_name)
#         tdms_obj = TdmsFile(file_name)
#         # print(test_exists(cur, get_test_info(tdms_obj))) # DELEDTE
#         if not test_exists(cur, get_test_info(tdms_obj)):
#             # print("WE GOT IN THE LOOP")
#             test_id = add_test_info(
#                 cur, tdms_obj, add_setting_info(cur, tdms_obj))
#             # print("TestID = ", test_id)
#             for obs_idx in range(len(tdms_obj.object("Data", "Idx").data)):
#                 obs_id = add_obs_info(cur, tdms_obj, test_id, obs_idx)
#         #        add_temp(cur, tdms_obj, obs_id, obs_idx)
#     # if not test:
#     #    move_files(directory)
