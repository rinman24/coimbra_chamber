"""Integration test suite for analysis engine."""


# ----------------------------------------------------------------------------
# Fixtures


# ----------------------------------------------------------------------------
# AnalysisEngine


def test_persist_fits(anlys_eng):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Use exp access to add some tubes, setting, and experiment.
        # You have many of these in conftest already.
        # We should also have a new (clean) instance of the db for this module.
    # Once you add the experiment you are free to add the fits.
        # So you want to set up all of the fits that you want it to add
        # Once you have a list of all the fits, you move on
    # Act --------------------------------------------------------------------
    # Here you want to call _persist_fits with the list you made
    # Assert -----------------------------------------------------------------
    # Now, we want to use exp access again to select all of the fits using a
    # query.
    # Once we have the results of the query we want to make sure that all of
    # The fits match up.
    pass
