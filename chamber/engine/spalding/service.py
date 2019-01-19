"""Spalding engine module."""

import math

import uncertainties as un

import chamber.utility.uncert as uncert


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
        self._t_s_guess = None
        self._s_state = None
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

    # ----------------------------------------------------------------------- #
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
