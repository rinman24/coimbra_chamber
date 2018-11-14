"""CRUD manager unit test suite."""

import chamber.manager.crud as crud_mngr

# ----------------------------------------------------------------------------
# build_tables


def test_can_create_experiment_tables():  # noqa: D103
    message = crud_mngr.create_tables('experiment', 'test')
    print(message)
    assert message == 'Successfully built `experiment` tables in `test`.'


def test_can_add_tube():  # noqa: D103
    message = crud_mngr.add_tube('test')
    print(message)
    assert message == 'Sucessfully added default tube to `test`.'

# ----------------------------------------------------------------------------
# drop_tables


def test_can_drop_experiment_tables():  # noqa: D103
    message = crud_mngr.drop_tables('experiment', 'test', drop_db=True)
    print(message)
    assert message == (
        'Successfully dropped `experiment` tables from `test`. '
        'Database `test` also dropped.'
        )
