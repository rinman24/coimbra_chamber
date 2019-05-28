"""Smoke test suite for analysis manager."""

import pytest  # NOTE: Temporary

from chamber.manager.analysis.service import AnalysisManager


@pytest.mark.skip(reason='organizing the exp access layout raw data first.')
def test_add_data():  # noqa: D103
    # Arrange ----------------------------------------------------------------

    anlys_mngr = AnalysisManager()

    # Act --------------------------------------------------------------------

    result = anlys_mngr.add_data()

    # Assert -----------------------------------------------------------------

    assert True
