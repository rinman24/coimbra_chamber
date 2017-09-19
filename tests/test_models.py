"""Module level Docstring."""
from math import isclose

#import pytest

import chamber.models as models

import tests.test_const as test_const

#@pytest.fixture(scope='module')
#def model_object():
#    """Model object to be manipulated durring testing."""
#    yield models.Model(test_const.SETTINGS)
    

MODEL = models.Model(test_const.SETTINGS)

class TestModels(object):
    """Unit testing of properties.py."""

    def test_init(self):
        MODEL = models.Model(test_const.SETTINGS)
        assert MODEL
        assert isclose(MODEL.length, 0.03)
        assert isclose(MODEL.pressure, 99950)
        assert MODEL.ref == 'Mills'
        assert MODEL.rule == 'mean'
        assert isclose(MODEL.temp_dp, 288)
        assert isclose(MODEL.temp_e, 295)

        assert isclose(MODEL.d_12, 2.57241624267905e-05)
        assert isclose(MODEL.h_fg, 2437289.2412412656)
        assert isclose(MODEL.k_m, 0.02617089010608943)
        assert isclose(MODEL.m_1e, 0.010623365736965384)
        assert isclose(MODEL.m_1s, 0.022403324704408374)
        assert isclose(MODEL.rho_m, 1.1593017242070287)

    def test_get_ref_state(self):
        """Test the ability to evaluate film values based on various rules."""
        assert MODEL.get_ref_state(0, 2, 'mean') == 1
        assert MODEL.get_ref_state(0, 3, 'one-third') == 2

    def test_bin_diff_coeff(self):
        """Test the calculation of the binary diffusion coefficient."""
        ref_temp, pressure = 300, 101325
        assert isclose(MODEL.get_bin_diff_coeff(ref_temp, pressure, 'Mills'),
                       1.97e-5*(101325/pressure)*pow(ref_temp/256, 1.685))
        assert isclose(MODEL.get_bin_diff_coeff(ref_temp, pressure, 'Marrero'),
                       1.87e-10*pow(ref_temp, 2.072)/(pressure/101325))

    def test_eval_props(self):
        """Test the calculation of all of the thermophysical properties."""
        MODEL.eval_props()
        assert isclose(MODEL.d_12, 2.57241624267905e-05)
        assert isclose(MODEL.h_fg, 2437289.2412412656)
        assert isclose(MODEL.k_m, 0.02617089010608943)
        assert isclose(MODEL.m_1e, 0.010623365736965384)
        assert isclose(MODEL.m_1s, 0.022403324704408374)
        assert isclose(MODEL.rho_m, 1.1593017242070287)

    def test_repr(self):
        """print(repr(<MODEL>))"""
        assert MODEL.__repr__() == test_const.REPR

    def test_str(self):
        """print(str(<MODEL>))"""
        assert MODEL.__str__() == test_const.STR
