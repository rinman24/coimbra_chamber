"""Spalding engine module."""

import math

import CoolProp.CoolProp as cp
import CoolProp.HumidAirProp as hap
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

    M1 = 18.015
    M2 = 28.964

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
        self._solution = None

        self._set_s_state(t_e)
        self._set_u_state()
        self._set_liq_props()
        self._set_t_state()
        self._set_film_props()
        self._set_e_state()

    # ------------------------------------------------------------------------
    # Public methods

    def solve(self):
        """Solve the model."""
        pass

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

        ref = self.film_guide['ref']
        if ref == 'Mills':
            d_12 = 1.97e-5*(101325/self.exp_state['P'].nominal_value)*pow(film_temp/256, 1.685)
        elif ref == 'Marrero':
            d_12 = 1.87e-10*pow(film_temp, 2.072)/(self.exp_state['P'].nominal_value/101325)

        self._film_props['T'] = film_temp
        self._film_props['m_1'] = m_1
        self._film_props['c_p'] = c_p
        self._film_props['rho'] = rho
        self._film_props['k'] = k
        self._film_props['alpha'] = alpha
        self._film_props['D_12'] = d_12

    def _set_e_state(self):
        x_1 = hap.HAPropsSI(
            'Y',
            'P', self.exp_state['P'].nominal_value,
            'T', self.exp_state['T'].nominal_value,
            'Tdp', self.exp_state['T_dp'].nominal_value)
        m_1 = self._x1_2_m1(x_1)
        self._e_state['m_1'] = m_1

        self._e_state['T'] = self.exp_state['T'].nominal_value

        self._e_state['h'] = (
            self.film_props['c_p'] * (self.e_state['T'] - self.s_state['T'])
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
        """Dictonary of e-state based on guess at surface temperature."""
        return self._e_state

    @property
    def solution(self):
        """Solution of the model with uncertainties."""
        return self._e_state
