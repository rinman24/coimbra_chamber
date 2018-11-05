"""CRUD manager unit test suite."""

import chamber.manager.crud as crud_mngr

# ----------------------------------------------------------------------------
# setup_experiment_tables


def test_setup_experiment_tables_returns_success():  # noqa: D103
    message = crud_mngr.setup_experiment_tables('schema')
    assert message == 'Success.'
