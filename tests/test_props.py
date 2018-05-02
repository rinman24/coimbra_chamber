
import math

from chamber import props

P_VALUE = 101325
T_VALUE = 290
TDP_VALUE = 280


def test_cpm():
    assert math.isclose(
        props.get_cp_m(P_VALUE, T_VALUE, TDP_VALUE),
        1017.641910841458
        )


def test_tdp2rh():
    assert math.isclose(
        props.tdp2rh(P_VALUE, T_VALUE, TDP_VALUE),
        0.5165573311068835
        )


def test_x12m1():
    assert math.isclose(
        props.x12m1(0.01),
        0.006243391414375084
    )


def test_rho_m():
    assert math.isclose(
        props.get_rho_m(P_VALUE, T_VALUE, TDP_VALUE),
        1.213231099568598
        )


def test_k_m():
    assert math.isclose(
        props.get_k_m(P_VALUE, T_VALUE, TDP_VALUE),
        0.02563350730647246
        )
