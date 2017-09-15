"""Module level Docstring."""
from math import isclose

import chamber.properties as prop

MODEL_VARS = dict(temp_dp=288, temp_e=295, temp_s=293, pressure=101325, ref='Mills', rule='mean',
	              length=0.03, d_12=0, hfg=0, k_m=0, m_1e=0, m_1s=0, rho_m=0)

class TestLiquidWaterProperties(object):
    """Unit testing of properties.py."""

    def test_get_ref_state(self):
        """Test the ability to evaluate film values based on various rules."""
        assert prop.get_ref_state(0, 2, 'mean') == 1
        assert prop.get_ref_state(0, 3, 'one-third') == 2

    def test_bin_diff_coeff(self):
        """Test the calculation of the binary diffusion coefficient."""
        ref_temp, pressure = 300, 101325
        assert isclose(prop.get_bin_diff_coeff(ref_temp, pressure, 'Mills'),
                       1.97e-5*(101325/pressure)*pow(ref_temp/256, 1.685))
        assert isclose(prop.get_bin_diff_coeff(ref_temp, pressure, 'Marrero'),
                       1.87e-10*pow(ref_temp, 2.072)/(pressure/101325))

    def test_get_tp_props(self):
        """Test the calculation of all of the thermophysical properties."""
        props = prop.get_tp_props(MODEL_VARS)
        assert isclose(props['d_12'], 2.487408627636508e-05)
        assert isclose(props['h_fg'], 2453874.327285723)
        assert isclose(props['k_m'], 0.02592285857763665)
        assert isclose(props['m_1e'], 0.010478738655174959)
        assert isclose(props['m_1s'], 0.01441074635353759)
        assert isclose(props['rho_m'], 1.1921643674975833)
