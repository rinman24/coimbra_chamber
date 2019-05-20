"""Analysis engine module."""


from chamber.access.sql.service import ChamberAccess
from chamber.access.tdms.service import TdmsAccess


class AnalysisEngine(object):
    """Encapsulated all aspects of analysis of an experiment."""

    def __init__(self):
        """Create an instance of analysis engine with access components."""
        self._chamber_access = ChamberAccess()
        self._tdms_access = TdmsAccess()
