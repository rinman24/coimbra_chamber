"""Spalding engine unit test suite."""

import math

import pytest
import uncertainties as un

import chamber.engine.spalding.service as dbs
import chamber.tests.engine.spalding.constants as const


# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture(scope='function')
def spald():
    """Instance of a Spalding model object."""
    return dbs.Spalding(**const.spald_input)


# ----------------------------------------------------------------------------
# Tests


def test_spalding_constructor(spald):  # noqa: D103
    # Test the _film_guide in constructor
    assert spald._film_guide['ref'] == const.ref
    assert spald._film_guide['rule'] == const.rule

    # Test the _exp_state in constructor
    assert _compare_ufloats(spald.exp_state['L'], const.exp_state['L'])
    assert _compare_ufloats(spald.exp_state['P'], const.exp_state['P'])
    assert _compare_ufloats(spald.exp_state['T'], const.exp_state['T'])
    assert _compare_ufloats(spald.exp_state['T_dp'], const.exp_state['T_dp'])

    # Test states and props
    assert math.isclose(spald.s_state['h'], const.initial_s_state['h'])
    assert math.isclose(spald.s_state['h_fg'], const.initial_s_state['h_fg'])
    assert math.isclose(spald.s_state['m_1'], const.initial_s_state['m_1'])
    assert math.isclose(spald.s_state['T'], const.initial_s_state['T'])

    assert math.isclose(spald.u_state['h'], const.initial_u_state['h'])
    assert math.isclose(spald.u_state['T'], const.initial_u_state['T'])

    assert math.isclose(spald.liq_props['c_p'], const.initial_liq_props['c_p'])
    assert math.isclose(spald.liq_props['T'], const.initial_liq_props['T'])

    assert math.isclose(spald.t_state['h'], const.initial_t_state['h'])
    assert math.isclose(spald.t_state['T'], const.initial_t_state['T'])

    assert math.isclose(
        spald.film_props['T'], const.initial_film_props['T'])
    assert math.isclose(
        spald.film_props['m_1'], const.initial_film_props['m_1'])
    assert math.isclose(
        spald.film_props['c_p'], const.initial_film_props['c_p'])
    assert math.isclose(
        spald.film_props['rho'], const.initial_film_props['rho'])
    assert math.isclose(
        spald.film_props['k'], const.initial_film_props['k'])
    assert math.isclose(
        spald.film_props['alpha'], const.initial_film_props['alpha'])
    assert math.isclose(
        spald.film_props['D_12'], const.initial_film_props['D_12'])
    assert math.isclose(
        spald.film_props['nu'], const.initial_film_props['nu'])

    assert math.isclose(spald.e_state['m_1'], const.initial_e_state['m_1'])
    assert math.isclose(spald.e_state['T'], const.initial_e_state['T'])
    assert math.isclose(spald.e_state['h'], const.initial_e_state['h'])
    assert math.isclose(spald.e_state['c_p'], const.initial_e_state['c_p'])


def test_update_model(spald):  # noqa: D103
    spald._film_guide['ref'] = 'Marrero'
    spald._film_guide['rule'] = '1/3'
    spald._update_model(t_guess=288.5)

    # Test states and props
    assert math.isclose(spald.s_state['h'], const.updated_s_state['h'])
    assert math.isclose(spald.s_state['h_fg'], const.updated_s_state['h_fg'])
    assert math.isclose(spald.s_state['m_1'], const.updated_s_state['m_1'])
    assert math.isclose(spald.s_state['T'], const.updated_s_state['T'])

    assert math.isclose(spald.u_state['h'], const.updated_u_state['h'])
    assert math.isclose(spald.u_state['T'], const.updated_u_state['T'])

    assert math.isclose(spald.liq_props['c_p'], const.updated_liq_props['c_p'])
    assert math.isclose(spald.liq_props['T'], const.updated_liq_props['T'])

    assert math.isclose(spald.t_state['h'], const.updated_t_state['h'])
    assert math.isclose(spald.t_state['T'], const.updated_t_state['T'])

    assert math.isclose(
        spald.film_props['T'], const.updated_film_props['T'])
    assert math.isclose(
        spald.film_props['m_1'], const.updated_film_props['m_1'])
    assert math.isclose(
        spald.film_props['c_p'], const.updated_film_props['c_p'])
    assert math.isclose(
        spald.film_props['rho'], const.updated_film_props['rho'])
    assert math.isclose(
        spald.film_props['k'], const.updated_film_props['k'])
    assert math.isclose(
        spald.film_props['alpha'], const.updated_film_props['alpha'])
    assert math.isclose(
        spald.film_props['D_12'], const.updated_film_props['D_12'])
    assert math.isclose(
        spald.film_props['nu'], const.updated_film_props['nu'])

    assert math.isclose(spald.e_state['m_1'], const.updated_e_state['m_1'])
    assert math.isclose(spald.e_state['T'], const.updated_e_state['T'])
    assert math.isclose(spald.e_state['h'], const.updated_e_state['h'])
    assert math.isclose(spald.e_state['c_p'], const.updated_e_state['c_p'])


def test_spalding_constructor_checks_ref_and_rule():  # noqa: D103
    spald_input = dict(const.spald_input)
    spald_input['rule'] = '1/4'
    with pytest.raises(ValueError) as err:
        dbs.Spalding(**spald_input)
    err_msg = "'1/4' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)

    spald_input = dict(const.spald_input)
    spald_input['ref'] = 'Inman'
    with pytest.raises(ValueError) as err:
        dbs.Spalding(**spald_input)
    err_msg = ("'Inman' is not a valid ref; try 'Mills' or 'Marrero'.")
    assert err_msg in str(err.value)


@pytest.mark.parametrize('name', const.properties)
def test_properties(spald, name):  # noqa: D103
    with pytest.raises(AttributeError):
        setattr(spald, name, 'foo')


@pytest.mark.parametrize('rule,expected', [
    ('1/2', 1/2),
    ('1/3', 1/3),
    ])
def test_use_rule(spald, rule, expected):  # noqa: D103
    e_value = 1
    s_value = 0
    spald._film_guide['rule'] = rule

    assert math.isclose(
        spald._use_rule(e_value, s_value), expected)


def test_solve_model(spald):  # noqa: D103
    spald.solve()

    assert _compare_ufloats(spald.solution['mddp'], const.solution['mddp'])
    assert _compare_ufloats(spald.solution['T_s'], const.solution['T_s'])
    assert _compare_ufloats(spald.solution['q_cu'], const.solution['q_cu'])
    assert _compare_ufloats(spald.solution['q_rs'], const.solution['q_rs'])
    assert _compare_ufloats(spald.solution['m_1s'], const.solution['m_1s'])
    assert _compare_ufloats(spald.solution['m_1e'], const.solution['m_1e'])
    assert _compare_ufloats(spald.solution['B_m1'], const.solution['B_m1'])
    assert _compare_ufloats(spald.solution['B_h'], const.solution['B_h'])
    assert _compare_ufloats(spald.solution['g_m1'], const.solution['g_m1'])
    assert _compare_ufloats(spald.solution['g_h'], const.solution['g_h'])


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
