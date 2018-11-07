"""CRUD manager unit test suite."""

import chamber.manager.crud as crud_mngr

# ----------------------------------------------------------------------------
# build_tables


def test_can_create_experiment_tables():  # noqa: D103
    message = crud_mngr.create_tables('experiment')
    assert message == 'Successfully build experiment tables.' 
