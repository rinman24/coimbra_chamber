"""
CRUD manager module.

Functions
---------

- `create_tables` -- Manage construction of tables for a given database.
- `drop_tables` -- Manage destuction of tables for a given database.
- `add_tube` -- Manage addition of tube into a given database.

"""

import configparser
import pathlib

import mysql.connector
import nptdms
import pandas as pd
import sqlalchemy
import tkinter as tk
from tkinter import filedialog

import chamber.utility.ddl as util_ddl
import chamber.engine.analysis as anlys_eng


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


def _get_engine(database, creds):
    """Use database and creds to create an sqlalchemy engine."""
    creds['database'] = database
    engine_url = (
        'mysql+mysqlconnector://{user}:{password}@{host}:3306/{database}'
        .format(**creds)
        )

    engine = sqlalchemy.create_engine(engine_url)

    return engine


def _get_experimental_data():
    """Ask user for filename and get databases dict."""
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title='Select Experiment')

    databases = anlys_eng.read_tdms(filepath)

    return databases


def _get_last_row_id(table, column, engine):
    """Get the last row id for foreign key constraints."""
    dml = 'SELECT IFNULL(MAX({0}), 0) FROM {1};'.format(column, table)
    return pd.read_sql_query(dml, con=engine).iloc[0, 0]


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
        last_row_id = _get_last_row_id(table, id_to_get, engine)
        return last_row_id


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
    Add experiment from a tdms file to specifies database.

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
    >>> add_experiment('schema')
    Inserting `Setting`...
    Inserting `Test`...
    Inserting `Observation`...
    Inserting `TempObservation`...
    'Successfully added experiment to `schema`.'

    """
    print('Loading TDMS file...')
    dataframes = _get_experimental_data()

    creds = _get_credentials()
    engine = _get_engine(database, creds)

    print('Inserting `Setting`...')
    setting_id = _update_table(
        'Setting',
        dataframes['setting'],
        engine,
        id_to_get='SettingId'
        )

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
