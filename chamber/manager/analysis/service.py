"""Analysis manager service."""


from chamber.access.experiment.service import ExperimentAccess
from chamber.utility.plot.service import PlotUtility


class AnalysisManager(object):
    """Analysis manager."""

    def __init__(self):
        """Constructor."""
        self._exp_acc = ExperimentAccess()
        self._plt_util = PlotUtility()

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def add_data(self):
        """Add data."""
        path = self._get_path()  # None -> str
        raw_data = self._exp_acc.get_raw_data(path)  # str -> DataSpec
        response = self._plt_util.plot(raw_data)
        if response:
            try:
                response = self._exp_acc.persist_raw_data(raw_data)  # DTO -> DTO
            except:
                print('Something went wrong.')
            else:
                return response  # DTO

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _get_path(self):
        """Get path as a string."""
        # TODO: Use Path to get a path string.
        return 'path'
