"""Docstring required."""

import math

import pytest

from chamber.models import models

P_VALUE = 101325
TE_VALUE = 290
TDP_VALUE = 280
TS_VALUE = 285

EXP_STATE = dict(
    p=P_VALUE, t_e=TE_VALUE, t_dp=TDP_VALUE, ref='Mills', rule='1/2'
    )


@pytest.fixture
def spald():
    """Obtain a fresh `spald` fixture for each test."""
    return models.Spalding(**EXP_STATE)


# __init__
def test_Spalding__init__(spald):
    """Test __init___."""
    # Test the _guide constructor
    assert spald._film_guide['ref'] == 'Mills'
    assert spald._film_guide['rule'] == '1/2'

    # Test the _exp_state constructor
    assert spald._exp_state['p'] == P_VALUE
    assert spald._exp_state['t_e'] == TE_VALUE
    assert spald._exp_state['t_dp'] == TDP_VALUE

    assert spald._t_s_guess is None
    assert spald._s_state is None
    assert spald._u_state is None
    assert spald._liq_props is None
    assert spald._t_state is None
    assert spald._film_props is None
    assert spald._e_state is None
    # assert spald._e_state is None
    # assert spald.q_cu == 0
    # assert spald.q_rs == 0


# film_guide property
def test_Spalding_film_guide(spald):
    """Test _film_guide."""
    assert isinstance(spald.film_guide, dict)
    assert len(spald.film_guide) == 2
    assert spald.film_guide['ref'] == 'Mills'
    assert spald.film_guide['rule'] == '1/2'

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.film_guide = 'hitchhiker'
    assert "can't set attribute" in str(err.value)


# exp_state property
def test_Spalding_exp_state(spald):
    """Test _exp_state."""
    assert isinstance(spald.exp_state, dict)
    assert len(spald.exp_state) == 3
    assert spald.exp_state['p'] == 101325
    assert spald.exp_state['t_e'] == 290
    assert spald.exp_state['t_dp'] == 280

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.exp_state = 300
    assert "can't set attribute" in str(err.value)


# t_s_guess property
def test_Spalding_t_s_guess(spald):
    """Test t_s_guess."""
    assert spald.t_s_guess is None

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.t_s_guess = 300
    assert "can't set attribute" in str(err.value)


# s-state
def test_Spalding_s_state(spald):
    """Test s_state."""
    assert spald.s_state is None

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.s_state = 'foo'
    assert "can't set attribute" in str(err.value)


def test_Spalding_set_s_state(spald):
    """Test set_s_state."""
    with pytest.raises(ValueError) as err:
        spald._set_s_state()
    err_msg = "Cannot set `s_state` when `self.t_s_guess` is None."
    assert err_msg in str(err.value)

    # This should only be done internally, but is done here for testing.
    spald._t_s_guess = 285
    assert spald.s_state is None
    spald._set_s_state()
    assert math.isclose(spald.s_state['m_1s_g'], 0.008605868703401028)
    assert math.isclose(spald.s_state['h_fgs_g'], 2472806.6902607535)
    assert math.isclose(spald.s_state['h_s_g'], 0)


# u-state
def test_Spalding_u_state(spald):
    """Test u_state."""
    assert spald.u_state is None

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.u_state = 'foo'
    assert "can't set attribute" in str(err.value)


def test_Spalding_set_u_state(spald):
    """Test set_u_state."""
    with pytest.raises(ValueError) as err:
        spald._set_u_state()
    err_msg = "Cannot set `u-state` when `self.s_state` is None."
    assert err_msg in str(err.value)

    spald._t_s_guess = 285
    spald._set_s_state()
    assert spald.u_state is None
    spald._set_u_state()
    assert math.isclose(spald.u_state['h_u_g'], -spald.s_state['h_fgs_g'])


# liq-props
def test_Spalding_liq_props(spald):
    """Test liq_props."""
    assert spald.liq_props is None

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.liq_props = 'Joe Montana'
    assert "can't set attribute" in str(err.value)


def test_Spalding_set_liq_props(spald):
    """Test set_liq_props."""
    with pytest.raises(ValueError) as err:
        spald._set_liq_props()
    err_msg = ("Cannot set `liq-props` when `self.s_state` or"
               " `self.u_state` is None.")
    assert err_msg in str(err.value)

    spald._t_s_guess = 285
    spald._set_s_state()
    spald._set_u_state()
    assert spald.liq_props is None
    spald._set_liq_props()
    assert math.isclose(spald.liq_props['c_pl_g'], 4189.82872258844)


# t-state
def test_Spalding_t_state(spald):
    """Test t_state."""
    assert spald.t_state is None

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.t_state = 'transferred'
    assert "can't set attribute" in str(err.value)


def test_Spalding_set_t_state(spald):
    """Test set_t_state."""
    with pytest.raises(ValueError) as err:
        spald._set_t_state()
    err_msg = "Cannot set `t-state` when `self.liq_props` is None."
    assert err_msg in str(err.value)

    spald._t_s_guess = 285
    spald._set_s_state()
    spald._set_u_state()
    spald._set_liq_props()
    assert spald.t_state is None
    spald._set_t_state()
    assert math.isclose(spald.t_state['h_t_g'], -2451857.5466478113)


# film-props
def test_Spalding_film_props(spald):
    """Test film_props."""
    assert spald.film_props is None

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.film_props = 'Motion-pictures'
    assert "can't set attribute" in str(err.value)


def test_Spalding_set_film_props(spald):
    """Test set_film_props."""
    with pytest.raises(ValueError) as err:
        spald._set_film_props()
    err_msg = ("Cannot set `film-props` when `self.s_state` is None.")
    assert err_msg in str(err.value)

    spald._t_s_guess = 285
    spald._set_s_state()
    assert spald.film_props is None
    spald._set_film_props()
    assert math.isclose(spald.film_props['c_pm_g'], 1019.9627505486458)
    assert math.isclose(spald.film_props['rho_m_g'], 1.2229936606324967)
    assert math.isclose(spald.film_props['k_m_g'], 0.025446947707731902)
    assert math.isclose(spald.film_props['alpha_m_g'], 2.040317009201964e-05)
    assert math.isclose(spald.film_props['d_12_g'], 2.3955520502741308e-05)


# e-state
def test_Spalding_e_state(spald):
    """Test e_state."""
    assert spald.e_state is None

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        spald.e_state = 'global warming'
    assert "can't set attribute" in str(err.value)


def test_Spalding_set_e_state(spald):
    """Test set_e_state."""
    with pytest.raises(ValueError) as err:
        spald._set_e_state()
    err_msg = "Cannot set `e-state` when `self.film_props` is None."
    assert err_msg in str(err.value)

    # This should only be done internally, but is done here for testing.
    spald._t_s_guess = 285
    spald._set_s_state()
    spald._set_film_props()
    assert spald.e_state is None
    spald._set_e_state()
    assert math.isclose(spald.e_state['m_1e'], 0.0061357476021502095)
    assert math.isclose(spald.e_state['h_e_g'], 5099.813752743229)

# ----------------------------------------------------------------------------
# Solver helper functions


def test_Spalding_update_model(spald):
    """Test update_model."""
    # Update the model
    new_t_s_guess = 287.5
    spald._update_model(new_t_s_guess)

    # Check that everything was updated
    assert spald.t_s_guess == new_t_s_guess

    assert math.isclose(spald.s_state['m_1s_g'], 0.010143540369588422)
    assert math.isclose(spald.s_state['h_fgs_g'], 2466889.85481398)
    assert math.isclose(spald.s_state['h_s_g'], 0)

    assert math.isclose(spald.u_state['h_u_g'], -spald.s_state['h_fgs_g'])

    assert math.isclose(spald.liq_props['c_pl_g'], 4188.229862295786)

    assert math.isclose(spald.t_state['h_t_g'], -2456419.2801582403)

    assert math.isclose(spald.film_props['c_pm_g'], 1021.4841291290464)
    assert math.isclose(spald.film_props['rho_m_g'], 1.2170548183931842)
    assert math.isclose(spald.film_props['k_m_g'], 0.025539619700973824)
    assert math.isclose(spald.film_props['alpha_m_g'], 2.0544673661172288e-05)
    assert math.isclose(spald.film_props['d_12_g'], 2.413048992963711e-05)

    assert math.isclose(spald.e_state['m_1e'], 0.0061357476021502095)
    assert math.isclose(spald.e_state['h_e_g'], 2553.710322822616)
