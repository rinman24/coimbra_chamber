"""CRUD manager unit test suite."""

import chamber.manager.crud as crud_mngr

# ----------------------------------------------------------------------------
# build_tables


def test_can_create_experiment_tables():
    message = crud_mngr.create_tables('experiment', 'test')
    print(message)
    assert message == 'Successfully built `experiment` tables in `test`.'


# ----------------------------------------------------------------------------
# add_tube


def test_can_add_tube():
    message = crud_mngr.add_tube('test')
    print(message)
    assert message == 'Sucessfully added default tube to `test`.'


# ----------------------------------------------------------------------------
# add_experiment


def test_can_add_experiment():
    message = crud_mngr.add_experiment('test')
    print(message)
    assert message == 'Successfully added experiment to `test`.'


# ----------------------------------------------------------------------------
# drop_tables


def test_can_drop_experiment_tables():
    message = crud_mngr.drop_tables('experiment', 'test', drop_db=True)
    print(message)
    assert message == (
        'Successfully dropped `experiment` tables from `test`. '
        'Database `test` also dropped.'
        )
