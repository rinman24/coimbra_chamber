"""Integration test suite for AnalysisEngine."""


from chamber.access.sql.service import ChamberAccess
from chamber.access.tdms.service import TdmsAccess
from chamber.engine.analysis.service import AnalysisEngine


def test_constructor():  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Act --------------------------------------------------------------------
    analysis_engine = AnalysisEngine()
    # Assert -----------------------------------------------------------------
    assert isinstance(analysis_engine, AnalysisEngine)
    assert isinstance(analysis_engine._chamber_access, ChamberAccess)
    assert isinstance(analysis_engine._tdms_access, TdmsAccess)
