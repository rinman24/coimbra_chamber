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
    mock_config['MySQL-Server'].keys.return_value.__iter__.return_value = [
        'host', 'user', 'password'
        ]
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


def test_can_call_get_creds(mock_ConfigParser, mock_config):  # noqa: D103
    crud_mngr.get_credentials('test_database')

    mock_config.read.assert_called_once_with('config.ini')


def test_get_creds_returns_correct_dict(mock_ConfigParser, mock_config):  # noqa: D103
    creds = crud_mngr.get_credentials('test_database')

    correct_creds = dict(
        host='test_host', user='test_user', password='test_password',
        database='test_database'
        )
    assert creds == correct_creds
