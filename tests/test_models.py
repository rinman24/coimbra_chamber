"""Unit testing of models.py."""
from math import isclose

import chamber.models as models

import tests.test_const as test_const

MODEL = models.Model(test_const.SETTINGS)
ONEDIM_ISOLIQ_NORAD = models.OneDimIsoLiqNoRad(test_const.SETTINGS)
ONEDIM_ISOLIQ_BLACKRAD = models.OneDimIsoLiqBlackRad(test_const.SETTINGS)


class Test_Models(object):
    """Unit testing of Models class."""

    def test_init(self):
        assert MODEL
        assert isclose(MODEL.length, 0.03)
        assert isclose(MODEL.pressure, 99950)
        assert MODEL.ref == 'Mills'
        assert MODEL.rule == 'mean'
        assert isclose(MODEL.temp_dp, 288)
        assert isclose(MODEL.temp_e, 295)
        assert isclose(MODEL.temp_s, 291.5)

        assert isclose(MODEL.mu_m, 1.8106909203849476e-05)
        assert isclose(MODEL.cp_m, 1016.6738656679439)
        assert isclose(MODEL.d_12, 2.510797939645015e-05)
        assert isclose(MODEL.h_fg, 2457424.545412025)
        assert isclose(MODEL.k_m, 0.025867252254694034)
        assert isclose(MODEL.m_1e, 0.010623365736965384)
        assert isclose(MODEL.m_1s, 0.013294255082507034)
        assert isclose(MODEL.rho_m, 1.1793376852254565)
        assert isclose(MODEL.nu_m, 1.5353455953023276e-05)
        assert isclose(MODEL.alpha_m, 2.157398944861877e-05)
        assert isclose(MODEL.beta_m, 0.0034100596760443308)
        assert isclose(MODEL.beta_star_m, 0.6033861519510446)
        assert MODEL.solution is None

        assert isclose(MODEL.Ra_number, -8252.400804563847)

    def test_repr(self):
        """print(repr(<MODEL>))"""
        assert MODEL.__repr__() == test_const.REPR

    def test_str(self):
        """print(str(<MODEL>))"""
        print(MODEL.__str__())
        assert MODEL.__str__() == test_const.STR

    def test_get_ref_state(self):
        """Test the ability to evaluate film values based on various rules."""
        assert MODEL.get_ref_state(0, 2, 'mean') == 1
        assert MODEL.get_ref_state(0, 3, 'one-third') == 2

    def test_bin_diff_coeff(self):
        """Test the calculation of the binary diffusion coefficient."""
        ref_temp, pressure = 300, 101325
        assert isclose(MODEL.get_bin_diff_coeff(ref_temp, pressure, 'Mills'),
                       1.97e-5 * (101325 / pressure) *
                       pow(ref_temp / 256, 1.685))
        assert isclose(MODEL.get_bin_diff_coeff(ref_temp, pressure, 'Marrero'),
                       1.87e-10 * pow(ref_temp, 2.072) / (pressure / 101325))

    def test_eval_props(self):
        """Test the calculation of all of the thermophysical properties."""
        MODEL.temp_s = 293
        MODEL.eval_props()
        assert isclose(MODEL.mu_m, 1.813689690669493e-05)
        assert isclose(MODEL.cp_m, 1017.2873735694611)
        assert isclose(MODEL.d_12, 2.521627605755569e-05)
        assert isclose(MODEL.h_fg, 2453874.327285723)
        assert isclose(MODEL.k_m, 0.02592145926625826)
        assert isclose(MODEL.m_1e, 0.010623365736965384)
        assert isclose(MODEL.m_1s, 0.014610145619944618)
        assert isclose(MODEL.rho_m, 1.1758589997836344)

        assert isclose(MODEL.nu_m, 1.5424380737853974e-05)
        assert isclose(MODEL.alpha_m, 2.167008152326072e-05)
        assert isclose(MODEL.beta_m, 0.003401360544217687)
        assert isclose(MODEL.beta_star_m, 0.603147186094405)
        assert isclose(MODEL.Ra_number, -3484.0297271546015)
        MODEL.temp_s = 291.5


class Test_OneDimIsoLiqNoRad(object):
    """Unit testing of OneDimIsoLiqNoRad class."""

    def test_eval_model(self):
        res = ONEDIM_ISOLIQ_NORAD.eval_model([1, 1, 1])
        assert isclose(res[0], 254.49907209600156)
        assert isclose(res[1], 0.9999973637622117)
        assert isclose(res[2], 2457425.545412025)

    def test_set_solution(self):
        ONEDIM_ISOLIQ_NORAD.set_solution([1, 2, 3])
        assert ONEDIM_ISOLIQ_NORAD.solution['mddp'] == 1
        assert ONEDIM_ISOLIQ_NORAD.solution['q_m'] == 2
        assert ONEDIM_ISOLIQ_NORAD.solution['temp_s'] == 3

    def test_solve_iteratively(self):
        count = ONEDIM_ISOLIQ_NORAD.solve_iteratively()
        assert count == 126
        assert isclose(
            ONEDIM_ISOLIQ_NORAD.solution['mddp'], 1.6526395638614737e-06)
        assert isclose(
            ONEDIM_ISOLIQ_NORAD.solution['q_m'], -4.0660229435638495)
        assert isclose(
            ONEDIM_ISOLIQ_NORAD.solution['temp_s'], 290.27625254693885)
        assert isclose(ONEDIM_ISOLIQ_NORAD.temp_s,
                       ONEDIM_ISOLIQ_NORAD.solution['temp_s'])


class Test_OneDimIsoLiqBlackRad(object):
    """Unit testing of OneDimIsoLiqBlackRad class."""

    def test_eval_model(self):
        res = ONEDIM_ISOLIQ_BLACKRAD.eval_model([1, 1, 1, 1])
        assert isclose(res[0], 254.49907209600156)
        assert isclose(res[1], 0.9999973637622117)
        assert isclose(res[2], 2457426.545412025)
        assert isclose(res[3], 21.01891902495625)

    def test_set_solution(self):
        ONEDIM_ISOLIQ_BLACKRAD.set_solution([1, 2, 3, 4])
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['mddp'] == 1
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['q_m'] == 2
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['q_r'] == 3
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['temp_s'] == 4

    def test_solve_iteratively(self):
        count = ONEDIM_ISOLIQ_BLACKRAD.solve_iteratively()
        assert count == 34
        assert isclose(
            ONEDIM_ISOLIQ_BLACKRAD.solution['mddp'], 4.3134887884960156e-06)
        assert isclose(
            ONEDIM_ISOLIQ_BLACKRAD.solution['q_m'], -1.3776042647982443)
        assert isclose(
            ONEDIM_ISOLIQ_BLACKRAD.solution['q_r'], -9.2030040325246905)
        assert isclose(
            ONEDIM_ISOLIQ_BLACKRAD.solution['temp_s'], 293.40654101908603)
