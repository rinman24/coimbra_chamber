"""Smoke test suite for analysis manager."""

import pytest  # NOTE: Temporary

from chamber.manager.analysis.service import AnalysisManager


@pytest.mark.skip(reason='Waiting to get access tests back in order.')
def test_add_data():  # noqa: D103
    # Arrange ----------------------------------------------------------------

    anlys_mngr = AnalysisManager()

    # Act --------------------------------------------------------------------

    result = anlys_mngr.add_data()

    # Assert -----------------------------------------------------------------

    assert result
