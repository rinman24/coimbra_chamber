"""CRUD manager unit test suite."""

import unittest.mock as mock

from mysql.connector import Error as mysql_Error
import pytest

import chamber.manager.crud as crud_mngr

_CORRECT_CREDS = dict(host='address', user='me', password='secret')
_SETUP_MESSAGE = 'Successfully built `group` tables.'
_FULL_SETUP_MESSAGE = 'Successfully built `group` tables in `schema`.'
_TEARDOWN_MESSAGE = 'Successfully dropped `group` tables.'
_FULL_TEARDOWN_MESSAGE = 'Successfully dropped `group` tables from `schema`.'

_ENGINE_INTANCE = (
    'Engine(mysql+mysqlconnector://me:***@address:3306/test_schema)'
    )


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
    create_engine.return_value = _ENGINE_INTANCE
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


def test_connect_executes_use_database_when_given(mock_mysql):  # noqa: D103
    crud_mngr._connect(_CORRECT_CREDS, database='schema')

    mock_mysql.cur.execute.assert_called_once_with('USE schema;')


def test_connect_does_not_execute_use_database_by_default(mock_mysql):  # noqa: D103
    crud_mngr._connect(_CORRECT_CREDS)

    mock_mysql.cur.execute.assert_not_called()


# ----------------------------------------------------------------------------
# _execute_build


def test_execute_build_executes_calls_in_correct_order(
        mock_mysql, mock_utility
        ):  # noqa: D103
    crud_mngr._execute_build(mock_mysql.cur, 'group')

    correct_calls = [mock.call('foo'), mock.call('bar'), mock.call('bacon!')]
    mock_mysql.cur.execute.assert_has_calls(correct_calls)


def test_execute_build_returns_success(
        mock_mysql, mock_utility
        ):  # noqa: D103
    message = crud_mngr._execute_build(mock_mysql.cur, 'group')
    assert message == _SETUP_MESSAGE


# ----------------------------------------------------------------------------
# _execute_drop


def test_execute_drop_executes_calls_in_correct_order(
        mock_mysql, mock_utility
        ):  # noqa D103
    crud_mngr._execute_drop(mock_mysql.cur, 'group')

    correct_calls = [
        mock.call('DROP TABLE three;'),
        mock.call('DROP TABLE two;'),
        mock.call('DROP TABLE one;')
        ]
    mock_mysql.cur.execute.assert_has_calls(correct_calls)


def test_execute_drop_returns_success(
        mock_mysql, mock_utility
        ):  # noqa: D103
    message = crud_mngr._execute_drop(mock_mysql.cur, 'group')
    assert message == _TEARDOWN_MESSAGE


# ----------------------------------------------------------------------------
# _get_engine


def test_get_engine_calls_create_engine(mock_sqlalchemy):  # noqa: D103
    crud_mngr._get_engine('test_schema', _CORRECT_CREDS)

    correct_url = 'mysql+mysqlconnector://me:secret@address:3306/test_schema'
    mock_sqlalchemy.create_engine.assert_called_once_with(
        correct_url
        )


def test_get_engine_returns_correct_value(mock_sqlalchemy):  # noqa: D103
    engine = crud_mngr._get_engine('test_schema', _CORRECT_CREDS)

    assert engine == _ENGINE_INTANCE


# ----------------------------------------------------------------------------
# create_tables


def test_create_tables_returns_success(
        mock_ConfigParser, mock_mysql, mock_utility
        ):  # noqa: D103
    message = crud_mngr.create_tables('group', 'schema')
    assert message == _FULL_SETUP_MESSAGE


def test_create_tables_creates_db_if_does_not_exists(
        mock_ConfigParser, mock_mysql, mock_utility
        ):  # noqa: D103
    crud_mngr.create_tables('group', 'schema')
    mock_mysql.cur.execute.assert_any_call(
        'CREATE DATABASE IF NOT EXISTS schema DEFAULT CHARACTER SET latin1 ;'
        )


def test_create_tables_catches_mysql_errors_during_connect_call(mock_mysql):  # noqa: D103
    mock_mysql.connect.side_effect = mysql_Error('Test error.')
    mock_mysql.connect.return_value = None

    message = crud_mngr.create_tables('group', 'schema')

    assert message == 'mySQL Error: Test error.'


# ----------------------------------------------------------------------------
# drop_tables


def test_drop_tables_returns_success(
        mock_ConfigParser, mock_mysql, mock_utility
        ):  # noqa: D103
    message = crud_mngr.drop_tables('group', 'schema')
    assert message == _FULL_TEARDOWN_MESSAGE


def test_drop_tables_drops_db_if_drop_db_is_true(
        mock_ConfigParser, mock_mysql, mock_utility
        ):  # noqa: D103
    crud_mngr.drop_tables('group', 'schema', drop_db=True)
    mock_mysql.cur.execute.assert_called_with(
        'DROP DATABASE schema;'
        )


def test_drop_tables_with_drop_db_true_has_extended_message(
        mock_ConfigParser, mock_mysql, mock_utility
        ):  # noqa: D103
    message = crud_mngr.drop_tables('group', 'schema', drop_db=True)
    assert message == (
        _FULL_TEARDOWN_MESSAGE + ' Database `schema` also dropped.'
        )


# ----------------------------------------------------------------------------
# add_tube


def test_add_tube_calls_to_sql_with_correct_inputs(
        mock_ConfigParser,
        mock_sqlalchemy,
        mock_pd
        ):  # noqa: D103

    crud_mngr.add_tube('test_schema')

    correct_params = dict(
        name='Tube', con=_ENGINE_INTANCE, if_exists='append', index=False
        )
    mock_pd.DataFrame.to_sql.assert_called_once_with(**correct_params)


def test_add_tube_returns_correct_message(
        mock_ConfigParser,
        mock_sqlalchemy,
        mock_pd
        ):  # noqa: D103

    message = crud_mngr.add_tube('test_schema')

    assert message == 'Sucessfully added default tube to `test_schema`.'


# ----------------------------------------------------------------------------
# helpers


def _configparser_key_setter(configparser, keys):
    configparser['MySQL-Server'].keys.return_value.__iter__.return_value = (
        keys
        )
