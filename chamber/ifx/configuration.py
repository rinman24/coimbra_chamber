"""Encapsulates configuration of settings."""

import os
from configparser import ConfigParser
from pathlib import Path


def get_value(key, section):
    """
    Get a configuration setting from a section.

    The setting can be stored in an environment variable or a local config.ini
    file.

    Parameters
    ----------
    key : str
        Desired key.
    section : str, default 'DEFAULT'
        Section for the config.ini file.

    Returns
    -------
    str
        Value of the requested key.

    Examples
    --------
    >>> import chamber.ifx.configuration as config
    >>> config.get_value('user', 'MySQL-Server')
    'root'

    """
    # check environment variable
    value = os.environ.get(key)

    if value:
        return value

    # check local config.ini
    parser = ConfigParser(delimiters='|')
    path = Path('chamber/config.ini')
    parser.read(path)

    if parser.has_option(section, key):
        return parser.get(section, key)
