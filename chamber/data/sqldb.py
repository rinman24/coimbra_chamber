"""
MySQL and TDMS Integration.

Functions
---------
- `add_tdms_file` -- Insert tdms files into the MySQL database.
- `add_tube_info` -- Add test-independant Tube information.
- `connect` -- Get a connection and cursor to a MySQL database.
- `create_tables` -- Create tables in the database.
- `get_test_dict` -- Create `DataFrame` representations of the tests.
- `get_test_from_set` -- Get a list of TestIds corresponding to setting info.
- `add_analysis` -- Pull, analyze, and insert analysis results into database.


.. todo:: Decouple database and tdms volatility via modulde encapsulation.
"""
import configparser
import re

from CoolProp.HumidAirProp import HAPropsSI
import mysql.connector
import nptdms
import numpy as np
import pandas as pd
from scipy import stats
from tqdm import tqdm

from chamber import const
from chamber.analysis import experiments
from chamber.data import ddl, dml


# ----------------------------------------------------------------------------
# Connect and setup


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

    Examples
    --------
    Obtain a connection and cursor to a schema named 'test' using built in
    config.ini:

    >>> cnx = connect('test')
    >>> type(cnx)
    <class 'mysql.connector.connection.MySQLConnection'>

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
        return cnx


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
    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> assert create_tables(cur, ddl.tables)
    Setting up tables...
    Setting  OK
    Tube  OK
    Test  OK
    Observation  OK
    TempObservation  OK
    Unit  OK

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


# ----------------------------------------------------------------------------
# `Tube` Table


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

    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> assert add_tube_info(cur)
    Tube added.

    Now add it again:

    >>> assert not add_tube_info(cur)
    Tube already exists.

    """
    # First query if the tube exists
    cur.execute(dml.select_tube, ddl.tube_data)

    # If the tube does not exist, add it
    # Else, it already exists.
    if not cur.fetchall():
        cur.execute(dml.add_tube, ddl.tube_data)
        print('Tube added.')
        return True
    else:
        print('Tube already exists.')
        return False


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
    >>> _get_setting_info(tdms_file)
    {'Reservoir': 0, 'Duty': '0.0', 'IsMass': 0, 'Temperature': 290,
    'TimeStep': '1.00', 'Pressure': 100000, 'TubeId': 1}

    """
    # ------------------------------------------------------------------------
    # Read thermocouples 4-14, average, and round to nearest 5 K
    avg_temp = (
        sum(float(_get_temp_info(tdms_obj, 0, i)) for i in range(4, 14))/10
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
    # Read IsMass
    is_mass = int(tdms_obj.object('Settings', 'IsMass').data[0])

    # ------------------------------------------------------------------------
    # Read Reservoir
    reservoir = int(tdms_obj.object('Settings', 'Reservoir').data[0])

    # ------------------------------------------------------------------------
    # Read TubeId
    tube_id = int(tdms_obj.object('Settings', 'TubeID').data[0])

    # ------------------------------------------------------------------------
    # Read TimeStep
    time_step = tdms_obj.object("Settings", "TimeStep").data[0]
    time_step_str = '{:.2f}'.format(round(time_step, 2))

    # ------------------------------------------------------------------------
    # Construct dictionary to return
    setting_info = dict(
        Duty=rounded_duty, IsMass=is_mass, Pressure=rounded_pressure,
        Reservoir=reservoir, Temperature=rounded_temp, TimeStep=time_step_str,
        TubeId=tube_id
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

    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> setting_info = dict(Duty=10, Pressure=100000, Temperature=300)
    >>> setting_id = _setting_exists(cur, setting_info)
    >>> setting_id
    1

    Attempt to obtain a setting ID that doesn't exist:
    >>> setting_info['Duty'] = 20
    >>> setting_id = _setting_exists(cur, setting_info)
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


def _add_setting_info(cur, tdms_obj):
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
    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> setting_id = _add_setting_info(cur, tdms_file)
    >>> setting_id
    1

    """
    # ------------------------------------------------------------------------
    # Get the setting info from the tdsm file
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
    >>> _get_test_info(tdms_file)
    {'Description': 'description', 'Author': 'RHI', 'DateTime':
    datetime.datetime(2018, 1, 29, 17, 54, 12)}

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
    >>> cnx = connect('my_schema')
    >>> cur = cnx.cursor()
    >>> test_info = dict(Author='author_01',
    ... DateTime=datetime.datetime(2018, 1, 29, 17, 54, 12),
    ... Description='description_01', IsMass=1, TimeStep=1)
    >>> _test_exists(cur, test_info)
    1

    Check for test info that does not exist in the database:

    >>> test_info['Author'] = 'foo'
    >>> _test_exists(cur, test_info)
    False

    .. todo:: Raise exception rather than print message.

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


def _add_test_info(cur, tdms_obj, setting_id):
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
    Add the test info for a given file with setting id 1 and tube id 2:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> test_id = _add_test_info(cur, tdms_file, 1, 2)
    >>> test_id
    1

    """
    # ------------------------------------------------------------------------
    # Get the test info from the tdsm file
    test_info = _get_test_info(tdms_obj)

    # ------------------------------------------------------------------------
    # Check if the test id already exists
    test_id = _test_exists(cur, test_info)

    # ------------------------------------------------------------------------
    # If the test id didn't exist, add it, and return the new setting id.
    # NOTE: It is important to point out that if the test id doen't already
    #       exist then the foreign key `SettingID` must also be added because
    #       it is not contained in the `test_info`.
    if not test_id:
        test_info["SettingID"] = setting_id
        cur.execute(dml.add_test, test_info)
        test_id = cur.lastrowid
    return test_id


# ----------------------------------------------------------------------------
# `Observation` Table


def _get_obs_info(tdms_obj, tdms_idx):
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
    >>> _get_obs_info(tdms_file, 10)
    {'DewPoint': '270.69', 'Idx': 8, 'Mass': '0.0985090', 'CapManOk': 1,
    'Pressure': 100393, 'OptidewOk': 1, 'PowRef': '-0.0003', 'PowOut':
    '-0.0003'}

    """
    # ------------------------------------------------------------------------
    # Construct the obs_info dictionary
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

    # ------------------------------------------------------------------------
    # If the setting IsMass is True, then also add mass
    if tdms_obj.object("Settings", "IsMass").data[0] == 1:
        obs_info['Mass'] = '{:.7f}'.format(
            tdms_obj.object("Data", "Mass").data[tdms_idx])

    return obs_info


def _add_obs_info(cur, tdms_obj, test_id, tdms_idx):
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
    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> assert _add_obs_info(cur, tdms_file, 1, 0)

    Add all observations in a file with test_id 2:

    >>> for i in range(len(tdms_file.object("Data", "Idx").data)):
    ...     assert add_obs_info(cur, tdms_file, 2, i)

    """
    # ------------------------------------------------------------------------
    # Get the observation info from the tdms file
    obs_info = _get_obs_info(tdms_obj, tdms_idx)
    # Add the test id to the dictionary of observation info
    obs_info['TestId'] = test_id

    # If the test is a mass test, then include mass info
    # Else, don't consider mass.
    if tdms_obj.object("Settings", "IsMass").data[0] == 1:
        cur.execute(dml.add_obs_m_t, obs_info)
        return True
    else:
        cur.execute(dml.add_obs_m_f, obs_info)
        return True


# ----------------------------------------------------------------------------
# `TempObservation` Table

def _get_temp_info(tdms_obj, tdms_idx, couple_idx):
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
    >>> _get_temp_info(tdms_file, 1, 4)
    '280.24'

    """
    # ------------------------------------------------------------------------
    # Compile a regular expression to use when obtaining TC obervations
    regex = re.compile(r'^(\d){3}.(\d){2}$')
    # Get and format the temperature observation
    temp_info = '{:.2f}'.format(
        tdms_obj.object("Data", "TC{}".format(couple_idx)).data[tdms_idx])
    if not regex.search(temp_info):
        return
    return temp_info


def _add_temp_info(cur, tdms_obj, test_id, tdms_idx, idx):
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
    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> assert _add_temp_info(cur, tdms_file, 1, 0, 99)

    """
    # ------------------------------------------------------------------------
    # If this is a mass test, we want to disregard thermocouples 0-3.
    if tdms_obj.object("Settings", "IsMass").data[0] == 1:
        initial_tc_index = 4
    else:
        initial_tc_index = 0

    # Use a list comprehension to get all of the thermocouple data
    temp_data_list = [
        (
            couple_idx,
            _get_temp_info(tdms_obj, tdms_idx, couple_idx),
            idx,
            test_id
        )
        for couple_idx
        in range(initial_tc_index, 14)
        ]

    # Execute many using the temp_data_list
    cur.executemany(dml.add_temp, temp_data_list)

    return True

# ----------------------------------------------------------------------------
# Add all data, main function


def add_tdms_file(cnx, tdms_obj):
    """
    Insert tdms files into the MySQL database.

    Uses loops to structure calls to add_setting, add_test, add_obs, and
    add_temp to build and execute queries that populate the MySQL database for
    a single tdms_obj.

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
    `True` or `None`
        `True` if sucessful, else `None`.

    Examples
    --------
    Add a tdms file to a database using a MySQL cursor:

    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> cnx = connect('my-schema')
    >>> assert add_tdms_file(cnx, tdms_obj)

    """
    try:
        # --------------------------------------------------------------------
        # Create a cursor and start the transaction
        cur = cnx.cursor()
        assert not cnx.in_transaction

        # --------------------------------------------------------------------
        # Setting: call add_setting_info which will add the setting or make a
        # new setting and return the new id.
        setting_id = _add_setting_info(cur, tdms_obj)
        assert cnx.in_transaction
        print('SettingID:', setting_id)

        # --------------------------------------------------------------------
        # Test: call add_test_info which will add the test or make a new test
        # and return the new id.
        test_id = _add_test_info(cur, tdms_obj, setting_id)
        print('TestID:', test_id)

        # --------------------------------------------------------------------
        # Observation and TempObservations: call add_obs_info and
        # add_temp_info in a loop which will add all of the observations from
        # the file.
        for tdms_idx in tqdm(range(len(tdms_obj.object("Data", "Idx").data))):
            assert _add_obs_info(cur, tdms_obj, test_id, tdms_idx)
            idx = int(tdms_obj.object("Data", "Idx").data[tdms_idx])
            assert _add_temp_info(cur, tdms_obj, test_id, tdms_idx, idx)

        assert cnx.in_transaction
        cnx.commit()
        assert not cnx.in_transaction
        assert cur.close()
        return True
    except mysql.connector.Error as err:
        # --------------------------------------------------------------------
        # Rollback transaction if there is an issue
        cnx.rollback()
        print("MySqlError: {}".format(err))


def _get_test_dict(cnx, test_id):
    """
    Create `DataFrame` representations of the tests.

    Uses the pandas `DataFrame` object's `read_sql` method to build a
    dictionary containing a dataframe for joined Setting and Test tables and a
    dataframe for joined Observation and TempObservation tables.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.

    Returns
    -------
    dict(DataFrame)
        A `dict` of two `DataFrames`, one conaining joined 'Setting' and
        'Test' tables and antoher `DataFrame` containting joined Thermocouple
        readings and `Obseravation` tables.

    Examples
    --------
    Get the `dict` of `DataFrames` for a test with TestId=4.

    >>> cnx = connect('my-schema')
    >>> test_dict = get_test_dict(4, cnx)
    >>> print(test_dict['info']['author'].iloc[0])
    >>> author_1
    >>> test_dict['data']['TC2'].iloc[4]
    '293.01'

    """
    # Build DataFrames
    info_df = pd.read_sql(dml.get_info_df.format(test_id), con=cnx)
    temp_df = pd.read_sql(dml.get_temp_df.format(test_id), con=cnx)
    obs_df = pd.read_sql(dml.get_obs_df.format(test_id), con=cnx)
    data_df = temp_df.merge(obs_df)

    # Make dictionary
    test_dict = {'info': info_df, 'data': data_df}
    return test_dict


def get_test_from_set(cur, setting_info):
    """
    Get a list of TestIds corresponding to specified setting information.

    Uses cursor's .execute function on a MySQL querry designed to get a list
    of TestIds corresponding to the setting info provided in the setting_info
    argument.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    setting_info : dict of {str: scalar}
        Set of values to insert into the Setting table. Keys should be column
        names and values should be the value to insert.

    Returns
    -------
    list(int) or False
        TestIDs for the MySQL database, which is the primary key for the Test
        table. Returns `False` if no TestIds match the argument setting info.

    Examples
    --------
    Get the TestIds corresponding to a setting_info dict.

    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> setting_info = dict(
    Duty='0.0', IsMass=0, Pressure=100000, Reservoir=0, Temperature=290,
    TimeStep='1.00', TubeId=1)
    >>> get_test_from_set(cur, setting_info)
    '[1, 4]'

    """
    test_from_set = dml.test_from_setting.format(dml.select_setting)
    cur.execute(test_from_set, setting_info)
    result = cur.fetchall()
    if not result:
        return False
    else:
        test_ids = [test_id[0] for test_id in result]
        return test_ids


def _add_rh_targets(cur, analyzed_df, test_id):
    """
    Insert Chi2 RH results into MySql database RHTargets table.

    Uses cursor's .executemany function on a MySQL insert query and list
    of RH data built by looping through an analyzed `DataFrame` built by
    the `experiments.mass_transfer` function.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    analyzed_df: DataFrame
        Results of the analysis of the test.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.

    Returns
    -------
    `True` or `None`
        `True` if successful. Else `None`.

    Examples
    --------
    Add RH data for an existing TestId.

    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> test_id = 1
    >>> _add_rh_targets(cur, test_id)
    True

    """
    rh_trgt_list = [
        (test_id, '{:.2f}'.format(rh)) for rh in analyzed_df.RH.unique()
    ]
    cur.executemany(dml.add_rh_targets, rh_trgt_list)

    return True


def _add_results(cur, analyzed_df, test_id):
    """
    Insert Chi2 results into MySql database Results table.

    Uses cursor's .executemany function on a MySQL insert query and list
    of results data built by looping through an analyzed `DataFrame` built by
    the `experiments.mass_transfer` function.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    analyzed_df: DataFrame
        Results of the analysis of the test.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.

    Returns
    -------
    `True` or `None`
        `True` if successful. Else `None`.

    Examples
    --------
    Add results data for existing RHTargets.

    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> test_id = 1
    >>> _add_results(cur, test_id)
    True

    """
    results_list = [
        (
            test_id,
            float(analyzed_df.iloc[idx]['RH']),
            float(analyzed_df.iloc[idx]['a']),
            float(analyzed_df.iloc[idx]['sig_a']),
            float(analyzed_df.iloc[idx]['b']),
            float(analyzed_df.iloc[idx]['sig_b']),
            float(analyzed_df.iloc[idx]['chi2']),
            float(analyzed_df.iloc[idx]['Q']),
            float(analyzed_df.iloc[idx]['nu'])
        ) for idx in analyzed_df.index
    ]
    cur.executemany(dml.add_results, results_list)

    return True


def _add_best_fit(cur, test_id):
    """Docstring."""
    cur.execute(dml.add_best_fit.format(test_id))
    return True


def add_analysis(cnx, test_id):
    """
    Pull, analyze, and insert analysis results into MySQL database.

    Uses `experiments` module to analyze a `DataFrame` of data stored in MySQL
    database. Uses `add_rh_targets` and `add_results` to populate MySQL
    databse RHTargest and Results tables.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.

    Returns
    -------
    `True` or `None`
        `True` if sucessful, else `None`.

    Examples
    --------
    Add analysis results for an existing TestId.

    >>> cnx = connect('my-schema')
    >>> test_id = 1
    >>> add_analysis(cnx, test_id)
    True

    """
    # --------------------------------------------------------------------
    # Create a DataFrame of analyzed data
    test_dict = _get_test_dict(cnx, test_id)
    processed_df = experiments.preprocess(test_dict['data'], purge=True)
    analyzed_df = experiments.mass_transfer(processed_df)
    try:
        # --------------------------------------------------------------------
        # Create a cursor and start the transaction
        cur = cnx.cursor()
        assert cnx.in_transaction

        # --------------------------------------------------------------------
        # RHTargets: call add_rh_targets
        _add_rh_targets(cur, analyzed_df, test_id)
        assert cnx.in_transaction
        cnx.commit()
        assert not cnx.in_transaction

        # --------------------------------------------------------------------
        # Results: call add_results
        _add_results(cur, analyzed_df, test_id)
        assert cnx.in_transaction
        cnx.commit()
        assert not cnx.in_transaction

        _add_best_fit(cur, test_id)
        assert cnx.in_transaction
        cnx.commit()
        assert not cnx.in_transaction

        assert cur.close()

        return True
    except mysql.connector.Error as err:
        # --------------------------------------------------------------------
        # Rollback transaction if there is an issue
        cnx.rollback()
        print("MySqlError: {}".format(err))
