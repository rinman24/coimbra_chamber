"""Unit testing of `film` module."""

import math

import pytest

from chamber import film


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
