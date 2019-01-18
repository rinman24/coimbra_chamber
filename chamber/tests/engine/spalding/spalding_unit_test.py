"""Spalding engine unit test suite."""

import pytest

import chamber.engine.spalding.service as dbs


# @pytest.fixture
# def spald():
#     """Obtain a fresh `spald` fixture for each test."""
#     return dbs.Spalding(**EXP_STATE)


# def test_spalding_constructor(spald):
#     """Test __init___."""
#     # Test the _guide constructor
#     assert spald._film_guide['ref'] == 'Mills'
#     assert spald._film_guide['rule'] == '1/2'

#     # Test the _exp_state constructor
#     assert spald._exp_state['p'] == P_VALUE
#     assert spald._exp_state['t_e'] == TE_VALUE
#     assert spald._exp_state['t_dp'] == TDP_VALUE

#     assert spald._t_s_guess is None
#     assert spald._s_state is None
#     assert spald._u_state is None
#     assert spald._liq_props is None
#     assert spald._t_state is None
#     assert spald._film_props is None
#     assert spald._e_state is None
    # assert spald._e_state is None
    # assert spald.q_cu is None
    # assert spald.q_rs is None