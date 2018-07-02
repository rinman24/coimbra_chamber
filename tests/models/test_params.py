"""Unit testing of `props` module."""

import math

import pytest

from chamber.models import params

LENGTH = 0.044
M_DOT_PP = 2.5e-6
P_VALUE = 101325
T_VALUE = 290
TDP_VALUE = 280
TS_VALUE = 289


def test_get_schmidt():
    assert math.isclose(
            params.get_schmidt(P_VALUE, T_VALUE, TDP_VALUE, 'Mills'),
            0.6104149007992397
            )
    assert math.isclose(
            params.get_schmidt(P_VALUE, T_VALUE, TDP_VALUE, 'Marrero'),
            0.6272163625320014
            )
    assert math.isclose(
            params.get_schmidt(P_VALUE, T_VALUE, TDP_VALUE, 'constant'),
            0.614
            )


def test_get_grashof():
    assert math.isclose(
            params.get_grashof(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE),
            0
            )
    assert math.isclose(
            params.get_grashof(P_VALUE, T_VALUE, TDP_VALUE, T_VALUE-1),
            0
            )
    assert math.isclose(
            params.get_grashof(P_VALUE, T_VALUE, TDP_VALUE, T_VALUE-0.5),
            230.11072973650792
            )
    assert math.isclose(
            params.get_grashof(P_VALUE, T_VALUE, TDP_VALUE, T_VALUE),
            523.3337477478808
            )
    assert math.isclose(
            params.get_grashof(P_VALUE, T_VALUE, TDP_VALUE, T_VALUE+0.5),
            817.5332327958012
            )
    assert math.isclose(
            params.get_grashof(P_VALUE, T_VALUE, TDP_VALUE, T_VALUE+1),
            1112.7334920658418
            )


def test_get_prandtl():
    assert math.isclose(
            params.get_prandtl(P_VALUE, T_VALUE, TDP_VALUE),
            0.7146248666414813
            )


def test_get_sherwood():
    assert math.isclose(
            params.get_sherwood(LENGTH, M_DOT_PP, P_VALUE, T_VALUE,
                                TDP_VALUE, TS_VALUE, 'Mills'),
            0.7332711832477895
            )

    assert math.isclose(
            params.get_sherwood(LENGTH, M_DOT_PP, P_VALUE, T_VALUE,
                                TDP_VALUE, TS_VALUE, 'Marrero'),
            0.7534542222085742
            )

    assert math.isclose(
            params.get_sherwood(LENGTH, M_DOT_PP, P_VALUE, T_VALUE,
                                TDP_VALUE, TS_VALUE, 'constant'),
            0.7375778440608858
            )
