"""Module containing pytest fixtures."""

import unittest.mock as mock

import pytest


@pytest.fixture()
def mock_ConfigParser(monkeypatch):
    """Mock of the configparser.ConfigParser class."""
    configparser = mock.MagicMock()
    configparser.read = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.manager.crud.configparser.ConfigParser.read',
        configparser.read
        )

    # Production code calls Python builtin dict() on
    # configparser['MySQL-Server'].
    configparser['MySQL-Server'] = mock.MagicMock()
    configparser_key_setter(configparser, ['host', 'user', 'password'])
    configparser['MySQL-Server'].__getitem__.side_effect = [
        'address', 'me', 'secret'
        ]

    mock_ConfigParser = mock.MagicMock(return_value=configparser)
    mock_ConfigParser.configparser = configparser
    monkeypatch.setattr(
        'chamber.manager.crud.configparser.ConfigParser',
        mock_ConfigParser
        )
    return mock_ConfigParser


@pytest.fixture()
def mock_mysql(monkeypatch):
    """Mock of mysql.connector module."""
    mock_mysql = mock.MagicMock()

    # Define instances before method definition and return value assignment.
    cnx_instance = mock_mysql.cnx
    cur_instance = mock_mysql.cur

    # Define methods and assign return values.
    connect_method = mock_mysql.connect
    connect_method.return_value = cnx_instance

    cursor_method = cnx_instance.cursor
    cursor_method.return_value = cur_instance

    execute_method = cur_instance.execute

    # Patch calls now that mock_mysql is setup.
    monkeypatch.setattr(
        'chamber.manager.crud.mysql.connector.connect', connect_method
        )
    monkeypatch.setattr(
        (
            'chamber.manager.crud.mysql.connector.connection.MySQLConnection'
            '.cursor'
            ),
        cursor_method
        )
    monkeypatch.setattr(
        'chamber.manager.crud.mysql.connector.cursor.MySQLCursor.execute',
        execute_method
        )

    return mock_mysql


@pytest.fixture()
def mock_utility(monkeypatch):
    """Mock chamber.utility."""
    table_order = ('one', 'two', 'three')
    ddl = {
        'one': 'foo',
        'two': 'bar',
        'three': 'bacon!'
        }

    build_instructions = {
        ('group', 'table_order'): table_order,
        ('group', 'ddl'): ddl
        }

    monkeypatch.setattr(
        'chamber.utility.ddl.build_instructions',
        build_instructions
        )


@pytest.fixture()
def mock_sqlalchemy(monkeypatch):
    """Mock of sqlalchemy package."""
    mock_sqlalchemy = mock.MagicMock()
    create_engine = mock_sqlalchemy.create_engine
    create_engine.return_value = (
        'Engine(mysql+mysqlconnector://me:***@address:3306/test_schema)'
        )
    monkeypatch.setattr(
        'chamber.manager.crud.sqlalchemy.create_engine',
        create_engine
        )

    return mock_sqlalchemy


@pytest.fixture()
def mock_pd(monkeypatch):
    """Mock of pandas package."""
    mock_pd = mock.MagicMock()

    DataFrame = mock_pd.DataFrame
    to_sql = DataFrame.to_sql

    monkeypatch.setattr(
        'chamber.manager.crud.pd.core.frame.DataFrame.to_sql', to_sql
        )

    return mock_pd


@pytest.fixture()
def mock_tk(monkeypatch):
    """Mock of tkinter module."""
    mock_tk = mock.MagicMock()

    root = mock_tk.root
    withdraw = root.withdraw
    withdraw.return_value = ''

    Tk = mock_tk.Tk
    monkeypatch.setattr('chamber.manager.crud.tk.Tk', Tk)
    Tk.return_value = root

    filedialog = mock_tk.filedialog
    askopenfilename = filedialog.askopenfilename
    monkeypatch.setattr(
        'chamber.manager.crud.filedialog.askopenfilename',
        askopenfilename
        )
    askopenfilename.return_value = 'C:/Users/Me/test_experiment.tdms'

    return mock_tk


@pytest.fixture()
def mock_nptdms(monkeypatch):
    """Mock of nptdms module."""
    mock_nptdms = mock.MagicMock()
    tdms_file = mock_nptdms.tdms_file

    TdmsFile = mock_nptdms.TdmsFile
    monkeypatch.setattr('chamber.manager.crud.nptdms.TdmsFile', TdmsFile)
    TdmsFile.return_value = tdms_file

    return mock_nptdms

# ----------------------------------------------------------------------------
# helpers


def configparser_key_setter(configparser, keys):
    """Change keys that configparser returns."""
    configparser['MySQL-Server'].keys.return_value.__iter__.return_value = (
        keys
        )
