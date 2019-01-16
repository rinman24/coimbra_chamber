"""CRUD manager unit test suite."""

import chamber.manager.crud.service as crud_mngr

# ----------------------------------------------------------------------------
# build_tables


def test_can_create_experiment_tables():  # noqa: D103
    # Arrange
    correct_message = 'Successfully built `experiment` tables in `test`.'

    # Act
    message = crud_mngr.create_tables('experiment', 'test')
    print(message)

    # Assert
    assert message == correct_message


# ----------------------------------------------------------------------------
# add_tube


def test_can_add_tube():  # noqa: D103
    # Arrange
    correct_message = 'Sucessfully added default tube to `test`.'

    # Act
    message = crud_mngr.add_tube('test')
    print(message)

    # Assert
    assert message == correct_message


# ----------------------------------------------------------------------------
# add_experiment


def test_can_add_experiment():  # noqa: D103
    # Arrange
    correct_message = 'Successfully added experiment to `test`.'

    # Act
    message = crud_mngr.add_experiment('test')
    print(message)

    # Assert
    assert message == correct_message


# ----------------------------------------------------------------------------
# drop_tables


def test_can_drop_experiment_tables():  # noqa: D103
    # Arrange
    correct_message = (
        'Successfully dropped `experiment` tables from `test`. '
        'Database `test` also dropped.'
        )

    # Act
    message = crud_mngr.drop_tables('experiment', 'test', drop_db=True)
    print(message)

    # Assert
    assert message == correct_message
