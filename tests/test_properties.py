"""Module level Docstring."""
from math import isclose
import pytest

import chamber.properties as prop

class TestProperties(object):
    """Unit testing of properties.py."""

    def test_termal_conductivity_range(self):
        """Check that the k_l function throws Value Errors for invalid temperatures."""
        with pytest.raises(ValueError):
            prop.k_l(273)
        with pytest.raises(ValueError):
            prop.k_l(374)

    def test_thermal_conductivity_liquid_water(self):
        """Check that a the thermal conductivity of water can be calculated."""
        assert isclose(prop.k_l(300), 0.611, rel_tol=0.005)
        assert isclose(prop.k_l(320), 0.641, rel_tol=0.005)
        assert isclose(prop.k_l(340), 0.661, rel_tol=0.005)
        assert isclose(prop.k_l(360), 0.676, rel_tol=0.005)
        assert isclose(prop.k_l(370), 0.680, rel_tol=0.005)

    def test_specific_heat_liquid_water(self):
        """Check that a the thermal conductivity of water can be calculated."""
        assert isclose(prop.c_l(300), 4178, rel_tol=0.0005)
        assert isclose(prop.c_l(320), 4174, rel_tol=0.0005)
        assert isclose(prop.c_l(340), 4184, rel_tol=0.0005)
        assert isclose(prop.c_l(360), 4200, rel_tol=0.0005)
        assert isclose(prop.c_l(370), 4209, rel_tol=0.0005)
