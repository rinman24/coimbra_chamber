"""CRUD manager unit test suite."""

import unittest.mock as mock

import pytest

import chamber.manager.crud as crud_mngr

_CORRECT_CREDS = dict(host='address', user='me', password='secret')


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
    _configparser_key_setter(configparser, ['host', 'user', 'password'])
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
def mock_connect(monkeypatch):
    """Mock connect method of mysql.connector.connect."""
    cur = mock.MagicMock()
    cur.execute = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.manager.crud.mysql.connector.cursor.MySQLCursor.execute',
        cur.execute
    )

    cnx = mock.MagicMock()
    cnx.cursor = mock.MagicMock(
        return_value=cur
        )
    monkeypatch.setattr(
        (
            'chamber.manager.crud.mysql.connector.connection.MySQLConnection'
            '.cursor'
            ),
        cnx.cursor
        )

    mock_connect = mock.MagicMock(return_value=cnx)
    monkeypatch.setattr(
        'chamber.manager.crud.mysql.connector.connect',
        mock_connect
        )

    # mock_connect is the manager mock
    mock_connect.cnx.cursor = cnx.cursor
    mock_connect.cur = cur

    return mock_connect


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
        ('schema', 'table_order'): table_order,
        ('schema', 'ddl'): ddl
        }

    monkeypatch.setattr(
        'chamber.utility.ddl.build_instructions',
        build_instructions
        )

# ----------------------------------------------------------------------------
# _get_credentials


def test_can_call_get_credentials(mock_ConfigParser):  # noqa: D103
    crud_mngr._get_credentials()

    mock_ConfigParser.configparser.read.assert_called_once_with('config.ini')


def test_get_credentials_returns_correct_dict(mock_ConfigParser):  # noqa: D103
    creds = crud_mngr._get_credentials()

    assert creds == _CORRECT_CREDS


def test_get_credentials_exception_knows_the_name_missing_key(mock_ConfigParser):  # noqa: D103
    _configparser_key_setter(
        mock_ConfigParser.configparser, ['user', 'password']
        )

    err_message = (
        'KeyError: config file is missing the following key: host.'
        )

    with pytest.raises(KeyError, match=err_message):
        crud_mngr._get_credentials()


def test_get_credentials_raises_file_not_found_error(mock_ConfigParser):  # noqa: D103
    mock_ConfigParser.configparser.read.return_value = []

    error_message = ('FileNotFoundError: config.ini does not exits.')
    with pytest.raises(FileNotFoundError, match=error_message):
        crud_mngr._get_credentials()


# ----------------------------------------------------------------------------
# _get_cursor


def test_get_cursor_calls_connect(mock_connect):  # noqa: D103
    crud_mngr._get_cursor('schema', _CORRECT_CREDS)

    creds_w_pass = dict(_CORRECT_CREDS)
    creds_w_pass['database'] = 'schema'
    mock_connect.assert_called_once_with(**creds_w_pass)


def test_get_cursor_calls_cursor(mock_connect):  # noqa: D103
    crud_mngr._get_cursor('schema', _CORRECT_CREDS)

    mock_connect.cnx.cursor.assert_called_once_with()


def test_get_cursor_returns_cursor(mock_connect):  # noqa: D103
    cur = crud_mngr._get_cursor('schema', _CORRECT_CREDS)
    assert cur == mock_connect.cur


# ----------------------------------------------------------------------------
# _build_tables


def test_build_tables_executes_calls_in_correct_order(mock_connect, mock_utility):  # noqa: D103
    crud_mngr._build_tables('schema', mock_connect.cnx.cursor)

    correct_calls = [mock.call('foo'), mock.call('bar'), mock.call('bacon!')]
    mock_connect.cnx.cursor.execute.assert_has_calls(correct_calls)


def test_build_tables_returns_success(mock_connect, mock_utility):  # noqa: D103
    message = crud_mngr._build_tables('schema', mock_connect.cnx.cursor)
    assert message == 'Success.'


# ----------------------------------------------------------------------------
# _drop_tables


def test_drop_tables_executes_calls_in_correct_order(mock_connect, mock_utility):  # noqa D103
    crud_mngr._drop_tables('schema', mock_connect.cnx.cursor)

    correct_calls = [
        mock.call('DROP TABLE three;'),
        mock.call('DROP TABLE two;'),
        mock.call('DROP TABLE one;')
        ]
    mock_connect.cnx.cursor.execute.assert_has_calls(correct_calls)


def test_drop_tables_returns_success(mock_connect, mock_utility):  # noqa: D103
    message = crud_mngr._drop_tables('schema', mock_connect.cnx.cursor)
    assert message == 'Success.'


# ----------------------------------------------------------------------------
# setup_experiment_tables


def test_setup_tables_returns_success(mock_ConfigParser, mock_connect, mock_utility):  # noqa: D103
    message = crud_mngr.setup_tables('schema')
    assert message == 'Success.'


# ----------------------------------------------------------------------------
# helpers


def _configparser_key_setter(configparser, keys):
    configparser['MySQL-Server'].keys.return_value.__iter__.return_value = (
        keys
        )
