"""Docstring."""
from math import isclose

import pytest

import chamber.const as const
import chamber.water as water


class TestWater(object):
    """Unit testing of water.py."""

    def test_p_sat_liq(self):
        """Test calculation of the saturation vapor pressure."""
        assert isclose(water.p_sat_liq(273.15), 610, rel_tol=0.005)
        assert isclose(water.p_sat_liq(288.00), 1688, rel_tol=0.005)
        assert isclose(water.p_sat_liq(303.00), 4206, rel_tol=0.005)

    def test_enh_fact_liq(self):
        """Test correct calculation of the enhancement factor."""
        assert isclose(water.enh_fact_liq(
            273.15, 101325.00, water.p_sat_liq(286.55)), 1, rel_tol=0.01)
        assert isclose(water.enh_fact_liq(
            288.00, 101325.00, water.p_sat_liq(286.55)), 1, rel_tol=0.01)
        assert isclose(water.enh_fact_liq(
            303.00, 101325.00, water.p_sat_liq(286.55)), 1, rel_tol=0.01)
        assert isclose(water.enh_fact_liq(
            296.15, 101325.00, water.p_sat_liq(286.55)), 1, rel_tol=0.01)
        assert isclose(water.enh_fact_liq(
            290.05, 101325.00, water.p_sat_liq(286.55)), 1, rel_tol=0.01)

    def test_eff_p_sat_liq(self):
        """Test calculation of the effective saturation vapor pressure."""
        assert isclose(water.eff_p_sat_liq(273.15, 101325.00),
                       610, rel_tol=0.0112)
        assert isclose(water.eff_p_sat_liq(288.00, 101325.00),
                       1688, rel_tol=0.0112)
        assert isclose(water.eff_p_sat_liq(303.00, 101325.00),
                       4206, rel_tol=0.0112)

    def test_rel_humidity(self):
        """Test calculation of the effective saturation vapor pressure."""
        assert isclose(water.rel_humidity(296.15, 290.05, 101325.00, False),
                       0.686, rel_tol=0.01)
        assert isclose(water.rel_humidity(296.15, 290.05, 101325.00),
                       0.686, rel_tol=0.0112)
        assert isclose(water.rel_humidity(296.15, 290.05, 101325.00, True),
                       0.686, rel_tol=0.0112)
