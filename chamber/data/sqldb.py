"""
MySQL and TDMS Integration.

Functions
---------
- `add_tdms_file` -- Insert tdms files into the MySQL database.
- `add_tube_info` -- Add test-independant Tube information.
- `connect` -- Get a connection and cursor to a MySQL database.
- `create_tables` -- Create tables in the database.
- `get_high_low_testids` -- Get Low and High RH TestIds for a p and t setting.
- `get_rht_results` Get `DataFrame` of evap reate and RH results for a TestId.
- `get_test_dict` -- Create `DataFrame` representations of the tests.
- `add_analysis` -- Pull, analyze, and insert analysis results into database.


.. todo:: Decouple database and tdms volatility via modulde encapsulation.
"""
import configparser
import os
import re

from CoolProp.HumidAirProp import HAPropsSI
import matplotlib.pyplot as plt
import mysql.connector
import nptdms
import numpy as np
import pandas as pd
from scipy import stats
from tqdm import tqdm

from chamber.analysis import experiments

# ----------------------------------------------------------------------------
# MySQL DDL constants
# ----------------------------------------------------------------------------
TABLES = list()

# 'Tube' table ddl
TABLES.append(("Tube",
               "CREATE TABLE IF NOT EXISTS `Tube` ("
               "  `TubeId` TINYINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,"
               "  `DiameterIn` DECIMAL(7,7) UNSIGNED NOT NULL,"
               "  `DiameterOut` DECIMAL(7,7) UNSIGNED NOT NULL,"
               "  `Length` DECIMAL(4,4) UNSIGNED NOT NULL,"
               "  `Material` VARCHAR(50) NOT NULL,"
               "  `Mass` DECIMAL(7,7) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`TubeId`))"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))

# 'Setting' table ddl
TABLES.append(("Setting",
               "CREATE TABLE IF NOT EXISTS `Setting` ("
               "  `SettingId` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,"
               "  `Duty` DECIMAL(4,1) UNSIGNED NOT NULL,"
               "  `IsMass` BIT(1) NOT NULL,"
               "  `Pressure` MEDIUMINT(6) UNSIGNED NOT NULL,"
               "  `Temperature` DECIMAL(4,1) UNSIGNED NOT NULL,"
               "  `TimeStep` DECIMAL(4,2) UNSIGNED NOT NULL,"
               "  `Reservoir` BIT(1) NOT NULL,"
               "  `TubeId` TINYINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`SettingId`, `TubeId`),"
               "  INDEX `fk_Setting_Tube1_idx` (`TubeId` ASC),"
               "  CONSTRAINT `fk_Setting_Tube`"
               "    FOREIGN KEY (`TubeId`)"
               "    REFERENCES `Tube` (`TubeId`)"
               "    ON DELETE RESTRICT"
               "    ON UPDATE CASCADE) "
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))

# 'Test' table ddl
TABLES.append(("Test",
               "CREATE TABLE IF NOT EXISTS `Test` ("
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,"
               "  `Author` VARCHAR(50) NOT NULL,"
               "  `DateTime` DATETIME NOT NULL,"
               "  `Description` VARCHAR(1000) NOT NULL,"
               "  `SettingId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`TestId`, `SettingId`),"
               "  INDEX `fk_Test_Setting_idx` (`SettingId` ASC),"
               "  CONSTRAINT `fk_Test_Setting`"
               "    FOREIGN KEY (`SettingId`)"
               "    REFERENCES `Setting` (`SettingId`)"
               "    ON DELETE RESTRICT"
               "    ON UPDATE CASCADE)"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))

# 'Observation' table ddl
TABLES.append(("Observation",
               "CREATE TABLE IF NOT EXISTS `Observation` ("
               "  `CapManOk` BIT(1) NOT NULL,"
               "  `DewPoint` DECIMAL(5,2) UNSIGNED NOT NULL,"
               "  `Idx` MEDIUMINT(6) UNSIGNED NOT NULL,"
               "  `Mass` DECIMAL(7,7) UNSIGNED NULL DEFAULT NULL,"
               "  `OptidewOk` BIT(1) NOT NULL,"
               "  `PowOut` DECIMAL(6,4) NULL DEFAULT NULL,"
               "  `PowRef` DECIMAL(6,4) NULL DEFAULT NULL,"
               "  `Pressure` MEDIUMINT(6) UNSIGNED NOT NULL,"
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`Idx`, `TestId`),"
               "  INDEX `fk_Observation_Test_idx` (`TestId` ASC),"
               "  CONSTRAINT `fk_Observation_Test`"
               "    FOREIGN KEY (`TestId`)"
               "    REFERENCES `Test` (`TestId`)"
               "    ON UPDATE CASCADE)"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))

# 'TempObservation' table ddl
TABLES.append(("TempObservation",
               "CREATE TABLE IF NOT EXISTS `TempObservation` ("
               "  `ThermocoupleNum` TINYINT(2) UNSIGNED NOT NULL,"
               "  `Temperature` DECIMAL(5,2) NOT NULL,"
               "  `Idx` MEDIUMINT(6) UNSIGNED NOT NULL,"
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`Idx`, `TestId`, `ThermocoupleNum`),"
               "  CONSTRAINT `fk_TempObservation_Observation`"
               "    FOREIGN KEY (`Idx` , `TestId`)"
               "    REFERENCES `Observation` (`Idx` , `TestId`)"
               "    ON UPDATE CASCADE)"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))

# 'RHTargets' table ddl
TABLES.append(("RHTargets",
               "  CREATE TABLE IF NOT EXISTS `RHTargets` ("
               "  `RH` DECIMAL(3,2) UNSIGNED NOT NULL,"
               "  `SigRH` FLOAT UNSIGNED NOT NULL,"
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  `Nu` SMALLINT UNSIGNED,"
               "  `PressureSmooth` FLOAT NOT NULL,"
               "  `DewPointSmooth` FLOAT NOT NULL,"
               "  `TemperatureSmooth` FLOAT NOT NULL,"
               "  `SpaldMdpp` FLOAT NOT NULL,"
               "  `SpaldMdppUnc` FLOAT NOT NULL,"
               "  `SpaldTs` FLOAT NOT NULL,"
               "  PRIMARY KEY (`RH`, `TestId`),"
               "  INDEX `fk_RHTargets_Test_idx` (`TestId` ASC),"
               "  CONSTRAINT `fk_RHTargets_Test`"
               "    FOREIGN KEY (`TestId`)"
               "    REFERENCES `Test` (`TestId`)"
               "    ON DELETE RESTRICT"
               "    ON UPDATE CASCADE)"
               " ENGINE = InnoDB;"))

# 'Results' table ddl
TABLES.append(("Results",
               "  CREATE TABLE IF NOT EXISTS `Results` ("
               "  `RH` DECIMAL(3,2) UNSIGNED NOT NULL,"
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  `A` FLOAT NOT NULL,"
               "  `SigA` FLOAT UNSIGNED NOT NULL,"
               "  `B` FLOAT NOT NULL,"
               "  `SigB` FLOAT UNSIGNED NOT NULL,"
               "  `Chi2` FLOAT UNSIGNED NOT NULL,"
               "  `Q` DECIMAL(3,2) UNSIGNED NOT NULL,"
               "  `Nu` SMALLINT UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`Nu`, `RH`, `TestId`),"
               "  CONSTRAINT `fk_Results_RHTargets1`"
               "    FOREIGN KEY (`RH` , `TestId`)"
               "    REFERENCES `RHTargets` (`RH` , `TestId`)"
               "    ON DELETE RESTRICT"
               "    ON UPDATE CASCADE)"
               "ENGINE = InnoDB;"))

# 'Unit' table ddl
TABLES.append(("Unit",
               "CREATE TABLE IF NOT EXISTS `Unit` ("
               "  `Duty` VARCHAR(50) NOT NULL,"
               "  `Length` VARCHAR(50) NOT NULL,"
               "  `Mass` VARCHAR(50) NOT NULL,"
               "  `Power` VARCHAR(50) NOT NULL,"
               "  `Pressure` VARCHAR(50) NOT NULL,"
               "  `Temperature` VARCHAR(50) NOT NULL,"
               "  `Time` VARCHAR(50) NOT NULL)"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))

# Convert tables list to immutable tuple
TABLES = tuple(TABLES)

# Constant for Table Drop
TABLE_NAME_LIST = [table[0] for table in reversed(TABLES)]


# Default tube
TUBE_DATA = dict(
    DiameterIn=0.03, DiameterOut=0.04, Length=0.06, Material='Delrin',
    Mass=0.0873832
    )

# Default units
UNITS = dict(
    Duty='Percent', Length='Meter', Mass='Kilogram', Power='Watt',
    Pressure='Pascal', Temperature='Kelvin', Time='Second'
    )

# ----------------------------------------------------------------------------
# MySQL DML insert and update statement constants
# ----------------------------------------------------------------------------
# dml to add data into the 'Setting' table
ADD_SETTING = ("INSERT INTO Setting "
               "(Duty, IsMass, Pressure, Reservoir, Temperature, TimeStep,"
               " TubeId)"
               " VALUES "
               "(%(Duty)s, %(IsMass)s, %(Pressure)s, %(Reservoir)s, "
               "%(Temperature)s, %(TimeStep)s, %(TubeId)s)")

# dml to add data into the 'test' table
ADD_TEST = ("INSERT INTO Test "
            "(Author, DateTime, Description,"
            " SettingID)"
            " VALUES "
            "(%(Author)s, %(DateTime)s, %(Description)s,"
            " %(SettingID)s)")

# dml to add data from a file into the specfied table
LOAD_DATA = ("LOAD DATA LOCAL INFILE '_data.csv' INTO TABLE "
             "{} FIELDS TERMINATED BY ',' "
             "ENCLOSED BY '' LINES TERMINATED BY '\n' "
             "IGNORE 1 LINES")

# dml to add 'RH', 'TestId' and 'SigRH' data into the 'RHTarget' table
ADD_RH_TARGETS = ("INSERT INTO RHTargets (TestId, RH, SigRH, "
                  "PressureSmooth, DewPointSmooth, TemperatureSmooth,"
                  "SpaldMdpp, SpaldMdppUnc, SpaldTs) VALUES "
                  "(%s, %s, %s, %s, %s, %s, %s, %s, %s)")

# dml to add analysis results into the 'Results' table
ADD_RESULTS = ("INSERT INTO Results"
               "  (TestId, RH, A, SigA, B, SigB, Chi2, Q, Nu)"
               "  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

# dml to add tube data into the 'Tube' table
ADD_TUBE = ("INSERT INTO Tube "
            "(DiameterIn, DiameterOut, Length, Material, Mass)"
            " VALUES "
            "(%(DiameterIn)s, %(DiameterOut)s, %(Length)s,"
            " %(Material)s, %(Mass)s)")

# dml to add unit information into the 'Unit' table
ADD_UNIT = ("INSERT INTO Unit "
            "(Duty, Length, Mass, Power, Pressure, Temperature, Time)"
            " VALUES "
            "(%(Duty)s, %(Length)s, %(Mass)s, %(Power)s, %(Pressure)s,"
            " %(Temperature)s, %(Time)s)")

# dml to update 'RHTargets', adding data to the 'Nu' column
UPDATE_RH_TARGET = "UPDATE RHTargets SET Nu={2} WHERE TestId={0} AND RH={1}"

# ----------------------------------------------------------------------------
# MySQL DML select statement constants
# ----------------------------------------------------------------------------
# dml to select the 'SettingID' from specified setting info
SELECT_SETTING = ("SELECT SettingID FROM Setting WHERE "
                  "  Duty = %(Duty)s AND"
                  "  Pressure = %(Pressure)s AND"
                  "  Temperature = %(Temperature)s AND"
                  "  IsMass = %(IsMass)s AND"
                  "  Reservoir = %(Reservoir)s AND"
                  "  TimeStep = %(TimeStep)s AND"
                  "  TubeId = %(TubeId)s")

# dml to select a 'TestId' basesd on its 'DataTime'
SELECT_TEST = ("SELECT TestID FROM Test WHERE "
               "    DateTime='{}'")

# dml to select a 'TestId' based on a 'SettingId'
TEST_FROM_SETTING = ("SELECT TestId FROM Test WHERE "
                     "    SettingId=({})")

# dml to select a 'TubeId' based on tube info
SELECT_TUBE = ("SELECT TubeID FROM Tube WHERE "
               "  DiameterIn = %(DiameterIn)s AND"
               "  DiameterOut = %(DiameterOut)s AND"
               "  Length = %(Length)s AND"
               "  Material = %(Material)s AND"
               "  Mass = %(Mass)s")
# dml to select data from joined 'Setting' and 'Test' tables
GET_INFO_DF = ("SELECT Temperature, Pressure, Duty, IsMass, Reservoir, "
               "TimeStep, Test.DateTime, Author, Description, TubeId, TestId, "
               "Setting.SettingId FROM Test INNER JOIN Setting ON "
               "Setting.SettingId=Test.SettingId WHERE TestId={};")

# dml to select data from 'Observation' based on a 'TestId'
GET_OBS_DF = ("SELECT Idx, DewPoint, Mass, Pressure, PowOut, PowRef, "
              "OptidewOk, CapManOk FROM Observation WHERE TestId={};")

# dml tp delect data from 'TempObesrvation' based on a 'TestId'
GET_TEMP_DF = ("SELECT Idx,"
               "MAX(CASE WHEN ThermocoupleNum=0 THEN VALUE ELSE 0 END) TC0, "
               "MAX(CASE WHEN ThermocoupleNum=1 THEN VALUE ELSE 0 END) TC1, "
               "MAX(CASE WHEN ThermocoupleNum=2 THEN VALUE ELSE 0 END) TC2, "
               "MAX(CASE WHEN ThermocoupleNum=3 THEN VALUE ELSE 0 END) TC3, "
               "MAX(CASE WHEN ThermocoupleNum=4 THEN VALUE ELSE 0 END) TC4, "
               "MAX(CASE WHEN ThermocoupleNum=5 THEN VALUE ELSE 0 END) TC5, "
               "MAX(CASE WHEN ThermocoupleNum=6 THEN VALUE ELSE 0 END) TC6, "
               "MAX(CASE WHEN ThermocoupleNum=7 THEN VALUE ELSE 0 END) TC7, "
               "MAX(CASE WHEN ThermocoupleNum=8 THEN VALUE ELSE 0 END) TC8, "
               "MAX(CASE WHEN ThermocoupleNum=9 THEN VALUE ELSE 0 END) TC9, "
               "MAX(CASE WHEN ThermocoupleNum=10 THEN VALUE ELSE 0 END) TC10, "
               "MAX(CASE WHEN ThermocoupleNum=11 THEN VALUE ELSE 0 END) TC11, "
               "MAX(CASE WHEN ThermocoupleNum=12 THEN VALUE ELSE 0 END) TC12, "
               "MAX(CASE WHEN ThermocoupleNum=13 THEN VALUE ELSE 0 END) TC13 "
               "FROM("
               "SELECT Idx, ThermocoupleNum, Temperature VALUE FROM "
               "TempObservation WHERE TestId={}) "
               "src GROUP BY Idx;")

# dml to get the 'TestId' from both the high and low RH tests for a 'Setting'
GET_HIGH_LOW_TESTIDS = ('SELECT TestId FROM Test Inner Join Setting ON '
                        'Test.SettingId=Setting.SettingId WHERE '
                        'Setting.Temperature={0} AND Setting.Pressure={1} AND '
                        'TestId IN (SELECT TestId FROM RHTargets)')

# dml to get the analysis results from joined 'RHTarget' and 'Results' tables.
GET_RHTARGET_RESULTS = ('SELECT RHT.RH, SigRH, B, SigB FROM RHTargets AS RHT '
                        'INNER JOIN Results AS Res ON RHT.RH=Res.RH AND '
                        'RHT.TestId=Res.TestId AND RHT.Nu=Res.Nu WHERE '
                        'RHT.TestId={}')

# dml to get data from the 'Resuts' table for a TestId
GET_RES_DF = 'SELECT * FROM Results WHERE TestId={}'


# ----------------------------------------------------------------------------
# Connect and setup functions
# ----------------------------------------------------------------------------
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

    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> assert create_tables(cur, TABLES)
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
            print(err.msg)
        else:
            print(table[0], ' OK')
    return True


# ----------------------------------------------------------------------------
# `Tube` table functions
# ----------------------------------------------------------------------------
def add_tube_info(cur):
    """
    Use a MySQL cursor to add test-independant Tube info.

    Uses cursor .execute function on the ADD_TUBE and TUBE_DATA.
    Adds the new Tube if the Tube doesn't exist. If the Tube already
    exists, then the function does nothing.

    Parameters
    ----------
    cur : mysql.connector.cursor.MySqlCursor
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
    cur.execute(SELECT_TUBE, TUBE_DATA)

    # If the tube does not exist, add it
    # Else, it already exists.
    if not cur.fetchall():
        cur.execute(ADD_TUBE, TUBE_DATA)
        print('Tube added.')
        return True
    else:
        print('Tube already exists.')
        return False


# ----------------------------------------------------------------------------
# `Setting` table finctions
# ----------------------------------------------------------------------------
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
    cur.execute(SELECT_SETTING, setting_info)
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
        cur.execute(ADD_SETTING, setting_info)
        setting_id = cur.lastrowid

    return setting_id


# ----------------------------------------------------------------------------
# `Test` Table
# ----------------------------------------------------------------------------
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
    cur.execute(SELECT_TEST.format(
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
        cur.execute(ADD_TEST, test_info)
        test_id = cur.lastrowid
    return test_id


# ----------------------------------------------------------------------------
# `Observation` Table
def _add_obs_info(cur, tdms_obj, test_id):
    """
    Add relevant data to the 'Observation' table in the MySQL databse.

    Use npTDMS.as_dataframe to create a `DataFrame` object containint the data
    from the argument `nptdms.TdmsFile` object. Format the `Dataframe` for use
    with _load_data and compatibility with the 'Observation' table. Calls
    _load_data to insert data into the database.

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

    Returns
    -------
    True
        Returns `True` after sucess.

    Examples
    --------
    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> test_id = 1
    >>> _add_obs_info(cur, tdms_obj, test_id)
    True

    """
    obs_df = tdms_obj.object('Data').as_dataframe()
    obs_df['TestId'] = [test_id for i in range(len(obs_df))]
    obs_df = obs_df[['CapManOk', 'DewPoint', 'Idx', 'Mass', 'OptidewOk',
                     'PowOut', 'PowRef', 'Pressure', 'TestId']]
    assert _load_data(cur, obs_df, 'Observation')
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
    # Get and format the temperature observation
    temp_info = '{:.2f}'.format(
        tdms_obj.object("Data", "TC{}".format(couple_idx)).data[tdms_idx])
    return temp_info


# ----------------------------------------------------------------------------
# `TempObservation` Table
def _add_temp_info(cur, tdms_obj, test_id):
    """
    Add relevant data to the 'TempObservation' table in the MySQL databse.

    Use npTDMS.as_dataframe to create a `DataFrame` object containint the data
    from the argument `nptdms.TdmsFile` object. Format the `Dataframe` for use
    with _load_data and compatibility with the 'TempObservation' table. Calls
    _load_data to insert data into the database.

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

    Returns
    -------
    True
        Returns `True` after sucess.

    Examples
    --------
    >>> import nptdms
    >>> tdms_file = nptdms.TdmsFile('my-file.tdms')
    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> test_id = 1
    >>> _add_temp_info(cur, tdms_obj, test_id)
    True

    """
    temp_df = pd.DataFrame()
    is_mass = (int(tdms_obj.object('Settings', 'IsMass').data[0]) == 1)
    for n in range(4 if is_mass else 0, 14):
        temp_df[n] = tdms_obj.object('Data', 'TC{}'.format(n)).data
    temp_df['Idx'] = tdms_obj.object('Data', 'Idx').data
    temp_df = pd.melt(temp_df, id_vars=['Idx']).sort_values('Idx')
    temp_df['TestId'] = [test_id for i in range(len(temp_df))]
    temp_df.columns = ['Idx', 'ThermocoupleNum', 'Temperature', 'TestId']
    temp_df.sort_values(['Idx', 'ThermocoupleNum'], inplace=True)
    temp_df = temp_df[['ThermocoupleNum', 'Temperature', 'Idx', 'TestId']]
    assert _load_data(cur, temp_df, 'TempObservation')
    return True


def _load_data(cur, df, table):
    """
    Leverage MySQL 'LOAD DATA INFILE' functionality to rapidly upload data.

    Save the argument `DataFrame` as a .csv file. Use a MySQL
    'LOAD DATA INFILE' style querry to rapidly mass-upload the data into the
    argument table. The .csv file is created and deleted in the root of the
    repository every time _load_data is run.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    df: DataFrame
        A `DataFrame` object compatible with the argument table.
    table: str
        The name of the MySQL database table in which the data will be written.

    Returns
    -------
    True
        Returns `True` after sucess.

    """
    df.to_csv(path_or_buf='_data.csv', index=False)
    assert os.path.isfile('_data.csv')
    cur.execute(LOAD_DATA.format(table))
    os.remove('_data.csv')
    assert not os.path.isfile('_data.csv')
    return True


# ----------------------------------------------------------------------------
# Add all data, main function
# ----------------------------------------------------------------------------
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
        assert _add_obs_info(cur, tdms_obj, test_id)
        assert _add_temp_info(cur, tdms_obj, test_id)

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
    info_df = pd.read_sql(GET_INFO_DF.format(test_id), con=cnx)
    temp_df = pd.read_sql(GET_TEMP_DF .format(test_id), con=cnx)
    obs_df = pd.read_sql(GET_OBS_DF.format(test_id), con=cnx)
    data_df = temp_df.merge(obs_df)

    # Make dictionary
    test_dict = {'info': info_df, 'data': data_df}
    return test_dict


def get_high_low_testids(cur, p, t):
    """Get the Low and High RH TestIds for a specific p and t setting.

    Get the TestIds that correspond to the Low and High Relative Humiditys at a
    specified pressure (Pa) and temperature (K) setting. Only returns TestIds
    that have been analyzed by checking the TestIds present in the RHTargets
    table.

    Parameters
    ----------
    cur : mysql.connector.crsor.MySqlCursor
        Cursor for MySQL database.
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.

    Returns
    -------
    list(int)
        A list of TestIds in RHTargets with the specified t and p settings.

    Examples
    --------
    >>> cnx = connect('my-schema')
    >>> cur = cnx.cursor()
    >>> p = 40000
    >>> t = 280
    >>> get_high_low_testids(cur, p, t)
    [1, 4]

    """
    cur.execute(GET_HIGH_LOW_TESTIDS.format(t, p))
    res = cur.fetchall()
    tid_list = [tid[0] for tid in res]
    return tid_list


def get_rht_results(cnx, test_id):
    """
    Get a `DataFrame` of evaporation rate and RH results for a TestId.

    Use Pandas read_sql functionality and a `MySQLConnection` object to
    pull the RH, SigRh, B, SigB results stored in the RHTargets and Resutls
    tables in the MySql database.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.

    Returns
    -------
    DataFrame
        DataFrame with columns ['RH', 'SigRH', 'B', 'SigB']

    Examples
    --------
    >>> cnx = connect('my-schema')
    >>> test_id = 1
    >>> get_rht_resuts(cnx, test_id)
        RH     SigRH             B          SigB
    0   0.10  0.001920 -6.108320e-09  4.862530e-11
    1   0.15  0.002802 -5.184070e-09  1.725580e-11
    2   0.20  0.003628 -4.707150e-09  3.329170e-12
    3   0.25  0.004452 -4.396130e-09  2.163040e-12

    """
    res_df = pd.read_sql(GET_RHTARGET_RESULTS.format(test_id), con=cnx)
    return res_df


def _add_rh_targets(cur, analyzed_df, test_id):
    """
    Insert Chi2 RH results and uncertainty into MySql database RHTargets table.

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
    rh_trgt_list = [(
        test_id,
        '{:.2f}'.format(rh),
        float(analyzed_df.loc[analyzed_df['RH'] == rh].SigRH.iloc[0]),
        float(analyzed_df.loc[analyzed_df['RH'] == rh].p.iloc[0]),
        float(analyzed_df.loc[analyzed_df['RH'] == rh].t_dp.iloc[0]),
        float(analyzed_df.loc[analyzed_df['RH'] == rh].t_e.iloc[0]),
        float(analyzed_df.loc[analyzed_df['RH'] == rh].spald_mdpp.iloc[0]),
        float(analyzed_df.loc[analyzed_df['RH'] == rh].spald_mdpp_unc.iloc[0]),
        float(analyzed_df.loc[analyzed_df['RH'] == rh].spald_t_s.iloc[0])
    ) for rh in analyzed_df.RH.unique()]
    cur.executemany(ADD_RH_TARGETS, rh_trgt_list)

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
    cur.executemany(ADD_RESULTS, results_list)

    return True


def _get_res_df(cnx, test_id):
    """
    Get a `DataFrame` of the Results table.

    Use Pandas read_sql functionality and a `MySQLConnection` object to execute
    a querry which returns a representation of the 'Results' table in the MySQL
    database.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.

    Returns
    -------
    DataFrame
        `DataFrame` containing the column data stored in the 'Results' table
        in the MySQL database.

    Examples
    --------
    >>> cnx = connect('my-schema')
    >>> test_id = 1
    >>> _get_res_df(cnx, test_id)
    ..todo: Add output.

    """
    res_df = pd.read_sql(GET_RES_DF.format(test_id), con=cnx)
    return res_df


def _add_best_fit(cnx, test_id):
    """
    Add the .Nu' value of the best Chi2 fit to the 'RHTargets' Table.

    Update the RHTargets table by using a 'MySQLConnection.cursor' object
    to insert the degrees of freeom, 'Nu' corresponding to the most appropreate
    Chi2 linear fit for each Relative Humidity, 'RH'.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.
    test_id : int
        TestID for the MySQL database, which is the primary key for the Test
        table.

    Returns
    -------
    True or None
        `True` if sucessful, `None` if not.

    Examples
    --------
    Add best fit data for Testid 4.

    >>> cnx = connect('my-schema')
    >>> test_id = 4
    True

    """
    cur = cnx.cursor()
    res_df = _get_res_df(cnx, test_id)
    for rh in res_df.RH.unique():
        rh_set_df = res_df[res_df['RH'] == rh].reset_index()
        rh_row = experiments._get_df_row(rh_set_df)
        if rh_row is not None:
            cur.execute(UPDATE_RH_TARGET.format(
                rh_row.TestId.iloc[0], rh_row.RH.iloc[0], rh_row.Nu.iloc[0]))
    return True


def add_analysis(cnx, test_id, steps=1):
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
    steps : int
        The step size for Chi2 analysis. Defaults to 1.

    Returns
    -------
    `True` or `None`
        `True` if sucessful, else `None`.

    Examples
    --------
    Add analysis results for an existing TestId.

    >>> cnx = connect('my-schema')
    >>> test_id = 1
    >>> add_analysis(cnx, test_id, steps=2, nu_min=150)
    True

    """
    # --------------------------------------------------------------------
    # Create a DataFrame of analyzed data
    test_dict = _get_test_dict(cnx, test_id)
    processed_df = experiments.preprocess(test_dict['data'])
    analyzed_df = experiments.mass_transfer(processed_df, steps=steps)
    try:
        # --------------------------------------------------------------------
        # Create a cursor and start the transaction
        cur = cnx.cursor()
        assert cnx.in_transaction

        # --------------------------------------------------------------------
        # RHTargets: call add_rh_targets
        assert _add_rh_targets(cur, analyzed_df, test_id)
        assert cnx.in_transaction

        # --------------------------------------------------------------------
        # Results: call add_results
        assert _add_results(cur, analyzed_df, test_id)
        assert cnx.in_transaction

        assert _add_best_fit(cnx, test_id)

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
