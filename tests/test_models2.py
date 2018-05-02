
"""Unit testing of models2.py."""

import math

import matplotlib.pyplot as plt
import pytest

import chamber.models2 as mods

@pytest.fixture(scope='module')
def spald_low():
    return mods.SpaldingLow(EXP_STATE)


class Test_SpaldingLow:
    """Unit testing of `BaseModel` class."""
    def test__init__(self, spald_low):
        # Non-Public Attributes
        assert spald_low._vars == ('mddp', 'dmdy_s', 'm1s', 'dhdy_s', 'qcu',
                                   'qrem', 'he', 'ts', 'hfgs')
        for var in spald_low._vars:
            assert spald_low.sol[var] is None

        # Check `ReferenceState` Composition
        assert isinstance(spald_low._RefFilm, mods.ReferenceFilm)
        assert spald_low._RefFilm.film_rule == 'one-third'
        assert spald_low._RefFilm.ref == 'Mills'
        assert spald_low._RefFilm.alpha is None
        assert spald_low._RefFilm.cp is None
        assert spald_low._RefFilm.d12 is None
        assert spald_low._RefFilm.k is None
        assert spald_low._RefFilm.p is None
        assert spald_low._RefFilm.rho is None
        assert spald_low._RefFilm.t is None
        assert spald_low._RefFilm.ts_guess is None
        assert spald_low._RefFilm.x is None

        # Check `Properties` Composition
        assert isinstance(spald_low._RefFilm ._FilmProps, mods.FilmProperties)
        assert spald_low._RefFilm._FilmProps.alpha is None
        assert spald_low._RefFilm._FilmProps.cp is None
        assert spald_low._RefFilm._FilmProps.d12 is None
        assert spald_low._RefFilm._FilmProps.k is None
        assert spald_low._RefFilm._FilmProps.rho is None

        # Check `ExperimentalState` Composition
        assert isinstance(spald_low._RefFilm._ExpState,
                          mods.ExperimentalState)
        assert math.isclose(spald_low._RefFilm._ExpState.p, EXP_STATE['p'])
        assert math.isclose(spald_low._RefFilm._ExpState.tch,
                            EXP_STATE['tch'])
        assert math.isclose(spald_low._RefFilm._ExpState.tdp,
                            EXP_STATE['tdp'])
        assert math.isclose(spald_low._RefFilm._ExpState.tm, EXP_STATE['tm'])
        assert math.isclose(spald_low._RefFilm._ExpState.Lt, EXP_STATE['Lt'])

    def test_fun(self, spald_low):
        # Check _fun but you need to run an update_film
        spald_low._RefFilm.update_film(285)
        res = spald_low._fun(spald_low._x0)
        assert math.isclose(res[0], 0.0007402192445895659)
        assert math.isclose(res[1], -129.95775331699213)
        assert math.isclose(res[2], 93.38525405193718)
        assert math.isclose(res[3], 25.04947820390145)
        assert math.isclose(res[4], 88888.88888888889)
        assert math.isclose(res[5], -109.29972699999996)
        assert math.isclose(res[6], -0.018069131569001473)
        assert math.isclose(res[7], 55293.158267371735)
        assert math.isclose(res[8], 62710.75875873427)

    def test_set_sol(self, spald_low):
        # Check if set solution works
        for key in spald_low.sol:
            assert spald_low.sol[key] is None
        spald_low._set_sol(spald_low._x0)
        assert math.isclose(spald_low.sol['mddp'], 1e-5)
        assert math.isclose(spald_low.sol['dmdy_s'], 25)
        assert math.isclose(spald_low.sol['m1s'], 0.01)
        assert math.isclose(spald_low.sol['dhdy_s'], 2e5)
        assert math.isclose(spald_low.sol['qcu'], 500)
        assert math.isclose(spald_low.sol['qrem'], 350)
        assert math.isclose(spald_low.sol['he'], -5000)
        assert math.isclose(spald_low.sol['ts'], 300)
        assert math.isclose(spald_low.sol['hfgs'], 2.5e6)

    def test_solve(self, spald_low):
        # Test that the solver runs
        spald_low.solve(step=1, disp=True)
        assert spald_low._iter_dets.shape == (18, 13)

        assert math.isclose(spald_low.sol['mddp'], 4.382074468687315e-06)
        assert math.isclose(spald_low.sol['dmdy_s'], -0.14701975672068773)
        assert math.isclose(spald_low.sol['m1s'], 0.014389369876865659)
        assert math.isclose(spald_low.sol['dhdy_s'], 40414.76587311302)
        assert math.isclose(spald_low.sol['qcu'], 406.6147459480628)
        assert math.isclose(spald_low.sol['qrem'], 396.82823345703474)
        assert math.isclose(spald_low.sol['he'], 1818.664464290086)
        assert math.isclose(spald_low.sol['ts'], 289.23300439536564)
        assert math.isclose(spald_low.sol['hfgs'], 2462789.078875849)
