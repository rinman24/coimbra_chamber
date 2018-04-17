"""Unit testing of models2.py."""

import math

import pytest

import chamber.models2 as mods


REF_STATE = dict(p=101325, t=295, x=0.013)
EXP_STATE = dict(p=80000, tch=290, tdp=280, tm=291)


@pytest.fixture(scope='module')
def props():
    return mods.Properties()


@pytest.fixture(scope='module')
def exp_state():
    return mods.ExperimentalState(**EXP_STATE)


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

    def test_update(self, exp_state):
        new_state = dict(p=90000, tch=290, tdp=284, tm=290.5)
        exp_state.update(**new_state)

        assert math.isclose(exp_state.p, 90000)
        assert math.isclose(exp_state.tch, 290)
        assert math.isclose(exp_state.tdp, 284)
        assert math.isclose(exp_state.tm, 290.5)


class Test_Properties:
    """Unit testing of `Properties` class."""

    def test__init__(self, props):
        assert props.rho is None
        assert props.k is None
        assert props.cp is None

        assert props.alpha is None
        assert props.d12 is None

        with pytest.raises(AttributeError) as excinfo:
            props.rho = 1
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            props.k = 0.02
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            props.cp = 1000
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            props.alpha = 2e-5
        assert "can't set attribute" == str(excinfo.value)

        with pytest.raises(AttributeError) as excinfo:
            props.d12 = 2.5e-5
        assert "can't set attribute" == str(excinfo.value)

    def test__eval_rho(self, props):
        props._eval_rho(**REF_STATE)
        assert math.isclose(props.rho, 1.191183667721759)

    def test__eval_k(self, props):
        props._eval_k(**REF_STATE)
        assert math.isclose(props.k, 0.026001674240925747)

    def test__eval_cp(self, props):
        props._eval_cp(**REF_STATE)
        assert math.isclose(props.cp, 1021.6102706953045)

    def test__eval_alpha(self, props):
        props._eval_alpha()
        assert math.isclose(props.alpha, 2.1366694097871384e-05)

    def test__eval_d12(self, props):
        props._eval_d12(p=REF_STATE['p'], t=REF_STATE['t'])
        assert math.isclose(props.d12, 2.5016812959985912e-05)

        props._eval_d12(p=REF_STATE['p'], t=REF_STATE['t'], ref='Marrero')
        assert math.isclose(props.d12, 2.450827945070588e-05)

    def test_eval(self, props):
        ref_state = dict(p=80000, t=300, x=0.022)
        assert props.eval(**ref_state)

        assert math.isclose(props.rho, 0.9215607460590561)
        assert math.isclose(props.k, 0.02633755190531086)
        assert math.isclose(props.cp, 1032.3912146477846)
        assert math.isclose(props.alpha, 2.768261652495241e-05)
        assert math.isclose(props.d12, 3.2595513279317516e-05)
