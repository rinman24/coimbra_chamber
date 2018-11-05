"""CRUD manager unit test suite."""

import unittest.mock as mock

import pytest

import chamber.manager.crud as crud_mngr

_CORRECT_CREDS = dict(host='address', user='me', password='secret')


@pytest.fixture
def ConfigParser(monkeypatch):
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
    _configparser_key_setter(configparser, ['host', 'user', 'password'])
    configparser['MySQL-Server'].__getitem__.side_effect = [
        'address', 'me', 'secret'
        ]

    ConfigParser = mock.MagicMock(return_value=configparser)
    ConfigParser.configparser = configparser
    monkeypatch.setattr(
        'chamber.manager.crud.configparser.ConfigParser',
        ConfigParser
        )
    return ConfigParser


@pytest.fixture
def connect(monkeypatch):
    """Mock connect method of mysql.connector.connect."""
    cnx = mock.MagicMock()
    cnx.cursor = mock.MagicMock(
        return_value='<mysql.connector.cursor.MySQLCursor object at ...>'
        )
    monkeypatch.setattr(
        'mysql.connector.connection.MySQLConnection.cursor',
        cnx.cursor
        )

    connect = mock.MagicMock(return_value=cnx)
    monkeypatch.setattr(
        'chamber.manager.crud.mysql.connector.connect',
        connect
        )

    connect.cnx.cursor = cnx.cursor  # connect is the manager mock

    return connect


# ----------------------------------------------------------------------------
# _get_credentials


def test_can_call_get_credentials(ConfigParser):  # noqa: D103
    crud_mngr._get_credentials()

    ConfigParser.configparser.read.assert_called_once_with('config.ini')


def test_get_credentials_returns_correct_dict(ConfigParser):  # noqa: D103
    creds = crud_mngr._get_credentials()

    assert creds == _CORRECT_CREDS


def test_get_credentials_exception_knows_the_name_missing_key(ConfigParser):  # noqa: D103
    _configparser_key_setter(ConfigParser.configparser, ['user', 'password'])

    err_message = (
        'KeyError: config file is missing the following key: host.'
        )

    with pytest.raises(KeyError, match=err_message):
        crud_mngr._get_credentials()


def test_get_credentials_raises_file_not_found_error(ConfigParser):  # noqa: D103
    ConfigParser.configparser.read.return_value = []

    error_message = ('FileNotFoundError: config.ini does not exits.')
    with pytest.raises(FileNotFoundError, match=error_message):
        crud_mngr._get_credentials()


# ----------------------------------------------------------------------------
# _get_cursor


def test_get_cursor_calls_connect(connect):  # noqa: D103
    crud_mngr._get_cursor('schema', _CORRECT_CREDS)

    creds_w_pass = dict(_CORRECT_CREDS)
    creds_w_pass['database'] = 'schema'
    connect.assert_called_once_with(**creds_w_pass)


def test_get_cursor_calls_cursor(connect):  # noqa: D103
    crud_mngr._get_cursor('schema', _CORRECT_CREDS)

    connect.cnx.cursor.assert_called_once_with()


def test_get_cursor_returns_cursor(connect):  # noqa: D103
    cur = crud_mngr._get_cursor('schema', _CORRECT_CREDS)
    assert cur == '<mysql.connector.cursor.MySQLCursor object at ...>'


# ----------------------------------------------------------------------------
# _build_tables

@pytest.mark.skip
def test_can_call_build_tables():
    crud_mngr._build_tables('schema')

@pytest.mark.skip
def test_build_tables_executes_calls_in_correct_order(monkeypatch):
    table_order = ('one', 'two', 'three')
    ddl = {
        'one': 'foo',
        'two': 'bar',
        'three': 'bacon!'
        }
    build_instructions = {
        ('schema', 'table_order'): table_order,
        ('schema', 'ddl'): ddl
        }

    utility = mock.MagicMock()
    utility.ddl.build_instructions = build_instructions
    monkeypatch.setattr(
        'chamber.utility.ddl.build_instructions',
        utility.ddl.build_instructions
        )

    crud_mngr._build_tables('schema')

    pass


# ----------------------------------------------------------------------------
# setup_experiment_tables


def test_setup_experiment_tables_returns_success(ConfigParser, connect, monkeypatch):  # noqa: D103
    build_tables = mock.MagicMock(return_value='Success.')
    monkeypatch.setattr('chamber.access.experiment.build_tables', build_tables)

    message = crud_mngr.setup_experiment_tables('schema')
    assert message == 'Success.'


# ----------------------------------------------------------------------------
# helpers


def _configparser_key_setter(configparser, keys):
    configparser['MySQL-Server'].keys.return_value.__iter__.return_value = (
        keys
        )
