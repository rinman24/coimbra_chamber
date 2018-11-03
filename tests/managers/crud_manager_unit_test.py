"""CRUD manager unit test suite."""

import unittest.mock as mock

import pytest

import chamber.managers.crud as crud_mngr


@pytest.fixture
def mock_config(monkeypatch):
    """Mock of an instance of the configparser.ConfigParser() class."""
    mock_config = mock.MagicMock()
    mock_config.read = mock.MagicMock()
    monkeypatch.setattr(
        'configparser.ConfigParser.read', mock_config.read
        )

    # Production code calls Python builtin dict() on
    # mock_config['MySQL-Server'].
    mock_config['MySQL-Server'] = mock.MagicMock()
    _mock_config_key_setter(mock_config, ['host', 'user', 'password'])
    mock_config['MySQL-Server'].__getitem__.side_effect = [
        'test_host', 'test_user', 'test_password'
        ]

    return mock_config


@pytest.fixture
def mock_ConfigParser(mock_config, monkeypatch):
    """Mock of the configparser.ConfigParser() constructor."""
    mock_ConfigParser = mock.MagicMock(return_value=mock_config)
    monkeypatch.setattr('configparser.ConfigParser', mock_ConfigParser)
    return mock_ConfigParser


def test_can_call_get_credentials(mock_ConfigParser, mock_config):  # noqa: D103
    crud_mngr.get_credentials()

    mock_config.read.assert_called_once_with('config.ini')


def test_get_credentials_returns_correct_dict(mock_ConfigParser, mock_config):  # noqa: D103
    creds = crud_mngr.get_credentials()

    correct_creds = dict(
        host='test_host', user='test_user', password='test_password'
        )
    assert creds == correct_creds


def test_get_credentials_exception_knows_the_name_missing_key(
        mock_ConfigParser, mock_config
        ):  # noqa: D103
    _mock_config_key_setter(mock_config, ['user', 'password'])

    err_message = (
        'KeyError: config file is missing the following key: {}.'
        .format('host')
        )

    with pytest.raises(KeyError, match=err_message):
        crud_mngr.get_credentials()


def _mock_config_key_setter(mock_config, keys):
    mock_config['MySQL-Server'].keys.return_value.__iter__.return_value = (
        keys
        )
