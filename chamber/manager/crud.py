"""
CRUD Manager module.

Functions
---------

- `build_tables` -- Orchestrate construction of tables for a given database.
- `drop_tables` -- Orchestrate destuction of tables for a given database.

"""

import configparser

import mysql.connector

import chamber.utility.ddl as util_ddl


def _get_credentials():
    """
    Use configparser to obtain credentials.

    Returns
    -------
    dict
        Crednetials included in the config.ini file. Keys include: `host`,
        `user`, and `password`.

    Raises
    ------
    FileNotFoundError: If the config.ini file is not found.
    KeyError: If any keys are missing from the `MySQL-Server` section of the
        config.ini file.

    Examples
    --------
    >>> creds = _get_credentials()
    >>> type(creds)
    <class 'dict'>

    """
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


def _get_cursor(database, creds):
    """
    Get a cursor using mysql.connector.

    Parameters
    ----------
    database: str
        Name of the database for which to create a cursor.
    creds: dict
        dictionay of credentials. Typically returned from a call to the
        `_get_credentials` function.

    Returns
    -------
    mysql.connector.cursor.MySQLCursor
        cursor object for the specified database.

    Examples
    --------
    >>> creds = _get_credentials()
    >>> cur = _get_cursor('schema', creds)

    """
    creds['database'] = database
    cnx = mysql.connector.connect(**creds)
    cur = cnx.cursor()
    return cur


def _authenticate(database):
    """Use database to obtain a mySQL cursor."""
    creds = _get_credentials()
    cur = _get_cursor(database, creds)
    return cur


def _execute_build(database, cursor):
    """
    Use cursor and database name to build tables.

    Parameters
    ----------
    database: str
        Name of the database, which is used to lookup required ddl from
        utility.
    cursor : mysql.connector.cursor.MySQLCursor
        mySQL cursor object

    Returns
    -------
    str
        'Success.' if successful.

    Examples
    --------
    >>> _execute_build('schema', cursor)
    'Success.'

    """
    table_order = util_ddl.build_instructions[database, 'table_order']
    ddl = util_ddl.build_instructions[database, 'ddl']

    for table in table_order:
        print('Creating table {}: '.format(table), end='')
        cursor.execute(ddl[table])
        print('OK')
    return 'Sucessfully built {} tables.'.format(database)


def _execute_drop(database, cursor):
    """
    Use cursor and database name to drop tables.

    Parameters
    ----------
    database: str
        Name of the database, which is used to lookup required table order
        from utility.
    cursor : mysql.connector.cursor.MySQLCursor
        mySQL cursor object

    Returns
    -------
    str
        'Success.' if successful.

    Examples
    --------
    >>> _execute_drop('schema', cursor)
    'Success.'

    """
    table_order = util_ddl.build_instructions[database, 'table_order']
    reversed_table_order = table_order[::-1]

    for table in reversed_table_order:
        print('Dropping table {}: '.format(table), end='')
        cursor.execute('DROP TABLE {};'.format(table))
        print('OK')
    return 'Sucessfully dropped {} tables.'.format(database)


def build_tables(database):
    """
    Orchestrate construction of tables for a given database.

    Parameters
    ----------
    database : str
        Name of the database (or schema)

    Returns
    -------
    str
        "Success." if successful.

    Examples
    --------
    >>> message = build_tables('schema')
    >>> message
    'Successfully built schema tables.'

    """
    cur = _authenticate(database)
    message = _execute_build(database, cur)
    return message


def drop_tables(database):
    """
    Orchestrate destruction of tables for a given database.

    Parameters
    ----------
    database : str
        Name of the database (or schema)

    Returns
    -------
    str
        "Success." if successful.

    Examples
    --------
    >>> message = drop_tables('schema')
    >>> message
    'Successfully dropped schema tables.'

    """
    cur = _authenticate(database)
    message = _execute_drop(database, cur)
    return message
