"""Spalding engine module."""

import math

import CoolProp.CoolProp as cp
import CoolProp.HumidAirProp as hap
import pandas as pd
import scipy.optimize as opt
import uncertainties as un

import chamber.utility.uncert as uncert


class Spalding(object):
    """
    Implement the 1-D D. B. Spalding model for water and air.

    Parameters
    ----------
    m : int or float
        Total mass in kg.
    p : int or float
        Pressure in Pa.
    t_e : int or float
        Ambient temperature in K.
    t_dp : int or float
        Dew point temperature in K.
    ref : {'Mills', 'Marrero'}
        Referance to use for binary species diffusivity calculation.
    rule : {'1/2', '1/3'}
        Rule to use for film property calculation.

    Examples
    --------
    Constructing Spalding model from a dictionary.

    >>> exp_state = dict(
        length=0.06, m=0.099, p=101325, t_e=290, t_dp=280, ref='Mills',
        rule='1/2')
    >>> dbs = Spalding(**exp_state)
    >>> dbs._m
    0.099

    """
    ACC_G = 9.81
    M1 = 18.015
    M2 = 28.964
    R = 0.015
    SIGMA = 5.67036713e-8

    def __init__(self, m, p, t_e, t_dp, ref, rule):  # noqa: D107
        if rule not in ['1/2', '1/3']:
            err_msg = (
                "'{0}' is not a valid rule; try '1/2' or '1/3'.".format(rule))
            raise ValueError(err_msg)
        if ref not in ['Mills', 'Marrero']:
            err_msg = (
                "'{0}' is not a valid ref; try 'Mills' or 'Marrero'."
                .format(ref))
            raise ValueError(err_msg)

        self._film_guide = dict(ref=ref, rule=rule)
        self._calculate_exp_state(m, p, t_e, t_dp)

        self._s_state = dict()
        self._u_state = dict()
        self._liq_props = dict()
        self._t_state = dict()
        self._film_props = dict()
        self._e_state = dict()
        self._solution = dict()

        self._set_s_state(t_e)
        self._set_u_state()
        self._set_liq_props()
        self._set_t_state()
        self._set_film_props()
        self._set_e_state()

    # ------------------------------------------------------------------------
    # Public methods

    def solve(self):
        """Solve the model and return result as ufloats."""
        # Solve the best guess
        t_dp = self.exp_state['T_dp'].nominal_value
        t_dp = t_dp if t_dp > 273.07 else 273.07
        result_best = self._solve(2e-7, 0.01, 0.1, 0.01, t_dp)
        exp_state_best = dict(self.exp_state)  # Keep the original

        # Set up a guess with the uncertainties
        self._exp_state['L'] = un.ufloat(
            exp_state_best['L'].nominal_value + exp_state_best['L'].std_dev,
            exp_state_best['L'].std_dev)
        self._exp_state['P'] = un.ufloat(
            exp_state_best['P'].nominal_value + exp_state_best['P'].std_dev,
            exp_state_best['P'].std_dev)
        self._exp_state['T'] = un.ufloat(
            exp_state_best['T'].nominal_value + exp_state_best['T'].std_dev,
            exp_state_best['T'].std_dev)
        self._exp_state['T_dp'] = un.ufloat(
            exp_state_best['T_dp'].nominal_value + exp_state_best['T_dp'].std_dev,
            exp_state_best['T_dp'].std_dev)

        # Solve the delta system
        self._update_model(t_dp)
        result_delta = self._solve(2e-7, 0.01, 0.1, 0.01, t_dp)
        exp_state_best = dict(self.exp_state)
        self._exp_state = exp_state_best  # reset the original

        # Calculate undertainties
        mddp_del = abs(result_best['mddp'] - result_delta['mddp'])
        t_s_del = abs(result_best['T_s'] - result_delta['T_s'])
        q_cu_del = abs(result_best['q_cu'] - result_delta['q_cu'])
        q_rs_del = abs(result_best['q_rs'] - result_delta['q_rs'])
        m_1s_del = abs(result_best['m_1s'] - result_delta['m_1s'])
        m_1e_del = abs(result_best['m_1e'] - result_delta['m_1e'])
        b_m1_del = abs(result_best['B_m1'] - result_delta['B_m1'])
        b_h_del = abs(result_best['B_h'] - result_delta['B_h'])
        g_m1_del = abs(result_best['g_m1'] - result_delta['g_m1'])
        g_h_del = abs(result_best['g_h'] - result_delta['g_h'])
        sh_del = abs(result_best['Sh_L'] - result_delta['Sh_L'])
        nu_del = abs(result_best['Nu_L'] - result_delta['Nu_L'])
        gr_m_del = abs(result_best['Gr_mR'] - result_delta['Gr_mR'])

        # Set the solution attribute
        self.solution['mddp'] = un.ufloat(result_best['mddp'], mddp_del)
        self.solution['T_s'] = un.ufloat(result_best['T_s'], t_s_del)
        self.solution['q_cu'] = un.ufloat(result_best['q_cu'], q_cu_del)
        self.solution['q_rs'] = un.ufloat(result_best['q_rs'], q_rs_del)
        self.solution['m_1s'] = un.ufloat(result_best['m_1s'], m_1s_del)
        self.solution['m_1e'] = un.ufloat(result_best['m_1e'], m_1e_del)
        self.solution['B_m1'] = un.ufloat(result_best['B_m1'], b_m1_del)
        self.solution['B_h'] = un.ufloat(result_best['B_h'], b_h_del)
        self.solution['g_m1'] = un.ufloat(result_best['g_m1'], g_m1_del)
        self.solution['g_h'] = un.ufloat(result_best['g_h'], g_h_del)
        self.solution['Sh_L'] = un.ufloat(result_best['Sh_L'], sh_del)
        self.solution['Nu_L'] = un.ufloat(result_best['Nu_L'], nu_del)
        self.solution['Gr_mR'] = un.ufloat(result_best['Gr_mR'], gr_m_del)

    # ------------------------------------------------------------------------
    # Internal methods

    def _calculate_exp_state(self, mass, press, amb_temp, dew_point):
        rho_liq = 997  # kg/m^3
        radius = 0.015  # m
        len_tube = 0.06  # m
        m_tube = un.ufloat(8.73832e-2, 8.73832e-4)  # default tube
        liq_height = (mass-m_tube) / (rho_liq*math.pi*pow(radius, 2))
        len_eff = len_tube - liq_height

        press = un.ufloat(press, press*uncert.pct_p)

        amb_temp = un.ufloat(amb_temp, uncert.del_t)

        dew_point = un.ufloat(dew_point, uncert.del_tdp)

        self._exp_state = dict(
            L=len_eff, P=press, T=amb_temp, T_dp=dew_point)

    def _set_s_state(self, t_guess):
        h_g = cp.PropsSI('H', 'T', t_guess, 'Q', 1, 'water')
        h_f = cp.PropsSI('H', 'T', t_guess, 'Q', 0, 'water')

        pressure = self.exp_state['P'].nominal_value
        x_1 = hap.HAPropsSI('Y', 'P', pressure, 'T', t_guess, 'RH', 1)
        m_1 = self._x1_2_m1(x_1)

        self._s_state['h'] = 0
        self._s_state['h_fg'] = h_g - h_f
        self._s_state['m_1'] = m_1
        self._s_state['T'] = t_guess

    def _set_u_state(self):
        self._u_state['h'] = -self.s_state['h_fg']
        self._u_state['T'] = self.s_state['T']

    def _set_liq_props(self):
        self._liq_props['T'] = self._use_rule(
            self.exp_state['T'].nominal_value, self.s_state['T'])
        self._liq_props['c_p'] = cp.PropsSI(
            'Cpmass', 'T', self._liq_props['T'], 'Q', 0, 'water')

    def _set_t_state(self):
        self._t_state['T'] = self.exp_state['T'].nominal_value
        self._t_state['h'] = (
            self.liq_props['c_p'] * (self.t_state['T'] - self.s_state['T'])
            + self.u_state['h']
            )

    def _set_film_props(self):
        film_temp = self._use_rule(
            self.exp_state['T'].nominal_value, self.s_state['T'])

        x_1s = hap.HAPropsSI(
            'Y',
            'T', self.s_state['T'],
            'P', self.exp_state['P'].nominal_value,
            'RH', 1)
        x_1e = hap.HAPropsSI(
            'Y',
            'T', self.exp_state['T'].nominal_value,
            'P', self.exp_state['P'].nominal_value,
            'Tdp', self.exp_state['T_dp'].nominal_value)
        x_1 = self._use_rule(x_1e, x_1s)
        m_1 = self._x1_2_m1(x_1)

        c_p = hap.HAPropsSI(
            'cp_ha',
            'P', self.exp_state['P'].nominal_value,
            'T', film_temp,
            'Y', x_1,
            )
        vha = hap.HAPropsSI(
            'Vha',
            'P', self.exp_state['P'].nominal_value,
            'T', film_temp,
            'Y', x_1,
            )
        rho = 1/vha
        k = hap.HAPropsSI(
            'k',
            'P', self.exp_state['P'].nominal_value,
            'T', film_temp,
            'Y', x_1,
            )
        alpha = k/(rho*c_p)
        mu = hap.HAPropsSI(
            'mu',
            'P', self.exp_state['P'].nominal_value,
            'T', film_temp,
            'Y', x_1,
            )
        nu = mu/rho
        mol_wght = m_1*self.M1 + (1-m_1)*self.M2
        beta = 1/film_temp
        gamma_1 = (mol_wght/self.M1 - 1)/rho

        ref = self.film_guide['ref']
        if ref == 'Mills':
            d_12 = (
                1.97e-5 *
                (101325/self.exp_state['P'].nominal_value) *
                pow(film_temp/256, 1.685)
                )
        elif ref == 'Marrero':
            d_12 = (
                1.87e-10 *
                pow(film_temp, 2.072) /
                (self.exp_state['P'].nominal_value/101325)
                )

        self._film_props['T'] = film_temp
        self._film_props['m_1'] = m_1
        self._film_props['c_p'] = c_p
        self._film_props['rho'] = rho
        self._film_props['k'] = k
        self._film_props['alpha'] = alpha
        self._film_props['D_12'] = d_12
        self._film_props['nu'] = nu
        self._film_props['M'] = mol_wght
        self._film_props['beta'] = beta
        self._film_props['gamma_1'] = gamma_1

    def _set_e_state(self):
        x_1 = hap.HAPropsSI(
            'Y',
            'P', self.exp_state['P'].nominal_value,
            'T', self.exp_state['T'].nominal_value,
            'Tdp', self.exp_state['T_dp'].nominal_value)
        m_1 = self._x1_2_m1(x_1)
        self._e_state['m_1'] = m_1

        self._e_state['T'] = self.exp_state['T'].nominal_value

        self._e_state['c_p'] = hap.HAPropsSI(
            'cp_ha',
            'P', self.exp_state['P'].nominal_value,
            'T', self.e_state['T'],
            'Y', x_1,
            )
        self._e_state['h'] = (
            self.e_state['c_p'] * (self.e_state['T'] - self.s_state['T'])
            + self.s_state['h'])

    def _use_rule(self, e_value, s_value):
        if self.film_guide['rule'] == '1/2':
            film_prop = (e_value+s_value)/2
        else:
            film_prop = s_value + (e_value-s_value)/3
        return film_prop

    def _x1_2_m1(self, x_1):
        num = x_1 * self.M1
        den = x_1*self.M1 + (1-x_1)*self.M2
        return num/den

    def _update_model(self, t_guess):
        self._set_s_state(t_guess)
        self._set_u_state()
        self._set_liq_props()
        self._set_t_state()
        self._set_film_props()
        self._set_e_state()

    def _eval_model(self, guess):
        mddp_g = guess[0]
        q_cu_g = guess[1]
        q_rs_g = guess[2]
        t_s_g = guess[3]
        m_1s_g = guess[4]

        res = [0]*5

        rho_m_g = self.film_props['rho']
        d_12_g = self.film_props['D_12']
        len_ = self.exp_state['L'].nominal_value
        m_1e = self.e_state['m_1']
        alpha_m_g = self.film_props['alpha']
        h_e_g = self.e_state['h']
        h_fgs_g = self.s_state['h_fg']
        h_t_g = self.t_state['h']
        t_e = self.e_state['T']
        sigma = self.SIGMA
        pressure = self.exp_state['P'].nominal_value
        x_1_s_calc = hap.HAPropsSI('Y', 'T', t_s_g, 'P', pressure, 'RH', 1)
        m_1_s_calc = self._x1_2_m1(x_1_s_calc)

        res[0] = (
            mddp_g - (rho_m_g * d_12_g / len_) * (m_1s_g - m_1e) / (1 - m_1s_g)
            )

        res[1] = (
            mddp_g -
            (rho_m_g * alpha_m_g / len_) *
            h_e_g / (h_fgs_g - (q_cu_g + q_rs_g) / mddp_g)
            )

        res[2] = q_cu_g - mddp_g * (h_t_g + h_fgs_g)

        res[3] = q_rs_g - sigma * (pow(t_e, 4) - pow(t_s_g, 4))

        res[4] = m_1s_g - m_1_s_calc

        return res

    def _solve(self, mddp_g, q_cu_g, q_rs_g, m_1s_g, t_s_g):
        """Solve the model."""
        results = dict(mddp=[], q_cu=[], q_rs=[], t_s_g=[], t_s=[], m_1s_g=[])

        delta = 1
        alpha = 5e-3
        initial_guess = [
            mddp_g, q_cu_g, q_rs_g, t_s_g, m_1s_g
            ]
        self._update_model(t_s_g)
        while abs(delta) > 1e-9:
            if not results['mddp']:
                guess = initial_guess
            res = opt.fsolve(self._eval_model, guess)
            results['mddp'].append(res[0])
            results['q_cu'].append(res[1])
            results['q_rs'].append(res[2])
            results['t_s'].append(res[3])
            results['m_1s_g'].append(res[4])
            results['t_s_g'].append(guess[3])
            delta = results['t_s'][-1] - results['t_s_g'][-1]
            t_s_g = self.s_state['T'] + delta * alpha
            t_s_g = t_s_g if t_s_g > 273.07 else 273.07
            guess = [results['mddp'][-1], results['q_cu'][-1],
                     results['q_rs'][-1], t_s_g,
                     results['m_1s_g'][-1]
                     ]
            self._update_model(t_s_g)
        results['mddp'] = results['mddp'][-1]
        results['T_s'] = results['t_s'][-1]
        results['q_cu'] = results['q_cu'][-1]
        results['q_rs'] = results['q_rs'][-1]
        results['m_1s'] = results['m_1s_g'][-1]
        
        results['m_1e'] = self.e_state['m_1']

        results['B_m1'] = (
            (self.s_state['m_1'] - self.e_state['m_1'])
            / (1-self.s_state['m_1'])
            )

        results['B_h'] = (
            (self.s_state['h'] - self.e_state['h'])
            / (self.u_state['h']
               + ((results['q_cu']+results['q_rs']) / results['mddp'])
               - self.s_state['h'])
            )
        results['g_m1'] = results['mddp']/results['B_m1']
        results['g_h'] = results['mddp']/results['B_h']

        results['Sh_L'] = (
            (results['g_m1'] * self.exp_state['L'].nominal_value)
            / (self.film_props['rho'] * self.film_props['D_12'])
            )
        results['Nu_L'] = (
            (results['g_h'] * self.exp_state['L'].nominal_value)
            / (self.film_props['rho'] * self.film_props['alpha'])
            )
        results['Gr_mR'] = (
            self.ACC_G
            * pow(self.R, 3)
            * self.film_props['gamma_1']*self.film_props['rho']*(self.s_state['m_1']
                                                                 - self.e_state['m_1'])
            / pow(self.film_props['nu'], 2)
            )

        return results

    # ------------------------------------------------------------------------
    # Properties

    @property
    def film_guide(self):
        """Get the film guide.

        A `film_guide` has the following keys:
            `ref` : Reference for binary species diffusiity.
            `rule` : Rule for calculating the film properties
        """
        return self._film_guide

    @property
    def exp_state(self):
        """Get the experimental state.

        This should not be confused with the e-state which contains
        `m_1e` and `h_e` and requires a guess at the surface temperature.

        An `exp_state` has the following keys:
            `L` : Length of Stefan tube.
            `P` : Pressure in Pa.
            `T_e` : Ambient temperature in K.
            `T_dp` : Dew point temperature in K.
        """
        return self._exp_state

    @property
    def s_state(self):
        """Get the guess at the s-state.

        The surface temperature was not measured. As a result, we must guess.
        In addition, it is assumed that the enthalpy at the s-state is zero.

        An `s_state` has the following keys:
            'h' : Specific enthalpy of the mixture at the s-state (saturated
                vapor mixture) in J/kg.
            'h_fg' : Specific enthalpy of vaporization for pure water at t_s
                in J/kg.
            'm_1' : Mass fraction of water vapor in the s-state (saturated
                vapor mixture) in [0, 1].
            'T' : Guess at the temperature in K.
        """
        return self._s_state

    @property
    def u_state(self):
        """Get the u-state.

        The `u_state` is based on a guess at the surface temperature.
        In addition, the `u_state` is assumed to be in thermodynamic
        equilibrium with the `s_state`. Finally the specific enthalpy is
        equal and opposite to `s_state['h_fg']` because the enthalpy datum
        is set at the `s_state`.

        A `u_state` has the following keys:
            'h': Specific enthalpy of pure water at t_s in J/kg.
            'T': Temperature in K.
        """
        return self._u_state

    @property
    def liq_props(self):
        """Get the liquid properties.

        The properties of the liquid depend on the temperature of the
        `s_state` and the `t_state`. It is assumed that the `t_state`
        is at the same temperature at the `exp_state`.

        A `liq_prop` dict has the following keys:
            'c_p': Specific heat of pure liquid water in J/kg K.
            'T': Temperature in K.
        """
        return self._liq_props

    @property
    def t_state(self):
        """Get the T-state.

        The `t_state` is based on a guess at the surface temperature.
        In addition, the `t_state` is assumed to be at the same temperature
        as the experimental state.

        A `t_state` has the following keys:
            'h': Specific enthalpy of pure water at t_s in J/kg.
            'T': Temperature in K.
        """
        return self._t_state

    @property
    def film_props(self):
        """Get film properties.

        The `film_props` are based on a guess at the surface temperature.

        A `film_props` attribute has the following keys:
            'c_p': Specific heat of the vapor mixture in J/kg K.
            'rho' : Specific mass of the vapor mixture in kg/m^3.
            'k' : Thermal conductivity of the vapor mixture in W/m K.
            'alpha' : Thermal diffusivity in m^2/s.
            'D_12' : Binary diffusion coefficient in m^2/s.
        """
        return self._film_props

    @property
    def e_state(self):
        """Get e-state.

        The `e_state` is based on a guess at the surface temperature.

        An `e_state` has the following keys:
            'm_1': Mass fraction of water vapor in [0, 1].
            'c_p': Specific heat of the vapor mixture in J/kg K.
            'h': Specific enthalpy of pure water at t_s in J/kg.
            'T': Temperature in K.
        """
        return self._e_state

    @property
    def solution(self):
        """Get the solution.

        The `solution` is based on a diffusion dominated assumption.

        A `solution` has the following keys:
            'mddp': Mass flux of species 1 in kg/m^2s.
            'T_s': Surface temperature in K.
            'q_cu': Conduction flux at the u surface in W/m^2.
            'q_rs': Radiative flux at the s surface in W/m^2.
            'm_1s': Mass fraction of water vapor at the s surface in [0-1].
        """
        return self._solution
