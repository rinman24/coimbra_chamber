"""CRUD manager unit test suite."""

import chamber.manager.crud as crud_mngr

# ----------------------------------------------------------------------------
# build_tables


def test_can_create_experiment_tables():  # noqa: D103
    message = crud_mngr.create_tables('experiment')
    assert message == 'Successfully built experiment tables.'


# ----------------------------------------------------------------------------
# drop_tables


def test_can_drop_experiment_tables():  # noqa: D103
    message = crud_mngr.drop_tables('experiment', drop_db=True)
    assert message == (
        'Successfully dropped experiment tables. Database also dropped.'
        )
