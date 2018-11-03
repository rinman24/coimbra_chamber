"""CRUD Manager module."""

import configparser


def get_credentials(database):
    """Use configparser to obtain credentials."""
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
    config = dict(config_parser['MySQL-Server'])

    required_key_set = {'host', 'user', 'password'}
    config_key_set = set(config.keys())

    if required_key_set.issubset(config_key_set):
        config['database'] = database
        return config
    else:
        raise KeyError('config file is missing a key.')
