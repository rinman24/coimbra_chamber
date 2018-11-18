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
    root = tk.Tk()
    root.withdraw()
    fp = filedialog.askopenfilename(title='Select Experiment')

    # tdms_file = nptdms.TdmsFile(fp)
    # You need some helper functions here. namely get settings df
    # However, this may belong in an engine. The question is, should
    # CRUD manager be responsible for knowing how to get the data out
    # of nptdms files? Probably not. So who should know how to do this?
    # Well an engine. but What engine?


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
