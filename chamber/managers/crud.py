
"""
CRUD Manager module.

Functions
---------

- `get_credentials` -- use configparser to obtain credentials.

"""

import configparser

import mysql.connector

import chamber.access.experiment as exp_acc


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
    >>> creds = get_credentials()
    >>> type(creds)
    <class 'dict'>

    """
    config_parser = configparser.ConfigParser()

    # congif_parser.read() returns a list containing the files read;
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
