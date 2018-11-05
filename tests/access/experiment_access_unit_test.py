"""Experiment access unit test suite."""

import unittest.mock as mock

import pytest

import chamber.access.experiment as exp_acc
import chamber.utility.ddl as ddl


def test_can_call_build_experiment_tables(monkeypatch):  # noqa: D103
    mock_cursor = mock.MagicMock()
    mock_cursor.execute = mock.MagicMock()

    mock_build_instructions = {
        ('experiments', 'table order'): ('one', 'two', 'three'),
        ('experiments', 'ddl'): dict(one='foo', two='bar', three='bacon!')
        }

    monkeypatch.setattr(
        'chamber.utility.ddl.build_instructions',
        mock_build_instructions
        )

    exp_acc.build_tables(mock_cursor)

    mock_cursor.execute.assert_has_calls(
        list(
            mock.call(mock_build_instructions['experiments', 'ddl'][table])
            for table
            in mock_build_instructions['experiments', 'table order']
            )
        )
