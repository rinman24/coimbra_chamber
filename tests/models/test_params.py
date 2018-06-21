"""Unit testing of `props` module."""

import math

import pytest

from chamber.models import params

P_VALUE = 101325
T_VALUE = 290
TS_VALUE = 289
TDP_VALUE = 280


def test_get_schmidt():
    assert math.isclose(
            params.get_schmidt(P_VALUE, T_VALUE, TDP_VALUE, 'Mills'),
            0.6104149007992397
            )
    assert math.isclose(
            params.get_schmidt(P_VALUE, T_VALUE, TDP_VALUE, 'Marrero'),
            0.6272163625320014
            )


def test_get_grashof():
    assert math.isclose(
            params.get_grashof(P_VALUE, T_VALUE, TS_VALUE, TDP_VALUE),
            456.280130439354
            )


def test_get_prandtl():
    assert math.isclose(
            params.get_prandtl(P_VALUE, T_VALUE, TDP_VALUE),
            0.7146248666414813
            )
