"""Experiment access unit test suite."""

import unittest.mock as mock

import pytest

import chamber.access.experiment as exp_acc


_DB_CREDENTIALS = dict(
    host='host', user='user', password='password', database='database'
    )


@pytest.fixture
def mock_mysql_connector(monkeypatch):
    """Avoid call to external mySQL database."""
    mock_mysql_connector = mock.MagicMock()
    mock_mysql_connector.connect = mock.MagicMock(return_value='cnx')

    monkeypatch.setattr(
        'mysql.connector.connect', mock_mysql_connector.connect
        )

    return mock_mysql_connector


def test_can_call_connect(mock_mysql_connector, monkeypatch):  # noqa: D103
    exp_acc.connect(**_DB_CREDENTIALS)
    mock_mysql_connector.connect.assert_called_with(**_DB_CREDENTIALS)


def test_connect_returns_cnx(mock_mysql_connector, monkeypatch):  # noqa: D103
    result = exp_acc.connect(**_DB_CREDENTIALS)
    assert result == 'cnx'
