"""Unit testing of models.py."""
from math import isclose

import chamber.models as models

import chamber.const as const
import tests.test_const as test_const

MODEL = models.Model(test_const.MOD_SET_01)
ONEDIM_ISOLIQ_NORAD = models.OneDimIsoLiqNoRad(test_const.MOD_SET_01)
ONEDIM_ISOLIQ_BLACKRAD = models.OneDimIsoLiqBlackRad(test_const.MOD_SET_01)
ONEDIM_ISOLIQ_BLACKGRAYRAD = \
    models.OneDimIsoLiqBlackGrayRad(test_const.MOD_SET_02)


class Test_Models(object):
    """Unit testing of Models class."""

    def test__init__(self):
        assert MODEL

        # Test settings
        assert isclose(MODEL.settings['L_t'], 0.03)
        assert isclose(MODEL.settings['P'], 99950)
        assert MODEL.settings['ref'] == 'Mills'
        assert MODEL.settings['rule'] == 'mean'
        assert isclose(MODEL.settings['T_DP'], 288)
        assert isclose(MODEL.settings['T_e'], 295)

        # Test properties
        assert isclose(MODEL.props['T_s'], 291.5)
        assert isclose(MODEL.props['alpha_m'], 2.1316027351382746e-05)
        assert isclose(MODEL.props['beta_m'], 0.0034100596760443308)
        assert isclose(MODEL.props['beta*_m'], 0.6033861519510446)
        assert isclose(MODEL.props['c_pm'], 1028.977439794093)
        assert isclose(MODEL.props['c_p1'], 1902.1686411087035)
        assert isclose(MODEL.props['D_12'], 2.510797939645015e-05)
        assert isclose(MODEL.props['h_fg'], 2457424.545412025)
        assert isclose(MODEL.props['k_m'], 0.025867252254694034)
        assert isclose(MODEL.props['m_1e'], 0.010623365736965384)
        assert isclose(MODEL.props['m_1s'], 0.013294255082507034)
        assert isclose(MODEL.props['mu_m'], 1.8106909203849476e-05)
        assert isclose(MODEL.props['nu_m'], 1.5353455953023276e-05)
        assert isclose(MODEL.props['rho_m'], 1.1793376852254565)
        assert isclose(MODEL.props['x_1e'], 0.01697037204844791)
        assert isclose(MODEL.props['x_1s'], 0.021202805952925376)

        # Test radiation properties
        assert MODEL.rad_props['eps_1'] == 1
        assert MODEL.rad_props['eps_2'] == 1
        assert MODEL.rad_props['eps_3'] == 1

        # Test reference state
        assert isclose(MODEL.ref_state['m_1'], 0.011957734324044858)
        assert isclose(MODEL.ref_state['T_m'], 293.25)
        assert isclose(MODEL.ref_state['x_1'], 0.019086589000686643)

        # Test dimensionless parameters
        assert isclose(MODEL.params['Gr_h'], -13406.091168735455)
        assert isclose(MODEL.params['Gr_mt'], 1810.1867399103678)
        assert isclose(MODEL.params['Ja_v'], 0.002709173820335637)
        assert isclose(MODEL.params['Le'], 1.1778920613376593)
        assert isclose(MODEL.params['Pr'], 0.7202775498421996)
        assert isclose(MODEL.params['Ra'], -8352.269630198443)

        # Test solution is None
        assert MODEL.solution is None

    def test___repr__(self):
        """>>> <MODEL>"""
        assert MODEL.__repr__() == test_const.REPR

    def test__str__(self):
        """>>> print(<MODEL>)"""
        assert MODEL.__str__() == test_const.STR

    def test_show_settings(self):
        """>>> print(<MODEL>)"""
        assert MODEL.show_settings(show_res=False) == test_const.STR

    def test_show_props(self):
        """>>> print(<MODEL>.show_props())"""
        assert MODEL.show_props(show_res=False) == test_const.PROPS

    def test_show_rad_props(self):
        """>>> print(<MODEL>.show_rad_props())"""
        assert MODEL.show_rad_props(show_res=False) == test_const.RAD_PROPS

    def test_show_ref_state(self):
        """>>> print(<MODEL>.show_ref_state())"""
        assert MODEL.show_ref_state(show_res=False) == test_const.REF_STATE

    def test_show_params(self):
        """>>> print(<MODEL>.show_params())"""
        # MODEL.show_params()
        # print(test_const.PARAMS)
        assert MODEL.show_params(show_res=False) == test_const.PARAMS

    def test_describe(self):
        """Docstring."""
        # No testing needed for this as all the methods have been tested above.
        pass

    def test_get_ref_state(self):
        """Test the ability to evaluate film values based on various rules."""
        assert MODEL.get_ref_state(0, 2, 'mean') == 1
        assert MODEL.get_ref_state(0, 3, 'one-third') == 2

    def test_bin_diff_coeff(self):
        """Test the calculation of the binary diffusion coefficient."""
        temp_ref, pressure = 300, 101325
        assert isclose(MODEL.get_bin_diff_coeff(temp_ref, pressure, 'Mills'),
                       1.97e-5 * (101325 / pressure) *
                       pow(temp_ref / 256, 1.685))
        assert isclose(MODEL.get_bin_diff_coeff(temp_ref, pressure, 'Marrero'),
                       1.87e-10 * pow(temp_ref, 2.072) / (pressure / 101325))

    def test_eval_props(self):
        """Test the calculation of all of the thermophysical properties."""
        MODEL.props['T_s'] = 293
        MODEL.eval_props()
        assert isclose(MODEL.props['alpha_m'], 2.139674209293613e-05)
        assert isclose(MODEL.props['beta_m'], 0.003401360544217687)
        assert isclose(MODEL.props['beta*_m'], 0.603147186094405)
        assert isclose(MODEL.props['c_pm'], 1030.2830319720397)
        assert isclose(MODEL.props['c_p1'], 1903.1216298034035)
        assert isclose(MODEL.props['D_12'], 2.521627605755569e-05)
        assert isclose(MODEL.props['h_fg'], 2453874.327285723)
        assert isclose(MODEL.props['k_m'], 0.02592145926625826)
        assert isclose(MODEL.props['m_1e'], 0.010623365736965384)
        assert isclose(MODEL.props['m_1s'], 0.014610145619944618)
        assert isclose(MODEL.props['mu_m'], 1.813689690669493e-05)
        assert isclose(MODEL.props['nu_m'], 1.5424380737853974e-05)
        assert isclose(MODEL.props['rho_m'], 1.1758589997836344)
        assert isclose(MODEL.props['T_s'], 293)
        assert isclose(MODEL.props['x_1e'], 0.01697037204844791)
        assert isclose(MODEL.props['x_1s'], 0.023283028230036043)
        MODEL.props['T_s'] = 291.5
        assert isclose(MODEL.props['T_s'], 291.5)

    def test_eval_params(self):
        """Test the calculation of all the dimensionless parameters"""
        MODEL.props['T_s'] = 293
        MODEL.eval_params()
        assert isclose(MODEL.params['Gr_h'], -7570.9718465628275)
        assert isclose(MODEL.params['Gr_mt'], 2676.1751282987025)
        assert isclose(MODEL.params['Ja_v'], 0.0015511158078812314)
        assert isclose(MODEL.params['Le'], 1.1785100716749086)
        assert isclose(MODEL.params['Pr'], 0.7208752001056339)
        assert isclose(MODEL.params['Ra'], -3528.537563755052)
        MODEL.props['T_s'] = 291.5
        assert isclose(MODEL.props['T_s'], 291.5)

    def test_run(self):
        """Docstring."""
        # No testing needed for this as all the methods have been tested above.
        pass

    def test_e_b(self):
        """Docstring."""
        assert isclose(MODEL.e_b(MODEL.settings['T_e']),
                       const.SIGMA * pow(MODEL.settings['T_e'], 4))


class Test_OneDimIsoLiqNoRad(object):
    """Unit testing of OneDimIsoLiqNoRad class."""

    def test__init__(self):
        """Docstring."""
        assert ONEDIM_ISOLIQ_NORAD

        assert len(ONEDIM_ISOLIQ_NORAD.solution) == 3
        assert ONEDIM_ISOLIQ_NORAD.solution['mddp'] is None
        assert ONEDIM_ISOLIQ_NORAD.solution['q_cs'] is None
        assert ONEDIM_ISOLIQ_NORAD.solution['T_s'] is None

    def test_eval_model(self):
        sol = ONEDIM_ISOLIQ_NORAD.eval_model([1, 1, 1])
        assert isclose(sol[0], 254.49907209600156)
        assert isclose(sol[1], 0.9999973637622117)
        assert isclose(sol[2], 2457425.545412025)

    def test_set_solution(self):
        ONEDIM_ISOLIQ_NORAD.set_solution([1, 2, 3])
        assert ONEDIM_ISOLIQ_NORAD.solution['mddp'] == 1
        assert ONEDIM_ISOLIQ_NORAD.solution['q_cs'] == 2
        assert ONEDIM_ISOLIQ_NORAD.solution['T_s'] == 3

    def test_solve(self):
        count = ONEDIM_ISOLIQ_NORAD.solve()
        assert count == 126
        assert isclose(
            ONEDIM_ISOLIQ_NORAD.solution['mddp'], 1.6526395638614737e-06)
        assert isclose(
            ONEDIM_ISOLIQ_NORAD.solution['q_cs'], -4.0660229435638495)
        assert isclose(
            ONEDIM_ISOLIQ_NORAD.solution['T_s'], 290.27625254693885)
        assert isclose(ONEDIM_ISOLIQ_NORAD.props['T_s'],
                       ONEDIM_ISOLIQ_NORAD.solution['T_s'])

    def test_show_solution(self):
        """>>> <OneDimIsoLiqNoRad>.show_props()"""
        assert ONEDIM_ISOLIQ_NORAD.show_solution(show_res=False) == \
            test_const.SOLUTION_01


class Test_OneDimIsoLiqBlackRad(object):
    """Unit testing of OneDimIsoLiqBlackRad class."""

    def test__init__(self):
        """Docstring."""
        assert ONEDIM_ISOLIQ_BLACKRAD

        assert len(ONEDIM_ISOLIQ_BLACKRAD.solution) == 4
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['mddp'] is None
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['q_cs'] is None
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['q_rad'] is None
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['T_s'] is None

    def test_eval_model(self):
        """Docstring."""
        res = ONEDIM_ISOLIQ_BLACKRAD.eval_model([1, 1, 1, 1])
        assert isclose(res[0], 254.49907209600156)
        assert isclose(res[1], 0.9999973637622117)
        assert isclose(res[2], 2457426.545412025)
        assert isclose(res[3], 430.43677457759003)

    def test_set_solution(self):
        """Docstring."""
        ONEDIM_ISOLIQ_BLACKRAD.set_solution([1, 2, 3, 4])
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['mddp'] == 1
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['q_cs'] == 2
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['q_rad'] == 3
        assert ONEDIM_ISOLIQ_BLACKRAD.solution['T_s'] == 4

    def test_solve(self):
        count = ONEDIM_ISOLIQ_BLACKRAD.solve()
        assert count == 315
        assert isclose(
            ONEDIM_ISOLIQ_BLACKRAD.solution['mddp'], 4.313551217117603e-06)
        assert isclose(
            ONEDIM_ISOLIQ_BLACKRAD.solution['q_cs'], -1.3775462599751673)
        assert isclose(
            ONEDIM_ISOLIQ_BLACKRAD.solution['q_rad'], -9.2032144826349729)
        assert isclose(
            ONEDIM_ISOLIQ_BLACKRAD.solution['T_s'], 293.40660826138048)

    def test_show_solution(self):
        """>>> <OneDimIsoLiqNoRad>.show_props()"""
        assert ONEDIM_ISOLIQ_BLACKRAD.show_solution(show_res=False) == \
            test_const.SOLUTION_02


class Test_OneDimIsoLiqBlackGrayRad(object):
    """Unit testing of OneDimIsoLiqBlackGrayRad class."""

    def test_init(self):
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD

        assert len(ONEDIM_ISOLIQ_BLACKGRAYRAD.solution) == 6
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['J_1'] is None
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['J_2'] is None
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['mddp'] is None
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['q_cs'] is None
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['q_rad'] is None
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['T_s'] is None

        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.rad_props['eps_1'] == 1
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.rad_props['eps_2'] == 1

    def test_eval_model(self):
        """Docstring."""
        res = ONEDIM_ISOLIQ_BLACKGRAYRAD.eval_model([1, 1, 1, 1, 1, 1])
        assert isclose(res[0], -0.99999994329633)
        assert isclose(res[1], 428.4367746342937)
        assert isclose(res[2], 2457426.545412025)
        assert isclose(res[3], 0.9999973637622117)
        assert isclose(res[4], 1.99999994329633)
        assert isclose(res[5], 0)

    def test_set_solution(self):
        """Docstring."""
        ONEDIM_ISOLIQ_BLACKGRAYRAD.set_solution([1, 2, 3, 4, 5, 6])
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['J_1'] == 1
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['J_2'] == 2
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['mddp'] == 3
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['q_cs'] == 4
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['q_rad'] == 5
        assert ONEDIM_ISOLIQ_BLACKGRAYRAD.solution['T_s'] == 6

    def test_solve(self):
        count = ONEDIM_ISOLIQ_BLACKGRAYRAD.solve()
        print(count)
        # assert count == 315
        # assert isclose(
        #     ONEDIM_ISOLIQ_BLACKRAD.solution['mddp'], 4.313551217117603e-06)
        # assert isclose(
        #     ONEDIM_ISOLIQ_BLACKRAD.solution['q_cs'], -1.3775462599751673)
        # assert isclose(
        #     ONEDIM_ISOLIQ_BLACKRAD.solution['q_rad'], -9.2032144826349729)
        # assert isclose(
        #     ONEDIM_ISOLIQ_BLACKRAD.solution['T_s'], 293.40660826138048)
