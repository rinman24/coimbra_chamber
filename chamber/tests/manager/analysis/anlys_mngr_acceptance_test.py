"""Smoke test suite for data manager."""

import pytest  # NOTE: Temporary

from chamber.manager.data.service import DataManager


def test_add_data(tube_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data_mngr = DataManager()
    # We must add a tube for the smoke test to work.
    data_mngr._exp_acc._add_tube(tube_spec)

    expected = dict(
        tube_id=1, setting_id=1, experiment_id=1,
        observations=3, temperatures=30,
        )
    # Act --------------------------------------------------------------------
    result = data_mngr.add_data()

    # Assert -----------------------------------------------------------------
    assert result == expected

    # Clean up ---------------------------------------------------------------
    data_mngr._exp_acc._teardown()
