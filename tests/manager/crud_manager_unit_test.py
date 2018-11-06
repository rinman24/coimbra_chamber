"""CRUD manager unit test suite."""

import unittest.mock as mock

import pytest

import chamber.manager.crud as crud_mngr

_CORRECT_CREDS = dict(host='address', user='me', password='secret')
_SETUP_MESSAGE = 'Sucessfully built schema tables.'
_TEARDOWN_MESSAGE = 'Sucessfully dropped schema tables.'


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


def test_get_credentials_returns_correct_dict(
        mock_ConfigParser
        ):  # noqa: D103
    creds = crud_mngr._get_credentials()

    assert creds == _CORRECT_CREDS


def test_get_credentials_exception_knows_the_name_missing_key(
        mock_ConfigParser
        ):  # noqa: D103
    _configparser_key_setter(
        mock_ConfigParser.configparser, ['user', 'password']
        )

    err_message = (
        'KeyError: config file is missing the following key: host.'
        )

    with pytest.raises(KeyError, match=err_message):
        crud_mngr._get_credentials()


def test_get_credentials_raises_file_not_found_error(
        mock_ConfigParser
        ):  # noqa: D103
    mock_ConfigParser.configparser.read.return_value = []

    error_message = ('FileNotFoundError: config.ini does not exits.')
    with pytest.raises(FileNotFoundError, match=error_message):
        crud_mngr._get_credentials()


# ----------------------------------------------------------------------------
# _connect

def test_connect_calls_connect_before_cursor(mock_mysql):  # noqa: D103
    crud_mngr._connect(_CORRECT_CREDS)

    correct_calls = [
        mock.call.connect(**_CORRECT_CREDS),
        mock.call.cnx.cursor()
        ]
    mock_mysql.assert_has_calls(correct_calls)


def test_connect_returns_cnx_and_cur(mock_mysql):  # noqa: D103
    cnx, cur = crud_mngr._connect(_CORRECT_CREDS)

    assert cnx == mock_mysql.cnx
    assert cur == mock_mysql.cur


# ----------------------------------------------------------------------------
# _execute_build


def test_execute_build_executes_calls_in_correct_order(
        mock_connect, mock_utility
        ):  # noqa: D103
    crud_mngr._execute_build('schema', mock_connect.cnx.cursor)

    correct_calls = [mock.call('foo'), mock.call('bar'), mock.call('bacon!')]
    mock_connect.cnx.cursor.execute.assert_has_calls(correct_calls)


def test_execute_build_returns_success(
        mock_connect, mock_utility
        ):  # noqa: D103
    message = crud_mngr._execute_build('schema', mock_connect.cnx.cursor)
    assert message == _SETUP_MESSAGE


# ----------------------------------------------------------------------------
# _execute_drop


def test_execute_drop_executes_calls_in_correct_order(
        mock_connect, mock_utility
        ):  # noqa D103
    crud_mngr._execute_drop('schema', mock_connect.cnx.cursor)

    correct_calls = [
        mock.call('DROP TABLE three;'),
        mock.call('DROP TABLE two;'),
        mock.call('DROP TABLE one;')
        ]
    mock_connect.cnx.cursor.execute.assert_has_calls(correct_calls)


def test_execute_drop_returns_success(
        mock_connect, mock_utility
        ):  # noqa: D103
    message = crud_mngr._execute_drop('schema', mock_connect.cnx.cursor)
    assert message == _TEARDOWN_MESSAGE


# ----------------------------------------------------------------------------
# build_tables


def test_build_tables_returns_success(
        mock_ConfigParser, mock_connect, mock_utility
        ):  # noqa: D103
    message = crud_mngr.build_tables('schema')
    assert message == _SETUP_MESSAGE


# ----------------------------------------------------------------------------
# drop_tables


def test_drop_tables_returns_success(
        mock_ConfigParser, mock_connect, mock_utility
        ):  # noqa: D103
    message = crud_mngr.drop_tables('schema')
    assert message == _TEARDOWN_MESSAGE


# ----------------------------------------------------------------------------
# helpers


def _configparser_key_setter(configparser, keys):
    configparser['MySQL-Server'].keys.return_value.__iter__.return_value = (
        keys
        )
