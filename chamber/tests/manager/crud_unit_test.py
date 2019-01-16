"""CRUD manager unit test suite."""

import unittest.mock as mock

from mysql.connector import Error as mysql_Error
import pandas as pd
import pytest

import chamber.manager.crud.service as crud_mngr

_CORRECT_CREDS = dict(host='address', user='me', password='secret')
_SETUP_MESSAGE = 'Successfully built `group` tables.'
_FULL_SETUP_MESSAGE = 'Successfully built `group` tables in `schema`.'
_TEARDOWN_MESSAGE = 'Successfully dropped `group` tables.'
_FULL_TEARDOWN_MESSAGE = 'Successfully dropped `group` tables from `schema`.'

_ENGINE_INSTANCE = (
    'Engine(mysql+mysqlconnector://me:***@address:3306/test_schema)'
    )

_TEST_FILEPATH = 'C:/Users/Me/test_experiment.tdms'

_LAST_ROW_ID = 924

_DATABASE = 'test_schema'


@pytest.fixture()
def mock_ConfigParser(monkeypatch):
    """Mock of the configparser.ConfigParser class."""
    configparser = mock.MagicMock()
    configparser.read = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.manager.crud.service.configparser.ConfigParser.read',
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
        'chamber.manager.crud.service.configparser.ConfigParser',
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
        'chamber.manager.crud.service.mysql.connector.connect', connect_method
        )
    monkeypatch.setattr(
        (
            'chamber.manager.crud.service.mysql.connector.connection.MySQLConnection'
            '.cursor'
            ),
        cursor_method
        )
    monkeypatch.setattr(
        'chamber.manager.crud.service.mysql.connector.cursor.MySQLCursor.execute',
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
        'chamber.manager.crud.service.sqlalchemy.create_engine',
        create_engine
        )

    return mock_sqlalchemy


@pytest.fixture()
def mock_pd(monkeypatch):
    """Mock of pandas package."""
    mock_pd = mock.MagicMock()

    mock_pd.read_sql_query.return_value.iloc.__getitem__.return_value = (
        _LAST_ROW_ID
        )
    monkeypatch.setattr(
        'chamber.manager.crud.service.pd.read_sql_query',
        mock_pd.read_sql_query
        )

    monkeypatch.setattr(
        'chamber.manager.crud.service.pd.core.frame.DataFrame.to_sql',
        mock_pd.DataFrame.to_sql
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
    monkeypatch.setattr('chamber.manager.crud.service.tk.Tk', Tk)
    Tk.return_value = root

    filedialog = mock_tk.filedialog
    askopenfilename = filedialog.askopenfilename
    monkeypatch.setattr(
        'chamber.manager.crud.service.filedialog.askopenfilename',
        askopenfilename
        )
    askopenfilename.return_value = 'C:/Users/Me/test_experiment.tdms'

    return mock_tk


@pytest.fixture()
def mock_engine(mock_pd, monkeypatch):
    """Mock chamber.engine."""
    mock_engine = mock.MagicMock()
    mock_engine.read_tdms.return_value = dict(
        setting=mock_pd.DataFrame,
        test=mock_pd.DataFrame,
        observation=mock_pd.DataFrame,
        temp_observation=mock_pd.DataFrame
        )

    monkeypatch.setattr(
        'chamber.manager.crud.service.anlys_eng.read_tdms', mock_engine.read_tdms
        )

    return mock_engine


@pytest.fixture()
def mock_input(monkeypatch):
    """Mock builtin input wrapper."""
    mock_input = mock.MagicMock(return_value='y')

    monkeypatch.setattr('builtins.input', mock_input)

    return mock_input


@pytest.fixture()
def mock_plt(monkeypatch):
    """Mock plotting."""
    mock_plt = mock.MagicMock()
    mock_plt.subplots.return_value = ('fig', [0, 1, 2, 3])

    monkeypatch.setattr('chamber.manager.crud.service.plt', mock_plt)

    return mock_plt

# ----------------------------------------------------------------------------
# _get_credentials


def test_can_call_get_credentials(mock_ConfigParser):  # noqa: D103
    crud_mngr._get_credentials()

    mock_ConfigParser.configparser.read.assert_called_once_with('config.ini')


def test_get_credentials_returns_correct_dict(mock_ConfigParser):  # noqa: D103
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


def test_get_credentials_raises_file_not_found_error(mock_ConfigParser):  # noqa: D103
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


def test_execute_build_returns_success(mock_mysql, mock_utility):  # noqa: D103
    message = crud_mngr._execute_build(mock_mysql.cur, 'group')
    assert message == _SETUP_MESSAGE


# ----------------------------------------------------------------------------
# _execute_drop


def test_execute_drop_executes_calls_in_correct_order(
        mock_mysql, mock_utility
        ):  # noqa: D103
    crud_mngr._execute_drop(mock_mysql.cur, 'group')

    correct_calls = [
        mock.call('DROP TABLE three;'),
        mock.call('DROP TABLE two;'),
        mock.call('DROP TABLE one;')
        ]
    mock_mysql.cur.execute.assert_has_calls(correct_calls)


def test_execute_drop_returns_success(mock_mysql, mock_utility):  # noqa: D103
    message = crud_mngr._execute_drop(mock_mysql.cur, 'group')
    assert message == _TEARDOWN_MESSAGE


# ----------------------------------------------------------------------------
# _get_engine


def test_get_engine_calls_create_engine(mock_sqlalchemy):  # noqa: D103
    crud_mngr._get_engine(_DATABASE, _CORRECT_CREDS)

    correct_url = (
        'mysql+mysqlconnector://me:secret@address:3306/{}'.format(_DATABASE)
        )
    mock_sqlalchemy.create_engine.assert_called_once_with(
        correct_url
        )


def test_get_engine_returns_correct_value(mock_sqlalchemy):  # noqa: D103
    engine = crud_mngr._get_engine(_DATABASE, _CORRECT_CREDS)

    assert engine == _ENGINE_INSTANCE


# ----------------------------------------------------------------------------
# _get_experimental_data


def test_get_experimental_data_calls_askopenfilename(mock_tk, mock_engine):  # noqa: D103
    # Act
    crud_mngr._get_experimental_data()

    # Assert
    correct_calls = [
        mock.call.Tk(),
        mock.call.root.withdraw(),
        mock.call.filedialog.askopenfilename(title='Select Experiment')
        ]

    mock_tk.assert_has_calls(correct_calls)


def test_get_experimental_data_calls_analysis_engine(mock_tk, mock_engine):  # noqa: D103
    # Arrange
    path = mock_tk.filedialog.askopenfilename.return_value

    # Act
    crud_mngr._get_experimental_data()

    # Assert
    mock_engine.read_tdms.assert_called_once_with(path)


def test_get_experimental_data_returns_correct(mock_tk, mock_engine):  # noqa: D103
    # Arrange
    correct_return_value = mock_engine.read_tdms.return_value

    # Act
    databases = crud_mngr._get_experimental_data()

    # Assert
    assert databases == correct_return_value


# ----------------------------------------------------------------------------
# _query_last_row_id


def test_query_lastrow_id_returns_correct_value(mock_pd):  # noqa: D103
    # Arrange
    correct_return_value = _LAST_ROW_ID

    # Act
    last_row_id = crud_mngr._query_last_row_id('Test', 'SettingId', 'engine')

    # Assert
    assert (last_row_id == correct_return_value)


# ----------------------------------------------------------------------------
# _update_table


def test_update_table_adds_col_if_necessary(mock_pd):  # noqa: D103
    # Arrange
    dataframe = pd.DataFrame(index=range(10))
    column, value = 'test_row', 123

    # Act
    return_value = crud_mngr._update_table(
        table='test_table',
        dataframe=dataframe,
        engine=_ENGINE_INSTANCE,
        col_to_add=(column, value)
        )

    # Assert
    unique_values = set(dataframe.loc[:, column])
    assert unique_values.pop() == value
    assert not unique_values
    assert not return_value


def test_update_table_calls_to_sql_correctly(mock_pd):  # noqa: D103
    # Arrange
    correct_params = dict(
        name='test_table', con=_ENGINE_INSTANCE, if_exists='append',
        index=False
        )

    # Act
    return_value = crud_mngr._update_table(
        table='test_table',
        dataframe=mock_pd.DataFrame,
        engine=_ENGINE_INSTANCE
        )

    # Assert
    mock_pd.DataFrame.to_sql.assert_called_once_with(**correct_params)
    assert not return_value


def test_update_table_returns_last_row_id_if_necessary(mock_pd):  # noqa: D103
    # Arrange
    table, column = 'test_table', 'table_id'

    # Act
    requested_id = crud_mngr._update_table(
        table=table,
        dataframe=mock_pd.DataFrame,
        engine=_ENGINE_INSTANCE,
        id_to_get=column
        )

    # Assert
    assert requested_id == _LAST_ROW_ID


# -----------------------------------------------------------------------------
# _query_setting_exists

@pytest.mark.parametrize(
    'query_results, expected',
    [
        (pd.DataFrame(data=[1]), 1),
        (pd.DataFrame(), False)
        ]
    )
def test_query_setting_exists_returns_correct_value(
        query_results, expected, mock_pd):  # noqa: D103
    # Arrange
    setting_df = pd.DataFrame(
        data=dict(
            Duty=[1],
            Pressure=[int(80e3)],
            Temperature=[300],
            IsMass=[1],
            Reservoir=[1],
            TimeStep=[1],
            TubeID=[1]
            )
        )
    dataframes = dict(setting=setting_df)

    mock_pd.read_sql_query.return_value = query_results

    # Act
    setting_id = crud_mngr._query_setting_exists(dataframes, _ENGINE_INSTANCE)

    # Assert
    assert setting_id == expected


# -----------------------------------------------------------------------------
# _query_test_exists


@pytest.mark.parametrize(
    'query_results, expected',
    [
        (pd.DataFrame(data=[2]), 2),
        (pd.DataFrame(), False)
        ]
    )
def test_query_test_exists_returns_correct_value(
        query_results, expected, mock_pd):  # noqa: D103
    # Arrange
    test_df = pd.DataFrame(
        data=dict(
            Author=['Me'],
            DateTime=['1/1/2018 0:0:0'],
            Description=['Details...']
            )
        )
    dataframes = dict(test=test_df)

    mock_pd.read_sql_query.return_value = query_results

    # Act
    test_id = crud_mngr._query_test_exists(dataframes, _ENGINE_INSTANCE)

    # Assert
    assert test_id == expected


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


def test_create_tables_catches_mysql_errors_during_connect_call(
        mock_ConfigParser, mock_mysql
        ):  # noqa: D103
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
    # Arrange
    correct_params = dict(
        name='Tube', con=_ENGINE_INSTANCE, if_exists='append', index=False
        )

    # Act
    crud_mngr.add_tube(_DATABASE)

    # Assert
    mock_pd.DataFrame.to_sql.assert_called_once_with(**correct_params)


def test_add_tube_returns_correct_message(
        mock_ConfigParser, mock_sqlalchemy, mock_pd
        ):  # noqa: D103
    correct_message = (
        'Sucessfully added default tube to `{}`.'.format(_DATABASE)
        )

    message = crud_mngr.add_tube(_DATABASE)

    assert message == correct_message


# ----------------------------------------------------------------------------
# add_experiment


def test_add_experiment_call_stack_when_setting_exists(
        mock_ConfigParser, mock_sqlalchemy, mock_pd, mock_engine, mock_tk,
        mock_input, mock_plt, monkeypatch
        ):  # noqa: D103
    # Arrange
    setting_id = 1
    _query_setting_exists = mock.MagicMock(return_value=setting_id)
    monkeypatch.setattr(
        'chamber.manager.crud.service._query_setting_exists', _query_setting_exists
        )

    mock_update_table = mock.MagicMock(return_value=_LAST_ROW_ID)
    monkeypatch.setattr(
        'chamber.manager.crud.service._update_table', mock_update_table
        )
    correct_calls = [
        mock.call(
            'Test',
            mock_engine.read_tdms.return_value['test'],
            _ENGINE_INSTANCE,
            col_to_add=('SettingId', setting_id),
            id_to_get='TestId'
            ),
        mock.call(
            'Observation',
            mock_engine.read_tdms.return_value['observation'],
            _ENGINE_INSTANCE,
            col_to_add=('TestId', _LAST_ROW_ID)
            ),
        mock.call(
            'TempObservation',
            mock_engine.read_tdms.return_value['temp_observation'],
            _ENGINE_INSTANCE,
            col_to_add=('TestId', _LAST_ROW_ID)
            )
        ]
    incorrect_call = mock.call(
        'Setting',
        mock_engine.read_tdms.return_value['setting'],
        _ENGINE_INSTANCE,
        id_to_get='SettingId'
        )

    # Act
    crud_mngr.add_experiment(_DATABASE)

    # Assert
    mock_update_table.assert_has_calls(correct_calls)
    assert incorrect_call not in mock_update_table.mock_calls


def test_add_experiment_call_stack_when_not_setting_exists(
        mock_ConfigParser, mock_sqlalchemy, mock_pd, mock_engine, mock_tk,
        mock_input, mock_plt, monkeypatch
        ):  # noqa: D103
    # Arrange
    setting_id = False
    _query_setting_exists = mock.MagicMock(return_value=setting_id)
    monkeypatch.setattr(
        'chamber.manager.crud.service._query_setting_exists', _query_setting_exists
        )

    mock_update_table = mock.MagicMock(return_value=_LAST_ROW_ID)
    monkeypatch.setattr(
        'chamber.manager.crud.service._update_table', mock_update_table
        )
    correct_calls = [
        mock.call(
            'Setting',
            mock_engine.read_tdms.return_value['setting'],
            _ENGINE_INSTANCE,
            id_to_get='SettingId'
            ),
        mock.call(
            'Test',
            mock_engine.read_tdms.return_value['test'],
            _ENGINE_INSTANCE,
            col_to_add=('SettingId', _LAST_ROW_ID),
            id_to_get='TestId'
            ),
        mock.call(
            'Observation',
            mock_engine.read_tdms.return_value['observation'],
            _ENGINE_INSTANCE,
            col_to_add=('TestId', _LAST_ROW_ID)
            ),
        mock.call(
            'TempObservation',
            mock_engine.read_tdms.return_value['temp_observation'],
            _ENGINE_INSTANCE,
            col_to_add=('TestId', _LAST_ROW_ID)
            )
        ]

    # Act
    crud_mngr.add_experiment(_DATABASE)

    # Assert
    mock_update_table.assert_has_calls(correct_calls)


def test_add_experiment_call_stack_when_test_exists(
        mock_ConfigParser, mock_sqlalchemy, mock_pd, mock_engine, mock_tk,
        mock_input, mock_plt, monkeypatch
        ):  # noqa: D103
    # Arrange
    test_id = 2
    _query_test_exists = mock.MagicMock(return_value=test_id)
    monkeypatch.setattr(
        'chamber.manager.crud.service._query_test_exists', _query_test_exists
        )

    mock_update_table = mock.MagicMock(return_value=_LAST_ROW_ID)
    monkeypatch.setattr(
        'chamber.manager.crud.service._update_table', mock_update_table
        )
    correct_calls = [
        mock.call(
            'Setting',
            mock_engine.read_tdms.return_value['setting'],
            _ENGINE_INSTANCE,
            id_to_get='SettingId'
            )
        ]

    incorrect_call = mock.call(
            'Test',
            mock_engine.read_tdms.return_value['test'],
            _ENGINE_INSTANCE,
            col_to_add=('SettingId', _LAST_ROW_ID),
            id_to_get='TestId'
            )

    # Act
    crud_mngr.add_experiment(_DATABASE)

    # Assert
    mock_update_table.assert_has_calls(correct_calls)
    assert incorrect_call not in mock_update_table.mock_calls


@pytest.mark.parametrize(
    'user_input, expected_message',
    [
        ('', 'Successfully added experiment to `{}`.'.format(_DATABASE)),
        ('y', 'Successfully added experiment to `{}`.'.format(_DATABASE)),
        ('n', 'Experiment not loaded.'),
        ('foobar', 'Unrecognized response.')
        ]
    )
def test_add_experiment_returns_correct_with_user_input(
        user_input, expected_message, mock_ConfigParser, mock_sqlalchemy,
        mock_pd, mock_engine, mock_tk, mock_input, mock_plt
        ):  # noqa: D103
    # Arrange
    mock_input.return_value = user_input

    # Act
    message = crud_mngr.add_experiment(_DATABASE)

    # Assert
    assert (message == expected_message)


# ----------------------------------------------------------------------------
# helpers


def _configparser_key_setter(configparser, keys):
    """Change keys that configparser returns."""
    configparser['MySQL-Server'].keys.return_value.__iter__.return_value = (
        keys
        )
