"""CRUD Manager module."""

import configparser


def get_credentials(database):
    """Use configparser to obtain credentials."""
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
    config = dict(config_parser['MySQL-Server'])
    config['database'] = database
    return config
