"""Module level Docstring."""
from math import isclose
import pytest

import chamber.properties as prop

class TestLiquidWaterProperties(object):
    """Unit testing of properties.py."""

    def test_termal_conductivity_range(self):
        """Check that the k_l function throws Value Errors for invalid temperatures."""
        with pytest.raises(ValueError):
            prop.k_l(273)
        with pytest.raises(ValueError):
            prop.k_l(374)

    def test_thermal_conductivity_liquid_water(self):
        """Check that a the thermal conductivity of water can be calculated."""
        assert isclose(prop.k_l(275), 0.556, rel_tol=0.005)
        assert isclose(prop.k_l(280), 0.568, rel_tol=0.005)
        assert isclose(prop.k_l(290), 0.591, rel_tol=0.005)
        assert isclose(prop.k_l(300), 0.611, rel_tol=0.005)
        assert isclose(prop.k_l(320), 0.641, rel_tol=0.005)
        assert isclose(prop.k_l(340), 0.661, rel_tol=0.005)
        assert isclose(prop.k_l(360), 0.676, rel_tol=0.005)
        assert isclose(prop.k_l(370), 0.680, rel_tol=0.005)

    def test_specific_heat_range(self):
        """Check that the c_l function throws Value Errors for invalid temperatures."""
        with pytest.raises(ValueError):
            prop.c_l(273)
        with pytest.raises(ValueError):
            prop.c_l(374)

    def test_specific_heat_liquid_water(self):
        """Check that a the specific heat of water can be calculated."""
        assert isclose(prop.c_l(275), 4217, rel_tol=0.0005)
        assert isclose(prop.c_l(280), 4203, rel_tol=0.0005)
        assert isclose(prop.c_l(290), 4186, rel_tol=0.0005)
        assert isclose(prop.c_l(300), 4178, rel_tol=0.0005)
        assert isclose(prop.c_l(320), 4174, rel_tol=0.0005)
        assert isclose(prop.c_l(340), 4184, rel_tol=0.0005)
        assert isclose(prop.c_l(360), 4200, rel_tol=0.0005)
        assert isclose(prop.c_l(370), 4209, rel_tol=0.0005)

    def test_density_range(self):
        """Check that the rho_l function throws Value Errors for invalid temperatures."""
        with pytest.raises(ValueError):
            prop.rho_l(273)
        with pytest.raises(ValueError):
            prop.rho_l(374)

    def test_density_liquid_water(self):
        """Check that a the density of water can be calculated."""
        assert isclose(prop.rho_l(275), 1000, rel_tol=0.0005)
        assert isclose(prop.rho_l(280), 1000, rel_tol=0.0005)
        assert isclose(prop.rho_l(290), 999, rel_tol=0.0005)
        assert isclose(prop.rho_l(300), 996, rel_tol=0.0005)
        assert isclose(prop.rho_l(320), 989, rel_tol=0.0005)
        assert isclose(prop.rho_l(340), 980, rel_tol=0.0005)
        assert isclose(prop.rho_l(360), 967, rel_tol=0.0005)
        assert isclose(prop.rho_l(370), 960, rel_tol=0.0005)
