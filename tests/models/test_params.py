"""Unit testing of `props` module."""

import math

import pytest

from chamber.models import params

P_VALUE = 101325
T_VALUE = 290
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
