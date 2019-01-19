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
    # Test the _film_guide in constructor
    assert spald._film_guide['ref'] == const.ref
    assert spald._film_guide['rule'] == const.rule

    # Test the _exp_state in constructor
    assert _compare_ufloats(spald._exp_state['L'], const.exp_state['L'])
    assert _compare_ufloats(spald._exp_state['P'], const.exp_state['P'])
    assert _compare_ufloats(spald._exp_state['T_e'], const.exp_state['T_e'])
    assert _compare_ufloats(spald._exp_state['T_dp'], const.exp_state['T_dp'])

    # Test states
    assert math.isclose(spald._s_state['h'], const.initial_s_state['h'])
    assert math.isclose(spald._s_state['h_fg'], const.initial_s_state['h_fg'])
    assert math.isclose(spald._s_state['m_1'], const.initial_s_state['m_1'])
    assert math.isclose(spald._s_state['T'], const.initial_s_state['T'])


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
