"""Analysis engine service."""


from chamber.access.experiment.service import ExperimentAccess


class AnalysisEngine(object):
    """Analysis engine."""

    def __init__(self):
        """Constructor."""
        self._exp_acc = ExperimentAccess()

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def perform_analysis(self, data, uncert):
        """TODO: docstring."""
        self._preprocess(data, uncert)
        self._regress_mass_flux()
        self._persist_results()

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _preprocess(self, data, uncert):
        # TODO: Implement.
        pass

    def _regress_mass_flux(self):
        # TODO: Implement.
        pass

    def _persist_results(self):
        # TODO: Implement.
        pass
