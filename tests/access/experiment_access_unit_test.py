"""Experiment access unit test suite."""

import unittest.mock as mock

import pytest

import chamber.access.experiment as exp


def test_connect_returns_cnx(monkeypatch):  # noqa D103
    mock_mysql_connector = mock.MagicMock()
    mock_mysql_connector.connect = mock.MagicMock(return_value='cnx')
    monkeypatch.setattr(
        'mysql.connector.connect', mock_mysql_connector.connect
        )
    config = dict(
        host='host',
        user='user',
        password='password',
        database='database'
        )
    result = exp.connect(**config)
    mock_mysql_connector.connect.assert_called_with(**config)
    assert result == 'cnx'
