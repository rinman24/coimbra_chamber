"""Unit testing of `film` module."""

import math

import pytest

from chamber import film


P_VALUE = 101325
T_VALUE = 290
TDP_VALUE = 280
TS_VALUE = 285


def test_use_rule():
    e_value = 1
    s_value = 0

    # Test e = 0 and s = 1 with '1/2'
    assert math.isclose(
        film.use_rule(e_value, s_value, '1/2'),
        1/2
    )

    # Test e = 0 and s = 1 with '1/3'
    assert math.isclose(
        film.use_rule(e_value, s_value, '1/3'),
        1/3
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film.use_rule(e_value, s_value, '1/4')
    err_msg = "'1/4' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)

    # Test temp_e = 300 and temp_s = 290 with '1/2'
    temp_e = 300
    temp_s = 290
    assert math.isclose(
        film.use_rule(temp_e, temp_s, '1/2'),
        295
    )

    # Test temp_e = 300 and temp_s = 290 with '1/3'
    assert math.isclose(
        film.use_rule(temp_e, temp_s, '1/3'),
        293.3333333333333
    )


def test__est_c_pm():
    # Test rule = '1/2'
    assert math.isclose(
        film._est_c_pm(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/2'),
        1019.9627505486458
    )

    # Test rule = '1/3'
    assert math.isclose(
        film._est_c_pm(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/3'),
        1020.7363637843752
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        film._est_c_pm(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/5')
    err_msg = "'1/5' is not a valid rule; try '1/2' or '1/3'."
    assert err_msg in str(err.value)
