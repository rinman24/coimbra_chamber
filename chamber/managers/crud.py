"""CRUD Manager module."""

import configparser


def get_credentials():
    """Use configparser to obtain credentials."""
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
