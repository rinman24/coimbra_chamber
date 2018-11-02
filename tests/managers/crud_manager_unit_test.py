"""CRUD manager unit test suite."""

import unittest.mock as mock

import pytest

import chamber.managers.crud as crud_mngr


def test_can_call_get_creds(monkeypatch):  # noqa: D103
    mock_config = mock.MagicMock()
    mock_config.read = mock.MagicMock()
    monkeypatch.setattr(
        'configparser.ConfigParser.read', mock_config.read
        )

    mock_ConfigParser = mock.MagicMock(return_value=mock_config)
    monkeypatch.setattr('configparser.ConfigParser', mock_ConfigParser)

    # The following lines are required for the mock of config['MySQL-Server']
    # section to behave properly in the dict(config['MySQL-Server']) call.
    mock_config['MySQL-Server'] = mock.MagicMock()
    mock_config['MySQL-Server'].keys.return_value.__iter__.return_value = [
        'host', 'user', 'password'
        ]
    mock_config['MySQL-Server'].__getitem__.side_effect = [
        'test_host', 'test_user', 'test_password'
        ]

    crud_mngr.get_credentials()

    mock_config.read.assert_called_once_with('config.ini')
