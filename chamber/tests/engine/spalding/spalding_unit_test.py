"""Spalding engine unit test suite."""

import math

import pytest
import uncertainties as un

import chamber.engine.spalding.service as dbs
import chamber.tests.engine.spalding.constants as const


@pytest.fixture(scope='function')
def spald():
    """Instance of a Spalding model object."""
    return dbs.Spalding(**const.spald_input)


def test_spalding_constructor(spald):  # noqa: D103
    pass


@pytest.mark.skip
@pytest.mark.parametrize('name', const.properties)
def test_properties(spald, name):  # noqa: D103
    with pytest.raises(AttributeError):
        setattr(spald, name, 'foo')


# ----------------------------------------------------------------------------
# Helpers


def _compare_ufloats(u1, u2):
    value_1 = u1.nominal_value
    value_2 = u2.nominal_value
    std_1 = u1.std_dev
    std_2 = u2.std_dev

    try:
        assert math.isclose(value_1, value_2)
        assert math.isclose(std_1, std_2)
    except AssertionError:
        return False
    else:
        return True
