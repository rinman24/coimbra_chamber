import pytest

from chamber.models import models

P_VALUE = 101325
TE_VALUE = 290
TDP_VALUE = 280
TS_VALUE = 285

EXP_STATE = dict(
    p=P_VALUE, t_e=TE_VALUE, t_dp=TDP_VALUE, ref='Mills', rule='1/2'
    )

MOD = models.Spalding(**EXP_STATE)


def test_Spalding__init__():
    assert MOD._t_s_guess is None

    # Test the _guide constructor
    assert MOD._film_guide.ref == 'Mills'
    assert MOD._film_guide.rule == '1/2'

    # Test the _exp_state constructor
    assert MOD._exp_state.p == P_VALUE
    assert MOD._exp_state.t_e == TE_VALUE
    assert MOD._exp_state.t_dp == TDP_VALUE


def test_Spalding_t_s_guess_getter():
    assert MOD.t_s_guess is None

    # Test raises ValueError
    with pytest.raises(AttributeError) as err:
        MOD.t_s_guess = 300
    assert "can't set attribute" in str(err.value)
