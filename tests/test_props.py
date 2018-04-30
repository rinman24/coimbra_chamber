"""Unit testing of models2.py."""

import math

import matplotlib.pyplot as plt
import pytest

import chamber.props as props


PROP_STATE = dict(p=101325, t=295, x=0.013)
EXP_STATE = dict(p=80000, tch=290, tdp=280, tm=291, Lt=0.045)
FILM_STATE = dict(P=101325, T=295, x1=0.013)


@pytest.fixture(scope='module')
def film_props():
    return props.FilmProperties()


@pytest.fixture(scope='module')
def exp_state():
    return props.ExperimentalState(**EXP_STATE)


@pytest.fixture(scope='module')
def ref_film():
    return props.ReferenceFilm(EXP_STATE)

# --------------------------------------------------------------------------- #
# Module Level Functions
# --------------------------------------------------------------------------- #


def test_hfgs():
    assert props.hfgs(273.15) == 2500938
    assert props.hfgs(290) == 2460974
    assert props.hfgs(300) == 2437289


def test_cpm():
    assert props.cpm(FILM_STATE) == 1021.6


class Test_ExperimentalState:
    """Unit testing of `ExperimentalState` class."""

    def test__init__(self, exp_state):
        assert math.isclose(exp_state.p, 80000)
        assert math.isclose(exp_state.tch, 290)
        assert math.isclose(exp_state.tdp, 280)
        assert math.isclose(exp_state.tm, 291)
        assert math.isclose(exp_state.Lt, 0.045)

        with pytest.raises(AttributeError) as excinfo:
            exp_state.p = 90000
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            exp_state.tch = 300
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            exp_state.tdp = 300
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            exp_state.tm = 300
        assert "can't set attribute" == str(excinfo.value)

    def test__change_state(self, exp_state):
        new_state = dict(p=90000, tch=290, tdp=284, tm=290.5, Lt=0.05)
        exp_state._change_state(**new_state)

        assert math.isclose(exp_state.p, 90000)
        assert math.isclose(exp_state.tch, 290)
        assert math.isclose(exp_state.tdp, 284)
        assert math.isclose(exp_state.tm, 290.5)
        assert math.isclose(exp_state.Lt, 0.05)


class Test_ReferenceFilm:
    """Unit testing of `ExperimentalState` class."""

    def test__init__(self, ref_film):
        assert ref_film.ts_guess is None

        assert isinstance(ref_film._ExpState, props.ExperimentalState)
        assert math.isclose(ref_film._ExpState.p, 80000)
        assert math.isclose(ref_film._ExpState.tch, 290)
        assert math.isclose(ref_film._ExpState.tdp, 280)
        assert math.isclose(ref_film._ExpState.tm, 291)
        assert math.isclose(ref_film._ExpState.Lt, 0.045)

        assert isinstance(ref_film ._FilmProps, props.FilmProperties)
        assert ref_film ._FilmProps.rho is None
        assert ref_film ._FilmProps.k is None
        assert ref_film ._FilmProps.cp is None
        assert ref_film ._FilmProps.alpha is None
        assert ref_film ._FilmProps.d12 is None
        assert ref_film ._FilmProps.ref == 'Mills'

        assert ref_film.film_rule == 'one-third'

        assert ref_film.p is None
        assert ref_film.t is None
        assert ref_film.x is None
        assert ref_film.x1e is None
        assert ref_film.m1e is None
        assert ref_film.x1s_guess is None
        assert ref_film.m1s_guess is None

        with pytest.raises(AttributeError) as excinfo:
            ref_film.ts_guess = 290
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            ref_film.film_rule = 'one-half'
        assert "can't set attribute" == str(excinfo.value)

    def test_change_film_rule(self, ref_film):
        assert ref_film.film_rule == 'one-third'

        original_film_rule = ref_film.film_rule
        assert ref_film.change_film_rule('one-half')
        assert ref_film.film_rule == 'one-half'
        assert ref_film.change_film_rule(original_film_rule)

        with pytest.raises(ValueError) as excinfo:
            ref_film.change_film_rule('one')
        assert "'one' is not a valid `film_rule`." == str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            ref_film.change_film_rule(2)
        err_msg = "`film_rule` must be <class 'str'> not <class 'int'>."
        assert (err_msg == str(excinfo.value))

    def test_update_film(self, ref_film):
        assert ref_film.ts_guess is None

        # This also updates the properties.
        assert ref_film.update_film(300)
        assert math.isclose(ref_film.rho, 0.9267691278805217)
        assert math.isclose(ref_film.k, 0.026100437937392484)
        assert math.isclose(ref_film.cp, 1047.04407550437)
        assert math.isclose(ref_film.alpha, 2.689746012139042e-05)
        assert math.isclose(ref_film.d12, 3.204816199008461e-05)

        with pytest.raises(TypeError) as excinfo:
            ref_film.update_film('300')
        err_msg = "`ts_guess` must be numeric not <class 'str'>."
        assert err_msg == str(excinfo.value)

    def test__use_film_rule(self, ref_film):
        assert ref_film.film_rule == 'one-third'
        original_film_rule = ref_film.film_rule
        assert math.isclose(ref_film._use_film_rule(1, 0), 1/3)
        assert ref_film.change_film_rule('one-half')
        assert math.isclose(ref_film._use_film_rule(1, 0), 0.5)
        assert ref_film.change_film_rule(original_film_rule)

    def test__eval_x1e(self, ref_film):
        ref_film._eval_x1e()
        assert math.isclose(ref_film._x1e, 0.012439210352397811)

    def test__eval_x1s_guess(self, ref_film):
        ref_film._eval_x1s_guess()
        assert math.isclose(ref_film.x1s_guess, 0.04437177884130174)

    def test__eval_state(self, ref_film):
        ref_film._eval_state()
        assert math.isclose(ref_film.p, 80000)
        assert math.isclose(ref_film.t, 297.0)
        assert math.isclose(ref_film.x, 0.033727589345000426)
        assert math.isclose(ref_film.x1e, 0.012439210352397811)
        assert math.isclose(ref_film.m1e, 0.007773480824434691)
        assert math.isclose(ref_film.x1s_guess, 0.04437177884130174)
        assert math.isclose(ref_film.m1s_guess, 0.028069131569001475)

        assert math.isclose(ref_film._FilmProps.rho, 0.9267691278805217)
        assert math.isclose(ref_film._FilmProps.k, 0.026100437937392484)
        assert math.isclose(ref_film._FilmProps.cp, 1047.04407550437)
        assert math.isclose(ref_film._FilmProps.alpha, 2.689746012139042e-05)
        assert math.isclose(ref_film._FilmProps.d12, 3.204816199008461e-05)

    def test__x2m(self, ref_film):
        assert math.isclose(ref_film._x2m(0.01), 0.006243391414375084)


class Test_FilmProperties:
    """Unit testing of `Properties` class."""

    def test__init__(self, film_props):
        assert film_props.rho is None
        assert film_props.k is None
        assert film_props.cp is None

        assert film_props.alpha is None
        assert film_props.d12 is None
        assert film_props.ref == 'Mills'

        with pytest.raises(AttributeError) as excinfo:
            film_props.rho = 1
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            film_props.k = 0.02
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            film_props.cp = 1000
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            film_props.alpha = 2e-5
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            film_props.d12 = 2.5e-5
        assert "can't set attribute" == str(excinfo.value)

    def test__eval_rho(self, film_props):
        film_props._eval_rho(**PROP_STATE)
        assert math.isclose(film_props.rho, 1.191183667721759)

    def test__eval_k(self, film_props):
        film_props._eval_k(**PROP_STATE)
        assert math.isclose(film_props.k, 0.026001674240925747)

    def test__eval_cp(self, film_props):
        film_props._eval_cp(**PROP_STATE)
        assert math.isclose(film_props.cp, 1021.6102706953045)

    def test__eval_alpha(self, film_props):
        film_props._eval_alpha()
        assert math.isclose(film_props.alpha, 2.1366694097871384e-05)

    def test_change_ref(self, film_props):
        assert film_props.ref == 'Mills'
        original_ref = film_props.ref
        assert film_props.change_ref('Marrero')
        assert film_props.ref == 'Marrero'
        assert film_props.change_ref(original_ref)

        with pytest.raises(ValueError) as excinfo:
            film_props.change_ref('ref')
        err_msg = "`ref` must be in ('Mills', 'Marrero')."
        assert (err_msg == str(excinfo.value))

        with pytest.raises(TypeError) as excinfo:
            film_props.change_ref(1)
        err_msg = "`ref` must be <class 'str'> not <class 'int'>."
        assert (err_msg == str(excinfo.value))

    def test__eval_d12(self, film_props):
        film_props._eval_d12(p=PROP_STATE['p'], t=PROP_STATE['t'])
        assert math.isclose(film_props.d12, 2.5016812959985912e-05)

        original_ref = film_props.ref
        assert film_props.change_ref('Marrero')
        film_props._eval_d12(p=PROP_STATE['p'], t=PROP_STATE['t'])
        assert math.isclose(film_props.d12, 2.450827945070588e-05)
        assert film_props.change_ref(original_ref)

    def test_eval(self, film_props):
        ref_film = dict(p=80000, t=300, x=0.022)
        assert film_props.eval(**ref_film)

        assert math.isclose(film_props.rho, 0.9215607460590561)
        assert math.isclose(film_props.k, 0.02633755190531086)
        assert math.isclose(film_props.cp, 1032.3912146477846)
        assert math.isclose(film_props.alpha, 2.768261652495241e-05)
        assert math.isclose(film_props.d12, 3.2595513279317516e-05)
