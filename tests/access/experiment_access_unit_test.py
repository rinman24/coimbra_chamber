"""Experiment access unit test suite."""

import unittest.mock as mock

import pytest

import chamber.access.experiment as exp_acc
import chamber.utility.ddl as ddl


@pytest.fixture
def cursor(monkeypatch):
    """Mock mysql cursor object."""
    cursor = mock.MagicMock()
    cursor.execute = mock.MagicMock()
    return cursor


@pytest.fixture
def utility(monkeypatch):
    """Mock chamber.utility."""
    utility = mock.MagicMock()
    utility.ddl.build_instructions = {
        ('experiments', 'table order'): ('one', 'two', 'three'),
        ('experiments', 'ddl'): dict(one='foo', two='bar', three='bacon!')
        }
    monkeypatch.setattr(
        'chamber.utility.ddl.build_instructions',
        utility.ddl.build_instructions
        )
    return utility


def test_can_call_build_experiment_tables(cursor, utility):  # noqa: D103
    exp_acc.build_tables(cursor)

    cursor.execute.assert_has_calls(
        list(
            mock.call(
                utility.ddl.build_instructions['experiments', 'ddl'][table]
                )
            for table
            in utility.ddl.build_instructions['experiments', 'table order']
            )
        )
