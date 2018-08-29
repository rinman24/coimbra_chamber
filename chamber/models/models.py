""".. Todo:: Docstring."""

import pandas as pd

from chamber.models import film
from chamber.models import props


class Spalding:
    """Init."""

    def __init__(self, p, t_e, t_dp, ref, rule):
        """Init."""
        self._t_s_guess = None
        self._s_state = None
        self._u_state = None
        self._liq_props = None
        self._t_state = None
        self._film_props = None
        self._e_state = None
        # self.q_cu = 0
        # self.q_rs = 0

        # Keep a 'guide' of how to calculate film props.
        self._film_guide = dict(ref=ref, rule=rule)

        # Set the _exp_state, which should not be confused with the
        # environmental or e-state with attributes such as m_1e and h_e.
        self._exp_state = dict(p=p, t_e=t_e, t_dp=t_dp)

    # ----------------------------------------------------------------------- #
    # Properties
    # ----------------------------------------------------------------------- #
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
        'p' : Pressure in Pa of the experimental state.
        't_e' : Dry bulb temperature of the experimental state in K.
        't_dp' : Dew point temperature of the experimental in K.
        """
        return self._exp_state

    @property
    def t_s_guess(self):
        """Guess at the surface temperature in K."""
        return self._t_s_guess

    @property
    def s_state(self):
        """
        Persist saturated state.

        Dictonary containing variables for the s-state, based on guess at
        surface temperature.

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

    @property
    def u_state(self):
        """
        Persist u state.

        Dictionary containing variables for the u-state, based on guess at
        surface temperature.

        Keys include an '_g' suffix to indicate that each value is based on
        t_s_guess.

        Keys
        ----
        h_u_g : Specific enthalpy of pure water at t_s in J/kg.
        """
        return self._u_state

    @property
    def liq_props(self):
        """
        Persist liquid properties.

        Dictionary containing variables for the liquid properties, based on
        guess at surface temperature.

        Keys include an '_g' suffix to indicate that each value is based on
        t_s_guess.

        Keys
        ----
        c_pl_g : Specific heat of pure water in J/kg K.
        """
        return self._liq_props

    @property
    def t_state(self):
        """
        Persist t state.

        Dictionary containing variables for the t-state, based on guess at
        surface temperature.

        Keys include an '_g' suffix to indicate that each value is based on
        t_s_guess.

        Keys
        ----
        h_t_g : Specific enthalpy of pure water at the 't-state' in J/kg.
        """
        return self._t_state

    @property
    def film_props(self):
        """
        Persist film properties.

        Dictionary containing variables for the vapor mixture film properties,
        based on guess at surface temperature.

        Keys include an '_g' suffix to indicate that each value is based on
        t_s_guess.

        Keys
        ----
        c_pm_g : Specific heat of vapor mixture film in J/kg K.
        rho_m_g : Specific mass of vapor mixture film in kg/m:math:`^3`
        k_m_g : Thermal conductivity of the vapor mixture film in W/m K.
        alpha_m_g : Thermal diffusivity of the vapor mixture film in
            m:math:`^2`/s.
        d_12_g : Binary species diffusivity of the vapor mixture film in
            m:math:`^2`/s
        """
        return self._film_props

    @property
    def e_state(self):
        """
        Persist e state.

        Dictonary containing variables for the e-state, based on guess at
        surface temperature and experimental state.

        Some keys include an '_g' suffix to indicate that each value is based
        on t_s_guess.

        Keys
        ----
        m_1e
        h_e_g
        """
        return self._e_state

    # ----------------------------------------------------------------------- #
    # Set States and Properties
    # ----------------------------------------------------------------------- #

    def _set_s_state(self):
        if self.t_s_guess:
            m_1s_g = props.get_m_1_sat(self._exp_state['p'], self.t_s_guess)
            h_fgs_g = props.get_h_fg_sat(self.t_s_guess)
            h_s_g = 0
            self._s_state = dict(m_1s_g=m_1s_g, h_fgs_g=h_fgs_g, h_s_g=h_s_g)
        else:
            err_msg = (
                "Cannot set `s_state` when `self.t_s_guess` is None."
                )
            raise ValueError(err_msg)

    def _set_u_state(self):
        if self.s_state:
            h_u_g = -self.s_state['h_fgs_g']
            self._u_state = dict(h_u_g=h_u_g)
        else:
            err_msg = (
                "Cannot set `u-state` when `self.s_state` is None."
                )
            raise ValueError(err_msg)

    def _set_liq_props(self):
        if self.s_state and self.u_state:
            liq_props_dict = film.est_liq_props(
                self.t_s_guess, self.exp_state['t_e'], self.film_guide['rule']
                )
            self._liq_props = dict(c_pl_g=liq_props_dict['c_pl'])
        else:
            err_msg = (
                "Cannot set `liq-props` when `self.s_state` or"
                " `self.u_state` is None."
                )
            raise ValueError(err_msg)

    def _set_t_state(self):
        if self.liq_props:
            c_pl_g = self.liq_props['c_pl_g']
            t_t = self.exp_state['t_e']
            t_s_g = self.t_s_guess
            h_u_g = self.u_state['h_u_g']

            h_t_g = c_pl_g*(t_t-t_s_g) + h_u_g
            self._t_state = dict(h_t_g=h_t_g)
        else:
            err_msg = (
                "Cannot set `t-state` when `self.liq_props` is None."
                )
            raise ValueError(err_msg)

    def _set_film_props(self):
        if self.s_state:
            film_props_dict = film.est_mix_props(
                self.exp_state['p'], self.exp_state['t_e'],
                self.exp_state['t_dp'], self.t_s_guess, self.film_guide['ref'],
                self.film_guide['rule']
                )
            self._film_props = dict(c_pm_g=film_props_dict['c_pm'],
                                    rho_m_g=film_props_dict['rho_m'],
                                    k_m_g=film_props_dict['k_m'],
                                    alpha_m_g=film_props_dict['alpha_m'],
                                    d_12_g=film_props_dict['d_12'])
        else:
            err_msg = (
                "Cannot set `film-props` when `self.s_state` is None."
                )
            raise ValueError(err_msg)

    def _set_e_state(self):
        if self.film_props:
            m_1e = props.get_m_1(self.exp_state['p'], self.exp_state['t_e'],
                                 self.exp_state['t_dp'])
            c_pm_g = self.film_props['c_pm_g']
            t_e = self.exp_state['t_e']
            t_s_g = self.t_s_guess
            h_s_g = self.s_state['h_s_g']
            h_e_g = c_pm_g*(t_e-t_s_g) + h_s_g

            self._e_state = dict(m_1e=m_1e, h_e_g=h_e_g)
        else:
            err_msg = (
                "Cannot set `e-state` when `self.film_props` is None."
                )
            raise ValueError(err_msg)

    # ----------------------------------------------------------------------- #
    # Iteratively Solve the Model
    # ----------------------------------------------------------------------- #

    def _update_model(self, t_s_guess):
        # Set the t_s_guess
        self._t_s_guess = t_s_guess

        # Update all of the states and properties
        self._set_s_state()
        self._set_u_state()
        self._set_liq_props()
        self._set_t_state()
        self._set_film_props()
        self._set_e_state()
