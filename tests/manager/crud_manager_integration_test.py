"""CRUD manager unit test suite."""

import chamber.manager.crud as crud_mngr

# ----------------------------------------------------------------------------
# build_tables


def test_setup_experiment_tables_returns_success():  # noqa: D103
    message = crud_mngr.build_tables('schema')
    assert message == 'Success.' 
