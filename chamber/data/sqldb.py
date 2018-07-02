"""
MySQL and TDMS Integration.

Functions
---------
    connect
    create_tables
    add_setting_info

"""
import configparser
import re

from CoolProp.HumidAirProp import HAPropsSI
import mysql.connector
import nptdms
import numpy as np
from scipy import stats

from chamber import const
from chamber.data import ddl, dml


# ----------------------------------------------------------------------------
# Connect to database


def connect(database):
    """
    Use config file to return connection and cursor to a MySQL database.

    The host, username, and password are all stored in config.ini in the root
    of the repository. Make sure to edit this file so that it contains your
    information.

    Parameters
    ----------
    database : str
        Name of the database for which to return a cursor.

    Returns
    -------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.
    cur : mysql.connector.cursor.MySqlCursor
        Cursor for MySQL database.

    Examples
    --------
    Obtain a connection and cursor to a schema named 'test' using built in
    config.ini:

    >>> cnx, cur = connect('test')
    >>> type(cnx)
    <class 'mysql.connector.connection.MySQLConnection'>
    >>> type(cur)
    <class 'mysql.connector.cursor.MySQLCursor'>

    """
    # Parse the 'MySQL-Server' section of the config file.
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
    config = dict(config_parser['MySQL-Server'])
    config['database'] = database

    # Try to connect
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print(
                "Something is wrong with your username or "
                "password: {}".format(err)
                )
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist {}".format(err))
        else:
            print(err)
    else:
        return cnx, cnx.cursor()


# ----------------------------------------------------------------------------
# `Setting` Table


def _get_setting_info(tdms_obj):
    """
    Use TDMS file to return initial state of test.

    This function searches through the nptdms.TdmsFile object for the initial
    settings including: Duty, Pressure, and Temperature. These settings are
    returned in the form of a dictionary with the keys: 'Duty', 'Pressure',
    and 'Temperature' respectively. This dictionaty can then be used as an
    input to the `add_setting` function.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        Object containg the data from the tdms test file. Original tdms files
        were created from UCSD Chamber experiments in the Coimbra Lab in SERF
        159.

    Returns
    -------
    setting_info : dict of {str: scalar}
        Set of values to insert into the Setting table. Keys should be column
        names and values should be the value to insert.

    Examples
    --------
    Get the settings from tdms file:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> get_setting_info(tdms_file)
    {'Duty': '5.0', 'Pressure': 100000, 'Temperature': 285}

    """
    # ------------------------------------------------------------------------
    # Read thermocouples 4-14, average, and round to nearest 5 K
    avg_temp = (
        sum(float(get_temp_info(tdms_obj, 0, i)) for i in range(4, 14))/10
        )
    rounded_temp = 5*round(avg_temp/5)

    # ------------------------------------------------------------------------
    # Read duty and round to nearest 0.1 %
    duty = tdms_obj.object('Settings', 'DutyCycle').data[0]
    rounded_duty = '{:.1f}'.format(round(duty, 1))

    # ------------------------------------------------------------------------
    # Read pressure and round to nearest 5 kPa
    pressure = tdms_obj.object('Data', 'Pressure').data[0]
    rounded_pressure = 5000*round(float(pressure)/5000)

    # ------------------------------------------------------------------------
    # Construct dictionary to return
    setting_info = dict(
        Duty=rounded_duty, Pressure=rounded_pressure, Temperature=rounded_temp
        )

    return setting_info


def _setting_exists(cur, setting_info):
    """
    Check if the settings exist in the database.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    setting_info : dict of {str : scalar}
        Experimental settings of to check for in database. Keys are column
        names from the Setting table and values are numerical values to
        insert.

    Returns
    -------
    setting_id : int or False
        SettingID for the MySQL database if it exists, False otherwise.

    Examples
    --------
    Obtain a setting ID that already exists:

    >>> _, cur = connect('my-schema')
    >>> setting_info = dict(Duty=10, Pressure=100000, Temperature=300)
    >>> setting_id = setting_exists(cur, setting_info)
    >>> setting_id
    1

    Attempt to obtain a setting ID that doesn't exist:
    >>> setting_info['Duty'] = 20
    >>> setting_id = setting_exists(cur, setting_info)
    >>> setting_id
    False

    """
    # ------------------------------------------------------------------------
    # Query the settings table and fetch the result
    cur.execute(dml.select_setting, setting_info)
    result = cur.fetchall()

    # ------------------------------------------------------------------------
    # Return the setting id or False
    if not result:
        return False
    else:
        setting_id = result[0][0]
        return setting_id


def add_setting_info(cur, tdms_obj):
    """
    Use a MySQL cursor and a TDMS file to add setting info into database.

    Uses cursor's .execute function on a MySQL insert query and dictionary of
    Setting data built by the get_setting method. Adds the new Setting if the
    setting doesn't exist and returns the SettingID form the MySQL database.
    If the setting already exists, then the SettingID of that setting is
    returned.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    tdms_obj : nptdms.TdmsFile
        Object containg the data from the tdms test file. Original tdms files
        were created from UCSD Chamber experiments in the Coimbra Lab in SERF
        159.

    Returns
    -------
    setting_id : int
        SettingID for the MySQL database, which is primary key for the Setting
        table.

    Examples
    --------
    Add the setting info for a given file and get its id:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> _, cur = connect('my-schema')
    >>> setting_id = add_setting_info(cur, tdms_file)
    >>> setting_id
    1

    """
    # ------------------------------------------------------------------------
    # Get the setting into from the tdsm file
    setting_info = _get_setting_info(tdms_obj)

    # ------------------------------------------------------------------------
    # Check if the setting id already exists
    setting_id = _setting_exists(cur, setting_info)

    # ------------------------------------------------------------------------
    # If the setting didn't exist, add it, and return the new setting id.
    if not setting_id:
        cur.execute(dml.add_setting, setting_info)
        setting_id = cur.lastrowid

    return setting_id


# ----------------------------------------------------------------------------
# `Test` Table


def _get_test_info(tdms_obj):
    """
    Use TDMS file to return test details.

    Builds a dictionary containing the initial state of test in the
    nptdms.TdmsFile.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        Object containg the data from the tdms test file. Original tdms files
        were created from UCSD Chamber experiments in the Coimbra Lab in SERF
        159.

    Returns
    -------
    test_info : dict of {str: str}
        Set of values to insert into the Test table. Keys should be column
        names and values should be the value to insert.

    Examples
    --------
    Get the initial state of the test from the tdms file:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> get_test_info(tdms_file)
    {'Description': 'description', 'TimeStep': 1, 'IsMass': 1, 'Author':
    'RHI', 'DateTime': datetime.datetime(2018, 1, 29, 17, 54, 12)}

    """
    # ------------------------------------------------------------------------
    # Construct the test_info dictionary with the exception of the `Author`
    # and `Description` fields, which will be filled below
    test_info = dict(
        Author='',
        DateTime=(
            tdms_obj.object().properties['DateTime']
            .replace(microsecond=0).replace(tzinfo=None)
            ),
        Description='',
        IsMass=int(tdms_obj.object("Settings", "IsMass").data[0]),
        TimeStep=int(tdms_obj.object("Settings", "TimeStep").data[0])
        )

    # ------------------------------------------------------------------------
    # Now iterate through properties and look for `Author` and `Description`
    for name, value in tdms_obj.object().properties.items():
        if name == "author":
            test_info['Author'] = value
        elif name == "description":
            test_info['Description'] = value[:1000]

    return test_info


def _test_exists(cur, test_info):
    """
    Check if a test already exists.

    Uses the test_info dictionary where the keys are the columns in the Test
    table and the values are the string values. The cursor executes a DML
    SELECT statement and returns the TestID if the test exists or False if no
    test matching the query exists.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    test_info : dict of {str: str or int or datetime.datetime}
        Test settings to check for in database. Keys are column names from
        the Test table and values should be the value to insert.

    Returns
    -------
    test_id : int or False
        This is the primary key for the Test table if the test already exists.
        If the test does not exist in the database the function returns False.

    Examples
    --------
    Check for test info that already exists in the database:

    >>> import datetime
    >>> _, cur = connect('my_schema')
    >>> test_info = dict(Author='author_01',
    ... DateTime=datetime.datetime(2018, 1, 29, 17, 54, 12),
    ... Description='description_01', IsMass=1, TimeStep=1)
    >>> test_exists(cur, test_info)
    1

    Check for test info that does not exist in the database:

    >>> test_info['Author'] = 'foo'
    >>> test_exists(cur, test_info)
    False

    Todo
    ----
    Raise exception rather than print message.

    """
    # ------------------------------------------------------------------------
    # If there is no test info print a message to the user, this should really
    # raise an exception; See Todo in docstring
    if not test_info:
        print("No test info: File Unable to Transfer")
        return False

    # ------------------------------------------------------------------------
    # Querry the data base to see if the test exists in the database and fetch
    # the results
    cur.execute(dml.select_test.format(
        test_info['DateTime'].replace(microsecond=0).replace(tzinfo=None))
        )
    result = cur.fetchall()

    if not result:
        return False
    else:
        return result[0][0]


# ----------------------------------------------------------------------------
# Still to be organized


def create_tables(cur, tables):
    """
    Create tables in the database.

    Uses a list of tuples where the 0 index is the name of the table and the 1
    index is a string of MySQL DDL used to create the table. A list is required
    so that the DDL can be executed in order to avoid foreign key constraint
    errors.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    tables : list of tuple of (str, str)
        List of tuples of table names and DDL query language. For example:
        [('UnitTest',
        "CREATE TABLE `UnitTest` ("
        "    `UnitTestID` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
        "    `Number` DECIMAL(5,2) NULL,"
        "    `String` VARCHAR(30) NULL,"
        "  PRIMARY KEY (`UnitTestID`)"
        ");"))]

    Returns
    -------
    bool
        `True` if successful.

    Examples
    --------
    Create tables in the MySQL database:

    >>> from chamebr.database import ddl
    >>> _, cur = connect('my-schema')
    >>> status = create_tables(cur, ddl.tables)
    Setting up tables...
    Setting  OK
    Tube  OK
    Test  OK
    Observation  OK
    TempObservation  OK
    Unit  OK
    >>> status
    True

    """
    print('Setting up tables...')
    for table in tables:
        name, ddl = table
        try:
            cur.execute(ddl)
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                print(name, 'already exists.')
            else:
                print(err.msg)
        else:
            print(table[0], ' OK')
    return True


def get_temp_info(tdms_obj, tdms_idx, couple_idx):
    """
    Get thermocouple observations.

    Returns temperature data for the provided index (time) and thermocouple
    index.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        Object containg the data from the tdms test file. Original tdms files
        were created from UCSD Chamber experiments in the Coimbra Lab in SERF
        159.
    tdms_idx : int
        Index in the tdms file representing a single time.
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

    Examples
    --------
    Get the temperature measurement from index 1 and thermocouple 4:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> get_temp_info(tdms_file, 1, 4)
    '280.24'

    """
    regex = re.compile(r'^(\d){3}.(\d){2}$')
    temp_info = '{:.2f}'.format(
        tdms_obj.object("Data", "TC{}".format(couple_idx)).data[tdms_idx])
    if not regex.search(temp_info):
        return
    return temp_info


def get_obs_info(tdms_obj, tdms_idx):
    """
    Use TDMS file and index to return observation info.

    Builds a dictionary containing the observation for a given index (time) in
    the nptdms.TdmsFile object.

    It is important to note here that tdms_idx is NOT the same as the Idx
    comumn in the MySQL schema. Because the tdms files are read in using
    `nptdms` data is converted into arrays of type `np.ndarray`. As a result,
    I can use the tdms_idx as a proxy for the idx column in the tdms file.

    Parameters
    ----------
    tdms_obj : nptdms.TdmsFile
        Object containg the data from the tdms test file. Original tdms files
        were created from UCSD Chamber experiments in the Coimbra Lab in SERF
        159.
    tdms_idx : int
        Index in the tdms file representing a single time.

    Returns
    -------
    obs_info : dict of {str: str or int}
        Set of values to insert into the Observation table. Keys should be
        column names and values should be the value to insert.

    Examples
    --------
    Get the observation information from index 10:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> get_obs_info(tdms_file, 10)
    {'DewPoint': '270.69', 'Idx': 8, 'Mass': '0.0985090', 'CapManOk': 1,
    'Pressure': 100393, 'OptidewOk': 1, 'PowRef': '-0.0003', 'PowOut':
    '-0.0003'}

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


def add_tube_info(cur):
    """
    Use a MySQL cursor to add test-independant Tube info.

    Uses cursor .execute function on the ADD_TUBE and TUBE_DATA constants in
    ddl.py. Adds the new Tube if the Tube doesn't exist. If the Tube already
    exists, then the function does nothing.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.

    Returns
    -------
    bool
        `True` if tube added, `False` if tube already exists in database.

    Examples
    --------
    Add the tube for the first time:

    >>> _, cur = connect('my-schema')
    >>> status = add_tube_info(cur)
    Tube added.
    >>> status
    True

    Now add it again:

    >>> status = add_tube_info(cur)
    Tube already exists.
    >>> status
    False

    """
    cur.execute(dml.select_tube, ddl.tube_data)
    if not cur.fetchall():
        cur.execute(dml.add_tube, ddl.tube_data)
        print('Tube added.')
        return True
    else:
        print('Tube already exists.')
        return False


def add_test_info(cur, tdms_obj, setting_id):
    """
    Use a MySQL cursor, TDMS file and setting_id to add test info.

    Uses cursor's .execute function on a MySQL insert query and dictionary of
    Test data built by get_test using the argument nptdms.TdmsFile. Adds the
    foreign key SettingID to the dictionary before executing the MySQL query.

     Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    tdms_obj : nptdms.TdmsFile
        Object containg the data from the tdms test file. Original tdms files
        were created from UCSD Chamber experiments in the Coimbra Lab in SERF
        159.
    setting_id : int
        SettingID for the MySQL database, which is primary key for the Setting
        table.

    Returns
    -------
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.

    Examples
    --------
    Add the test info for a given file and get its id:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> _, cur = connect('my-schema')
    >>> test_id = add_test_info(cur, tdms_file)
    >>> test_id
    1

    """
    test_info = _get_test_info(tdms_obj)
    test_id = _test_exists(cur, test_info)
    if not test_id:
        test_info["SettingID"] = setting_id
        test_info["TubeID"] = str(
            tdms_obj.object("Settings", "TubeID").data[0])
        cur.execute(dml.add_test, test_info)
        test_id = cur.lastrowid
    return test_id


def add_obs_info(cur, tdms_obj, test_id, tdms_idx):
    """
    Add an observation to the database.

    Uses cursor's .execute function on a MySQL insert query and dictionary of
    observation data built by get_obs using the argument nptdms.TdmsFile and
    index. Adds the foreign key TestID to the dictionary before executing the
    MySQL query.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    tdms_obj : nptdms.TdmsFile
        Object containg the data from the tdms test file. Original tdms files
        were created from UCSD Chamber experiments in the Coimbra Lab in SERF
        159.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.
    tdms_idx : int
        Index in the tdms file representing a single time.

    Returns
    -------
    `True` or `None`
        `True` if successful. Else `None`.

    Examples
    --------
    Add a single observation at test_idx 1 from a file with test_id 1:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> _, cur = connect('my-schema')
    >>> assert add_obs_info(cur, tdms_file, 1, 0)

    Add all observations in a file with test_id 2:

    >>> for i in range(len(tdms_file.object("Data", "Idx").data)):
    ...     assert add_obs_info(cur, tdms_file, 2, i)

    """
    obs_info = get_obs_info(tdms_obj, tdms_idx)
    obs_info['TestId'] = test_id
    if tdms_obj.object("Settings", "IsMass").data[0] == 1:
        cur.execute(dml.add_obs_m_t, obs_info)
        return True
    else:
        cur.execute(dml.add_obs_m_f, obs_info)
        return True


def add_temp_info(cur, tdms_obj, test_id, tdms_idx, idx):
    """
    Add a temperature observation to the database.

    Uses cursor's .execute function on a MySQL insert query and dictionary of
    TempObservation data built by looping through get_temp_info for each
    thermocouple using the argument nptdms.TdmsFile and index. Adds the foreign
    key ObservationID to the dictionary before executing the MySQL query.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    tdms_obj : nptdms.TdmsFile
        Object containg the data from the tdms test file. Original tdms files
        were created from UCSD Chamber experiments in the Coimbra Lab in SERF
        159.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.
    tdms_idx : int
        Index in the tdms file representing a single time.
    idx : int
        Idx for the MySql database, which is part of the composite primary key
        in the the Observation table.

    Returns
    -------
    `True` or `None`
        `True` if successful. Else `None`.

    Examples
    --------
    Add temperature from observations a tdms file where the `test_id` is 1,
    `tdms_index` is 0, and the `idx` is 99:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> _, cur = connect('my-schema')
    >>> assert add_temp_info(cur, tdms_file, 1, 0, 99)

    """
    if tdms_obj.object("Settings", "IsMass").data[0] == 1:
        initial_tc_index = 4
    else:
        initial_tc_index = 0

    temp_data = [
        (
            couple_idx,
            get_temp_info(tdms_obj, tdms_idx, couple_idx),
            idx,
            test_id
        )
        for couple_idx
        in range(initial_tc_index, 14)
        ]

    cur.executemany(dml.add_temp, temp_data)

    return True


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
    tdms_obj = nptdms.TdmsFile(file_name)
    if not _test_exists(cur, _get_test_info(tdms_obj)):
        # print("WE GOT IN THE LOOP")
        test_id = add_test_info(cur, tdms_obj, add_setting_info(cur, tdms_obj))
        # print("TestID = ", test_id)
        for tdms_idx in range(len(tdms_obj.object("Data", "Idx").data)):
            add_obs_info(cur, tdms_obj, test_id, tdms_idx)
        #   add_temp(cur, tdms_obj, obs_id, obs_idx)
    # if not test:
    #    move_files(directory)


# Not-Reviewed

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
#         tdms_obj = nptdms.TdmsFile(file_name)
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


# DEPRECIATED DEPRECIATED DEPRECIATED DEPRECIATED DEPRECIATED
# DEPRECIATED DEPRECIATED DEPRECIATED DEPRECIATED DEPRECIATED
# DEPRECIATED DEPRECIATED DEPRECIATED DEPRECIATED DEPRECIATED
# DEPRECIATED DEPRECIATED DEPRECIATED DEPRECIATED DEPRECIATED

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
#         regex = re.compile(r".tdms$")
#         if regex.search(file_path):
#             return file_list.append(file_path)
#     return file_list

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
