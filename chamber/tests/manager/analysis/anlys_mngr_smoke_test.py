"""Smoke test suite for analysis manager."""


from chamber.manager.analysis.service import AnalysisManager


def test_add_data():  # noqa: D103
    # Arrange ----------------------------------------------------------------

    anlys_mngr = AnalysisManager()

    # Act --------------------------------------------------------------------

    result = anlys_mngr.add_data()

    # Assert -----------------------------------------------------------------

    assert result
