"""
This module contains several classes required for modeling simultaneous
heat and mass transfer problems from a Stefan tube.

Classes:
    ExperimentalState: Custom read-only datastore for experimental state.
    FilmProperties: Thermophysical properties as a function of reference state.
    ReferenceFilm: Relevant properties based on a guess at the surface
        temperature.
"""

import CoolProp.HumidAirProp as hap
import CoolProp.CoolProp as cp
import numpy as np
import pandas as pd
import scipy.optimize as opt

import chamber.const as const


class _BaseModel:
    """
    This acts as an abstract base class for models. It should never be
    instanciated directly.
    """
    sig = const.SIGMA

    def __init__(self, exp_state, film_rule='one-third', ref='Mills'):
        """Return """

        # Create the an instance of ReferenceFilm.
        self._RefFilm = ReferenceFilm(
            exp_state, ref=ref, film_rule=film_rule
            )

        # Setup the variables tuple and solution dictionary.
        self._sol = {key: None for key in self._vars}

    def _set_sol(self, sol):
        for key, val in zip(self._vars, sol):
            self._sol[key] = val

    def solve(self, step=0.05, disp=False):
        """
        This is where the logic goes to solve the model.

        In order to solve the model, a guess at the surface temperature is
        required so that film properties can be evaluated. Because the surface
        temperature is unknown, I will make guesses at it and let the model
        solve for it. The guesses will start at the freezing point of water
        and increase until it reaches the environmental temperature. At each
        iteration I will persist results and compare the guess at surface
        temperature to the solution surface temperature and select the one
        with the minimum error.
        """
        ts_guess = 273.5
        results = list()
        while ts_guess < self._RefFilm._ExpState.tm:
            if disp:
                print(ts_guess)
            self._RefFilm.update_film(ts_guess)
            sol = opt.root(self._fun, self._x0)
            details = [ts_guess, sol.success, sol.message, sol.nfev]
            results.append(list(sol.x) + details)
            ts_guess += abs(step)
        columns = np.append(self._vars, ['ts_guess', 'success', 'message', 'nfev'])
        self._iter_dets = pd.DataFrame(results, columns=columns)

        # Now that the model has been solved for all the surface temperature
        # guesses, I need to find the index where the minimum difference occurs.
        self._idx_min = abs(self._iter_dets.ts - self._iter_dets.ts_guess).idxmin()
        self._set_sol(self._iter_dets.iloc[self._idx_min, 0:len(self._vars)].values)


class SpaldingLow(_BaseModel):
    """Self similar Spalding model for low mass transfer rate theory."""

    def __init__(self, exp_state, film_rule='one-third', ref='Mills'):
        """Docstring."""
        self._vars = ('mddp', 'dmdy_s', 'm1s', 'dhdy_s', 'qcu', 'qrem', 'he',
                      'ts', 'hfgs')

        self._x0 = (1e-5, 25, 0.01, 2e5, 500, 350, -5000, 300, 2.5e6)

        _BaseModel.__init__(self, exp_state, film_rule=film_rule, ref=ref)

    def _fun(self, vars_):
        """Vector function; i.e., system of equations."""
        mddp, dmdy_s, m1s, dhdy_s, qcu, qrem, he, ts, hfgs = vars_

        res = list()

        res.append(mddp
                   + self._RefFilm.rho*self._RefFilm.d12*dmdy_s
                   - mddp*m1s)
        res.append(mddp*hfgs
                   - self._RefFilm.rho*self._RefFilm.alpha*dhdy_s
                   - qcu
                   + qrem)
        res.append(qcu
                   - self.sig*pow(self._RefFilm._ExpState.tm, 4))
        res.append(dmdy_s
                   - (self._RefFilm.m1e-m1s)/self._RefFilm._ExpState.Lt)
        res.append(dhdy_s - he/self._RefFilm._ExpState.Lt)
        res.append(qrem - self.sig*pow(ts, 4))
        res.append(
            m1s
            - self._RefFilm._x2m(hap.HAPropsSI('Y',
                                               'T', ts,
                                               'P', self._RefFilm._ExpState.p,
                                               'RH', 1.0))
            )
        res.append(
            he
            - hap.HAPropsSI('Hha',
                            'T', self._RefFilm._ExpState.tm,
                            'P', self._RefFilm._ExpState.p,
                            'Tdp', self._RefFilm._ExpState.tdp)
            + hap.HAPropsSI('Hha',
                            'T', ts,
                            'P', self._RefFilm._ExpState.p,
                            'RH', 1.0)
            )
        
        # res.append(
        #     he - self._RefFilm.cp*(self._RefFilm._ExpState.tm-ts)
        #     )
        
        res.append(hfgs
                   - cp.PropsSI('H', 'T', ts, 'Q', 1, 'water')
                   + cp.PropsSI('H', 'T', ts, 'Q', 0, 'water'))
        return res

    @property
    def sol(self):
        """Desc."""
        return self._sol
