"""Spalding engine unit test suite."""

import math

import pytest
import uncertainties as un

import chamber.engine.spalding.service as dbs
import chamber.tests.engine.spalding.constants as const


@pytest.fixture
def spald():
    """Obtain a fresh `spald` fixture for each test."""
    return dbs.Spalding(**const.spald_input)


def test_spalding_constructor(spald):  # noqa: D103
    # Test internal attributes
    assert _compare_ufloats(spald._t_s_guess, const.t_s_guess)
    assert _compare_ufloats(spald._s_state['m_1s_g'], const.m_1s_g)
#    assert spald._s_state is None
    assert spald._u_state is None
    assert spald._liq_props is None
    assert spald._t_state is None
    assert spald._film_props is None
    assert spald._e_state is None

    # Test the _guide constructor
    assert spald._film_guide['ref'] == 'Mills'
    assert spald._film_guide['rule'] == '1/2'

    # Test the _exp_state constructor
    assert _compare_ufloats(spald._exp_state['L'], const.exp_state['L'])
    assert _compare_ufloats(spald._exp_state['P'], const.exp_state['P'])
    assert _compare_ufloats(spald._exp_state['T_e'], const.exp_state['T_e'])
    assert _compare_ufloats(spald._exp_state['T_dp'], const.exp_state['T_dp'])


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
