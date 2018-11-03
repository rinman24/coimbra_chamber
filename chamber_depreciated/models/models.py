""".. Todo:: Docstring."""
import pandas as pd
import scipy.optimize as opt
from scipy.constants import sigma
import numpy as np

from chamber.models import film
from chamber.models import props
from chamber.models import uncertainty as unc


class Spalding:
    """Init."""

    def __init__(self, m_l, p, t_e, t_dp, ref, rule):
        """Init."""
        self._t_s_guess = None
        self._s_state = None
        self._u_state = None
        self._liq_props = None
        self._t_state = None
        self._film_props = None
        self._e_state = None
        # self.q_cu = None
        # self.q_rs = None

        # Keep a 'guide' of how to calculate film props.
        self._film_guide = dict(ref=ref, rule=rule)

        # Set the _exp_state, which should not be confused with the
        # environmental or e-state with attributes such as m_1e and h_e.
        l_s = unc.liq_length((m_l, 0))[0]
        self._exp_state = dict(m_l=m_l, p=p, t_e=t_e, t_dp=t_dp, l_s=l_s)

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

    def _eval_model(self, guess):
        mdpp_g = guess[0]
        q_cu_g = guess[1]
        q_rs_g = guess[2]
        t_s_g = guess[3]
        m_1s_g = guess[4]

        res = [0]*5

        rho_m_g = self.film_props['rho_m_g']
        d_12_g = self.film_props['d_12_g']
        l_s = self.exp_state['l_s']
        # m_1s_g = self.s_state['m_1s_g']
        m_1e = self.e_state['m_1e']
        alpha_m_g = self.film_props['alpha_m_g']
        h_e_g = self.e_state['h_e_g']
        h_fgs_g = self.s_state['h_fgs_g']
        h_t_g = self.t_state['h_t_g']
        t_e = self.exp_state['t_e']

        res[0] = (
            mdpp_g - (rho_m_g * d_12_g / l_s) * (m_1s_g - m_1e) / (1 - m_1s_g)
            )

        res[1] = (
            mdpp_g -
            (rho_m_g * alpha_m_g / l_s) *
            h_e_g / (h_fgs_g - (q_cu_g + q_rs_g) / mdpp_g)
            )

        res[2] = q_cu_g - mdpp_g * (h_t_g + h_fgs_g)

        res[3] = q_rs_g - sigma * (pow(t_e, 4) - pow(t_s_g, 4))

        res[4] = m_1s_g - props.get_m_1_sat(self.exp_state['p'], t_s_g)

        return res

    def solve_system(self, mdpp_g, q_cu_g, q_rs_g, m_1s_g):
        r"""
        Iterate through guesses to solve Spalding model.

        Itterate through guesses determined by a progressively decreasing step
        size to approach and find a solution to the Spalding model.

        Parameters
        ----------
        mdpp_g: float
            Initial guess for the mass flux in kg/s/m\ :sup:`2`.
        q_cu_g: float
            Initial guess for the conductive heat flux in liquid at
            liquid-vapor interface in W/m\ :sup:`2`.
        q_rs_g: float
            Initial guess for the radiative heat flux at the surface
            in W/m\ :sup:`2`.
        m_1s_g: float
            Inital guess for the mass fraction of water vapor in the saturated
            vapor mixture in [0, 1].

        Returns
        -------
        Series
            Series containing the results found by the solver.

        Examples
        --------
        l_s = 0.044
        ref = 'constant'
        rule = '1/2'

        # 1atm t_e=290K t_dp=289K
        p = 101325
        t_e = 290
        t_dp = 289
        spald_1 = Spalding(l_s, p, t_e, t_dp, ref, rule)
        res, df = spald_1.solve_system(2e-7, 0.01, 0.1, 0.01)

        """
        t_dp = self.exp_state['t_dp']
        t_e = self.exp_state['t_e']
        results = dict(mdpp=[], q_cu=[], q_rs=[], t_s_g=[], t_s=[], m_1s_g=[])
        # for t_s_g in np.arange(t_dp if t_dp > 273.06 else 273.06, t_e, 0.01):
        delta = 1
        alpha = 5e-3
        initial_guess = [
            mdpp_g, q_cu_g, q_rs_g, t_e if t_e > 273.07 else 273.07, m_1s_g
            ]
        self._update_model(t_dp if t_dp > 273.07 else 273.07)
        while abs(delta) > 1e-9:
            if not results['mdpp']:
                guess = initial_guess
            res = opt.fsolve(self._eval_model, guess)
            results['mdpp'].append(res[0])
            results['q_cu'].append(res[1])
            results['q_rs'].append(res[2])
            results['t_s'].append(res[3])
            results['m_1s_g'].append(res[4])
            results['t_s_g'].append(guess[3])
            delta = results['t_s'][-1] - results['t_s_g'][-1]
            t_s_g = self.t_s_guess + delta * alpha
            t_s_g = t_s_g if t_s_g > 273.07 else 273.07
            guess = [results['mdpp'][-1], results['q_cu'][-1],
                     results['q_rs'][-1], t_s_g,
                     results['m_1s_g'][-1]
                     ]
            self._update_model(t_s_g)
        res_df = pd.DataFrame(results)
        return res_df.iloc[-1]  # , res_df
