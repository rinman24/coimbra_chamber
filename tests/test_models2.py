"""Unit testing of models2.py."""

import math

import pytest

import chamber.models2 as mods


PROP_STATE = dict(p=101325, t=295, x=0.013)
EXP_STATE = dict(p=80000, tch=290, tdp=280, tm=291)


@pytest.fixture(scope='module')
def film_props():
    return mods.FilmProperties()


@pytest.fixture(scope='module')
def exp_state():
    return mods.ExperimentalState(**EXP_STATE)


@pytest.fixture(scope='module')
def ref_film():
    return mods.ReferenceFilm(EXP_STATE)


@pytest.fixture(scope='module')
def model():
    return mods.Model(EXP_STATE)


class Test_ExperimentalState:
    """Unit testing of `ExperimentalState` class."""

    def test__init__(self, exp_state):
        assert math.isclose(exp_state.p, 80000)
        assert math.isclose(exp_state.tch, 290)
        assert math.isclose(exp_state.tdp, 280)
        assert math.isclose(exp_state.tm, 291)

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
        new_state = dict(p=90000, tch=290, tdp=284, tm=290.5)
        exp_state._change_state(**new_state)

        assert math.isclose(exp_state.p, 90000)
        assert math.isclose(exp_state.tch, 290)
        assert math.isclose(exp_state.tdp, 284)
        assert math.isclose(exp_state.tm, 290.5)


class Test_ReferenceState:
    """Unit testing of `ExperimentalState` class."""

    def test__init__(self, ref_film):
        assert ref_film.ts_guess is None

        assert isinstance(ref_film._ExpState, mods.ExperimentalState)
        assert math.isclose(ref_film._ExpState.p, 80000)
        assert math.isclose(ref_film._ExpState.tch, 290)
        assert math.isclose(ref_film._ExpState.tdp, 280)
        assert math.isclose(ref_film._ExpState.tm, 291)

        assert isinstance(ref_film ._FilmProps, mods.FilmProperties)
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
        assert ref_film._xe is None
        assert ref_film._xs is None

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

    def test_eval_xe(self, ref_film):
        ref_film._eval_xe()
        assert math.isclose(ref_film._xe, 0.012439210352397811)

    def test_eval_xs(self, ref_film):
        ref_film._eval_xs()
        assert math.isclose(ref_film._xs, 0.04437177884130174)

    def test_eval_state(self, ref_film):
        ref_film._eval_state()
        assert math.isclose(ref_film.p, 80000)
        assert math.isclose(ref_film.t, 297.0)
        assert math.isclose(ref_film.x, 0.033727589345000426)

        assert math.isclose(ref_film ._FilmProps.rho, 0.9267691278805217)
        assert math.isclose(ref_film ._FilmProps.k, 0.026100437937392484)
        assert math.isclose(ref_film ._FilmProps.cp, 1047.04407550437)
        assert math.isclose(ref_film ._FilmProps.alpha, 2.689746012139042e-05)
        assert math.isclose(ref_film ._FilmProps.d12, 3.204816199008461e-05)


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
        err_msg = "`ref` must be in ['Mills', 'Marrero']."
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


class Test_Model:
    """Unit testing of `Model` class."""

    def test__init__(self, model):
        # Check `ReferenceState` Composition
        assert isinstance(model._RefFilm, mods.ReferenceFilm)
        assert model._RefFilm.film_rule == 'one-third'
        assert model._RefFilm.ref == 'Mills'
        assert model._RefFilm.alpha is None
        assert model._RefFilm.cp is None
        assert model._RefFilm.d12 is None
        assert model._RefFilm.k is None
        assert model._RefFilm.p is None
        assert model._RefFilm.rho is None
        assert model._RefFilm.t is None
        assert model._RefFilm.ts_guess is None
        assert model._RefFilm.x is None

        # Check `Properties` Composition
        assert isinstance(model._RefFilm ._FilmProps, mods.FilmProperties)
        assert model._RefFilm._FilmProps.alpha is None
        assert model._RefFilm._FilmProps.cp is None
        assert model._RefFilm._FilmProps.d12 is None
        assert model._RefFilm._FilmProps.k is None
        assert model._RefFilm._FilmProps.rho is None

        # Check `ExperimentalState` Composition
        assert isinstance(model._RefFilm._ExpState, mods.ExperimentalState)
        assert math.isclose(model._RefFilm._ExpState.p, EXP_STATE['p'])
        assert math.isclose(model._RefFilm._ExpState.tch, EXP_STATE['tch'])
        assert math.isclose(model._RefFilm._ExpState.tdp, EXP_STATE['tdp'])
        assert math.isclose(model._RefFilm._ExpState.tm, EXP_STATE['tm'])
