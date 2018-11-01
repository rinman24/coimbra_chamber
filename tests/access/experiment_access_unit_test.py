"""Experiment access unit test suite."""

import unittest.mock as mock

import pytest

import chamber.access.experiment as exp_acc


_DB_CREDENTIALS = dict(
    host='host', user='user', password='password', database='database'
    )


def test_connect_returns_cnx(monkeypatch):  # noqa: D103
    mock_cnx = mock.MagicMock()
    mock_mysql_connector = mock.MagicMock()
    mock_mysql_connector.connect = mock.MagicMock(return_value=mock_cnx)

    monkeypatch.setattr(
        'mysql.connector.connect', mock_mysql_connector.connect
        )
    cnx = exp_acc.connect(**_DB_CREDENTIALS)
    assert cnx == mock_cnx


def test_can_call_build_table():  # noqa: D103
    exp_acc.build_table()
