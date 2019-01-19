"""Spalding engine module."""

import math

import CoolProp.HumidAirProp as hap
import uncertainties as un

import chamber.utility.uncert as uncert

M1 = 18.015
M2 = 28.946


class Spalding(object):
    """
    Implement the 1-D D. B. Spalding model for water and air.

    Parameters
    ----------
    length = int or float
        Total length of the Stefan tube in m.
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

    def __init__(self, m, p, t_e, t_dp, ref, rule):  # noqa: D107
        self._t_s_guess = un.ufloat(t_e, uncert.del_t)
        # self._s_state = None
        self._u_state = None
        self._liq_props = None
        self._t_state = None
        self._film_props = None
        self._e_state = None

        # Keep a 'guide' of how to calculate film props.
        self._film_guide = dict(ref=ref, rule=rule)

        rho_liq = 997  # kg/m^3
        radius = 0.015  # m
        len_tube = 0.06  # m
        m_tube = un.ufloat(8.73832e-2, 8.73832e-4)  # default tube
        liq_height = (m-m_tube)/(rho_liq*math.pi*pow(radius, 2))
        len_eff = len_tube - liq_height

        self._exp_state = dict(
            L=len_eff,
            P=un.ufloat(p, p*uncert.pct_p),
            T_e=un.ufloat(t_e, uncert.del_t),
            T_dp=un.ufloat(t_dp, uncert.del_tdp),
            )

        self._set_s_state()
    # ------------------------------------------------------------------------
    # Properties

    @property
    def film_guide(self):
        """Persist information for the calculation of film props.

        Keys
        ----
        'ref' : Reference for binary species diffusiity.
        'rule' : Rule for calculating the film properties
        """
        return self._film_guide

    @property
    def exp_state(self):
        """Dictonary of variables for the experimental state.

        This should not be confused with the e-state which contains
        'm_1e' and 'h_e' and requires a guess at the surface temperature.

        Keys
        ----
        'L' : Length of Stefan tube.
        'P' : Pressure in Pa.
        'T_e' : Ambient temperature in K.
        'T_dp' : Dew point temperature in K.
        """
        return self._exp_state

    @property
    def t_s_guess(self):
        """Guess at the surface temperature in K."""
        return self._t_s_guess

    @property
    def s_state(self):
        """Dictonary of s-state, based on guess at surface temperature.

        Keys include an '_g' suffix to indicate that each value is based on
        t_s_guess.

        Keys
        ----
        'm_1s_g' : Mass fraction of water vapor in the s-state (saturated vapor
            mixture) in [0, 1].
        'h_s_g' : Mixture enthalpy at the s-state (saturated vapor mixture) in
            J/kg.
        'h_fgs_g' : Specific enthalpy of vaporization for pure water at t_s in
            J/kg.
        """
        return self._s_state

    # ------------------------------------------------------------------------
    # Internal methods

    def _set_s_state(self):
        press = self.exp_state['P']
        temp = self.t_s_guess
        x_1s_g = hap.HAPropsSI(
            'Y',
            'P', press.nominal_value,
            'T', temp.nominal_value,
            'RH', 1)

        worst_x_1s_g = hap.HAPropsSI(
            'Y',
            'P', press.nominal_value + press.std_dev,
            'T', temp.nominal_value + temp.std_dev,
            'RH', 1)

        x_1s_g_std = abs(x_1s_g - worst_x_1s_g)
        x_1s_g = un.ufloat(x_1s_g, x_1s_g_std)  # Reassign `x_1s_g`

        num = x_1s_g*M1
        den = x_1s_g*M1 + (1-x_1s_g)*M2
        m_1s_g = num/den

        # h_fgs_g = props.get_h_fg_sat(self.t_s_guess)
        # h_s_g = 0
        # self._s_state = dict(m_1s_g=m_1s_g, h_fgs_g=h_fgs_g, h_s_g=h_s_g)
        self._s_state = dict(m_1s_g=m_1s_g)
