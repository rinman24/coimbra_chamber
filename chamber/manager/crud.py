"""CRUD manager module."""

import configparser
import datetime
import pathlib

import matplotlib.pyplot as plt
import mysql.connector
import nptdms
import pandas as pd
import sqlalchemy
import tkinter as tk
from tkinter import filedialog

import chamber.utility.ddl as util_ddl
import chamber.engine.analysis.service as anlys_eng


DEFAULT_TUBE = pd.DataFrame(
        data=dict(
            DiameterIn=0.03,
            DiameterOut=0.04,
            Length=0.06,
            Material='Delrin',
            Mass=0.0873832
            ),
        index=[0]
        )

# ----------------------------------------------------------------------------
# Internal logic


# Connecting


def _get_credentials():
    """Use configparser to obtain credentials."""
    config_parser = configparser.ConfigParser()

    # config_parser.read() returns a list containing the files read;
    # e.g. ['config.ini'].
    config_result = config_parser.read('config.ini')

    if config_result:  # The config file was read in.
        credentials = dict(config_parser['MySQL-Server'])
        required_key_set = {'host', 'user', 'password'}
        config_key_set = set(credentials.keys())

        if required_key_set.issubset(config_key_set):
            return credentials
        else:
            missing_key_set = required_key_set.difference(config_key_set)
            error_message = (
                'KeyError: config file is missing the following key: {}.'
                .format(missing_key_set.pop())
                )
            raise KeyError(error_message)
    error_message = 'FileNotFoundError: config.ini does not exits.'
    raise FileNotFoundError(error_message)


def _connect(creds, database=None):
    """Use credentials to connect to mySQL database."""
    cnx = mysql.connector.connect(**creds)
    cur = cnx.cursor()
    if database:
        cur.execute(
            'USE {};'.format(database)
            )
    return cnx, cur


def _get_engine(database, creds):
    """Use database and creds to create an sqlalchemy engine."""
    creds['database'] = database
    engine_url = (
        'mysql+mysqlconnector://{user}:{password}@{host}:3306/{database}'
        .format(**creds)
        )

    engine = sqlalchemy.create_engine(engine_url)

    return engine


# Setup/teardown


def _execute_build(cursor, table_group):
    """Use cursor and database name to build tables."""
    table_order = util_ddl.build_instructions[table_group, 'table_order']
    ddl = util_ddl.build_instructions[table_group, 'ddl']

    for table in table_order:
        print('Creating table {}: '.format(table), end='')
        cursor.execute(ddl[table])
        print('OK')
    return 'Successfully built `{}` tables.'.format(table_group)


def _execute_drop(cursor, table_group):
    """Use cursor and database name to drop tables."""
    table_order = util_ddl.build_instructions[table_group, 'table_order']
    reversed_table_order = table_order[::-1]

    for table in reversed_table_order:
        print('Dropping table {}: '.format(table), end='')
        cursor.execute('DROP TABLE {};'.format(table))
        print('OK')
    return 'Successfully dropped `{}` tables.'.format(table_group)


# Read tdms


def _get_experimental_data():
    """Ask user for filename and get databases dict."""
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title='Select Experiment')

    print('Loading TDMS file...')
    databases = anlys_eng.read_tdms(filepath)

    d = databases['test'].loc[0, 'DateTime']
    databases['test'].loc[0, 'DateTime'] = datetime.datetime(
        d.year, d.month, d.day, d.hour, d.minute, d.second
        )

    return databases


def _update_table(table, dataframe, engine, col_to_add=None, id_to_get=None):
    """
    Upload a `dataframe` into sql `table` using provided `engine`.

    Parameters
    ----------
    table : str
        Name of the sql table to insert `dataframe`.
    dataframe : pandas.DataFrame
        Format must mirror the sql tables
    engine : sqlalchemy.engine.base.Engine
        Typically build using `_get_engine` funciton.
    col_to_add : tuple of (str, int), optional
        str: name of column
        int: value to add
    id_to_get : str, optional
        Name of the column to get after the update.

    Returns
    -------
    int
        Last row id if `id_to_get` is truthy.

    Examples
    --------
    Get credentials and engine before starting:

    >>> creds = _get_credentials()
    >>> engine = _get_engine('test_schema', creds)

    If you want to update the dataframe as is:

    >>> _update_table('table', dataframe, engine)

    You can also add a column called `table_id` with a value of 1
    to the dataframe before inserting:

    >>> col_to_add = ('table_id', 1)
    >>> _update_table('table', dataframe, engine, col_to_add=col_to_add)


    You can also retreive the last row id as well:

    >>> id_to_get = 'table_id'
    >>> id = _update_table('table', dataframe, engine, id_to_get=id_to_get)

    """
    if col_to_add:
        column, value = col_to_add
        dataframe.loc[:, column] = value

    dataframe.to_sql(
        name=table,
        con=engine,
        if_exists='append',
        index=False
        )

    if id_to_get:
        last_row_id = _query_last_row_id(table, id_to_get, engine)
        return last_row_id


# Queries

def _query_last_row_id(table, column, engine):
    """Get the last row id for foreign key constraints."""
    dml = 'SELECT IFNULL(MAX({0}), 0) FROM {1};'.format(column, table)
    return pd.read_sql_query(dml, con=engine).iloc[0, 0]


def _query_setting_exists(dataframes, engine):
    """Return setting id if exists, else False."""
    df = dataframes['setting']

    setting_dict = dict(
        duty=df.loc[0, 'Duty'],
        pressure=df.loc[0, 'Pressure'],
        temp=df.loc[0, 'Temperature'],
        is_mass=df.loc[0, 'IsMass'],
        reservoir=df.loc[0, 'Reservoir'],
        time_step=df.loc[0, 'TimeStep'],
        tube_id=df.loc[0, 'TubeID']
        )

    sql = (
        "SELECT SettingID FROM Setting WHERE "
        "  Duty = {duty} AND"
        "  Pressure = {pressure} AND"
        "  Temperature = {temp} AND"
        "  IsMass = {is_mass} AND"
        "  Reservoir = {reservoir} AND"
        "  TimeStep = {time_step} AND"
        "  TubeId = {tube_id};".format(**setting_dict)
        )
    print('Checking if setting exists...')
    result = pd.read_sql_query(sql, con=engine)

    if not result.empty:
        setting_id = result.iloc[0, 0]
        print('    SettingId: {}'.format(setting_id))
        return setting_id
    else:
        print('    Setting does not exist.')
        return False


def _query_test_exists(dataframes, engine):
    """Return test id if exists, else False."""
    df = dataframes['test']

    test_dict = dict(
        author=df.loc[0, 'Author'],
        datetime=str(df.loc[0, 'DateTime']),
        )

    sql = (
        "SELECT TestId FROM Test WHERE "
        "  Author = '{author}' AND"
        "  DateTime = '{datetime}';".format(**test_dict)
        )
    print('Checking if test exists...')
    result = pd.read_sql_query(sql, con=engine)

    if not result.empty:
        test_id = result.iloc[0, 0]
        print('    TestId: {}'.format(test_id))
        return test_id
    else:
        print('    Test does not exist.')
        return False


def _query_temp_obs_and_pivot(test_id, engine):  # pragma: no cover
    dml = "SELECT * FROM TempObservation WHERE TestId={};".format(test_id)
    temp_data = pd.read_sql_query(dml, con=engine)
    temp_data = temp_data.pivot(
        index='Idx', columns='ThermocoupleNum', values='Temperature'
        )
    return temp_data


def _query_obs(test_id, engine):  # pragma: no cover
    dml = (
        "SELECT Idx, DewPoint, Mass, Pressure"
        "  FROM Observation"
        "  WHERE TestId={}".format(test_id)
        )

    obs_data = pd.read_sql_query(dml, con=engine)
    obs_data.index = obs_data.Idx
    obs_data.drop(columns=['Idx'], inplace=True)

    return obs_data


# ----------------------------------------------------------------------------
# Public functions


def create_tables(table_group, database):
    """
    Manage construction of a group of tables for a given database.

    In general, creation of tables occurs most often during creation of the
    schema. As a result, this function attempts to create the database if it
    doesn't already exist.

    Parameters
    ----------
    table_group : str
        Name of the group of tables to build. Typically accessed from
        `chamber.utility`.
    database : str
        Name of the database (or schema).

    Returns
    -------
    str
        Message confirming tables in group were built for the database.

    Examples
    --------
    >>> create_tables('group', 'schema')
    Creating table Tube: OK
    Creating table Setting: OK
    Creating table Test: OK
    Creating table Observation: OK
    Creating table TempObservation: OK
    'Successfully built `group` tables in `schema`.'

    """
    creds = _get_credentials()
    try:
        _, cur = _connect(creds)
    except mysql.connector.Error as err:
        print(err)
        return 'mySQL Error: ' + str(err)
    else:
        cur.execute(
            'CREATE DATABASE IF NOT EXISTS {} '
            'DEFAULT CHARACTER SET latin1 ;'
            .format(database)
            )
        cur.execute('USE {};'.format(database))
        message = _execute_build(cur, table_group)
        return message[:-1] + ' in `{}`.'.format(database)


def drop_tables(table_group, database, drop_db=False):
    """
    Manage destruction of tables for a given database.

    Parameters
    ----------
    table_group : str
        Name of the group of tables to build. Typically accessed from
        `chamber.utility`.
    database : str
        Name of the database (or schema)
    drop_db : bool, defalut False
        Deault beavior is to leave the schema in place after all tables are
        dropped. If `drop_db` is set to True, the schema is dropped with the
        tables.

    Returns
    -------
    str
        Message confirming that tables were dropped for the database. Will
        also confirm that database was dropped if `drop_db` is True.

    Examples
    --------
    Default behavior is to leave the schema in place.

    >>> drop_tables('group', 'schema')
    Dropping table TempObservation: OK
    Dropping table Observation: OK
    Dropping table Test: OK
    Dropping table Setting: OK
    Dropping table Tube: OK
    'Successfully dropped `group` tables.'

    However, you can also drop the schema with the tables.

    >>> drop_tables('group', 'schema', drop_db=True)
    Dropping table TempObservation: OK
    Dropping table Observation: OK
    Dropping table Test: OK
    Dropping table Setting: OK
    Dropping table Tube: OK
    'Successfully dropped `group` tables from `schema`. Database `schema` also dropped.'

    """
    creds = _get_credentials()
    _, cur = _connect(creds, database=database)
    message = _execute_drop(cur, table_group)
    message = message[:-1] + ' from `{}`.'.format(database)
    if drop_db:
        cur.execute(
            'DROP DATABASE {};'.format(database)
            )
        message += ' Database `{}` also dropped.'.format(database)
    return message


def add_tube(database):
    """
    Manage addition of tube into a given database.

    Parameters
    ----------
    database : str
        Name of the database (or schema)

    Returns
    -------
    str
        Message confirming tube was added.

    Examples
    --------
    >>> add_tube('schema')
    'Sucessfully added default tube to `schema`.'

    """
    creds = _get_credentials()
    engine = _get_engine(database, creds)
    DEFAULT_TUBE.to_sql(
        name='Tube',
        con=engine,
        if_exists='append',
        index=False
        )

    message = 'Sucessfully added default tube to `{}`.'.format(database)
    return message


def add_experiment(database):
    """
    Manage addition of experiment from a tdms file to a specified database.

    Function propmts user to select a tdms file then insertes the file into
    the specifiec sql database.

    Parameters
    ----------
    database : str
        Name of the database (or schema)

    Returns
    -------
    str
        Message confirming experiment was added.

    Examples
    --------
    Enter y when asked to proceed.

    >>> add_experiment('schema')
    Loading TDMS file...
    Proceed ([y]/n)? y
    Inserting `Setting`...
    Inserting `Test`...
    Inserting `Observation`...
    Inserting `TempObservation`...
    'Successfully added experiment to `schema`.'

    """
    dataframes = _get_experimental_data()

    _, axes = plt.subplots(nrows=4, ncols=1, figsize=(10, 8))
    dataframes['observation'].plot(x='Idx', y='Mass', ax=axes[0])
    dataframes['observation'].plot(x='Idx', y='Pressure', ax=axes[1])
    dataframes['observation'].plot(x='Idx', y='DewPoint', ax=axes[2])
    dataframes['temp_observation'].plot.scatter(
        x='Idx', y='Temperature', s=1, ax=axes[3]
        )
    plt.show()

    response = input('Proceed ([y]/n)? ').lower()

    if (not response) or ('y' in response):
        creds = _get_credentials()
        engine = _get_engine(database, creds)

        setting_id = _query_setting_exists(dataframes, engine)
        if not setting_id:
            print('Inserting `Setting`...')
            setting_id = _update_table(
                'Setting',
                dataframes['setting'],
                engine,
                id_to_get='SettingId'
                )

        test_id = _query_test_exists(dataframes, engine)
        if not test_id:
            print('Inserting `Test`...')
            test_id = _update_table(
                'Test',
                dataframes['test'],
                engine,
                col_to_add=('SettingId', setting_id),
                id_to_get='TestId'
                )

            print('Inserting `Observation`...')
            _update_table(
                'Observation',
                dataframes['observation'],
                engine,
                col_to_add=('TestId', test_id)
                )

            print('Inserting `TempObservation`...')
            _update_table(
                'TempObservation',
                dataframes['temp_observation'],
                engine,
                col_to_add=('TestId', test_id)
                )

            return 'Successfully added experiment to `{}`.'.format(database)
        else:
            return 'Halting execution.'

    elif 'n' in response:
        return 'Experiment not loaded.'
    else:
        return 'Unrecognized response.'
