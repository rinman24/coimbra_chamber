"""CRUD manager unit test suite."""

import chamber.manager.crud as crud_mngr

# ----------------------------------------------------------------------------
# build_tables


def test_can_create_experiment_tables():  # noqa: D103
    message = crud_mngr.create_tables('experiment', 'test')
    assert message == 'Successfully built `experiment` tables in `test`.'


# ----------------------------------------------------------------------------
# drop_tables


def test_can_drop_experiment_tables():  # noqa: D103
    message = crud_mngr.drop_tables('experiment', 'test', drop_db=True)
    assert message == (
        'Successfully dropped `experiment` tables from `test`. '
        'Database `test` also dropped.'
        )
