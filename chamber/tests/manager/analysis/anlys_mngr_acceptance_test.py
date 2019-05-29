"""Smoke test suite for analysis manager."""

import pytest  # NOTE: Temporary

from chamber.manager.analysis.service import AnalysisManager


def test_add_data(tube_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    anlys_mngr = AnalysisManager()
    # We must add a tube for the smoke test to work.
    anlys_mngr._exp_acc._add_tube(tube_spec)

    expected = dict(
        tube_id=1, setting_id=1, experiment_id=1,
        observations=3, temperatures=30,
        )
    # Act --------------------------------------------------------------------
    result = anlys_mngr.add_data()

    # Assert -----------------------------------------------------------------
    assert result == expected

    # Clean up ---------------------------------------------------------------
    anlys_mngr._exp_acc._teardown()
