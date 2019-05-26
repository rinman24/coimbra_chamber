"""Experiment access service."""


class ExperimentAccess(object):
    """Experiment access."""

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def get_raw_data(self, path):
        """Get raw data."""
        return True

    def persist_raw_data(self, data):
        """Persist raw data."""
        return True

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    pass
