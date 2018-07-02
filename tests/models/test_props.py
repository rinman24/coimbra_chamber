"""Unit testing of `props` module."""

import math

import pytest

from chamber.models import props

P_VALUE = 101325
T_VALUE = 290
TDP_VALUE = 280
TS_VALUE = 285
RH_VALUE = 0.5


def test_get_c_pm():
    assert math.isclose(
        props.get_c_pm(P_VALUE, T_VALUE, TDP_VALUE),
        1017.641910841458
        )


def test_get_c_pm_sat():
    assert math.isclose(
        props.get_c_pm_sat(P_VALUE, TS_VALUE),
        1022.2835902558337
        )


def test_get_rho_m():
    assert math.isclose(
        props.get_rho_m(P_VALUE, T_VALUE, TDP_VALUE),
        1.213231099568598
        )


def test_get_rho_m_sat():
    assert math.isclose(
        props.get_rho_m_sat(P_VALUE, TS_VALUE),
        1.2327562216963954
        )


def test_get_k_m():
    assert math.isclose(
        props.get_k_m(P_VALUE, T_VALUE, TDP_VALUE),
        0.02563350730647246
        )


def test_get_k_m_sat():
    assert math.isclose(
        props.get_k_m_sat(P_VALUE, TS_VALUE),
        0.025260388108991345
        )


def test_get_alpha_m():
    assert math.isclose(
        props.get_alpha_m(P_VALUE, T_VALUE, TDP_VALUE),
        2.076201562300882e-05
        )


def test_get_alpha_m_sat():
    assert math.isclose(
        props.get_alpha_m_sat(P_VALUE, TS_VALUE),
        2.0044324561030463e-05
        )


def test_get_d_12():
    # Test Mills
    assert math.isclose(
        props.get_d_12(P_VALUE, T_VALUE, TDP_VALUE, 'Mills'),
        2.4306504684558495e-05
        )

    # Test Marrero
    assert math.isclose(
        props.get_d_12(P_VALUE, T_VALUE, TDP_VALUE, 'Marrero'),
        2.365539793302829e-05
        )

    # Test constant
    assert math.isclose(
        props.get_d_12(P_VALUE, T_VALUE, TDP_VALUE, 'constant'),
        2.416458085635347e-05
        )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        props.get_d_12(P_VALUE, T_VALUE, TDP_VALUE, 'Inman')
    err_msg = ("'Inman' is not a valid ref;"
               " try 'Mills', 'Marrero', or 'constant'.")
    assert err_msg in str(err.value)


def test_get_x_1():
    assert math.isclose(
        props.get_x_1(P_VALUE, T_VALUE, TDP_VALUE),
        0.00982822815586041
    )


def test_get_x_1_sat():
    assert math.isclose(
        props.get_x_1_sat(P_VALUE, TS_VALUE),
        0.01376427605764327
    )


def test_get_m_1():
    assert math.isclose(
        props.get_m_1(P_VALUE, T_VALUE, TDP_VALUE),
        0.0061357476021502095
    )


def test_get_m_1_sat():
    assert math.isclose(
        props.get_m_1_sat(P_VALUE, TS_VALUE),
        0.008605868703401028
    )


def test_get_h_fg_sat():
    assert math.isclose(
        props.get_h_fg_sat(TS_VALUE),
        2472806.6902607535
        )


def test_get_rh():
    assert math.isclose(
        props.get_rh(P_VALUE, T_VALUE, TDP_VALUE),
        0.5165573311068835
        )


def test_x1_2_m1():
    assert math.isclose(
        props.x1_2_m1(0.01),
        0.006243391414375084
    )


def test_get_c_pl():
    assert math.isclose(
        props.get_c_pl(TS_VALUE),
        4192.729295040042
        )


def test_get_mu():
    assert math.isclose(
        props.get_mu(P_VALUE, T_VALUE, TDP_VALUE),
        1.800077369582236e-5
        )


def test_get_tdp():
    assert math.isclose(
        props.get_tdp(P_VALUE, T_VALUE, RH_VALUE),
        279.5268317988297
        )


def test_get_mol_wgt():
    assert math.isclose(
        props.get_mol_wgt(P_VALUE, T_VALUE, TDP_VALUE),
        28.856390729921483
        )


def test_get_gamma():
    assert math.isclose(
        props.get_gamma(P_VALUE, T_VALUE, TDP_VALUE),
        0.49602914637400736
        )


def test_get_beta_m1():
    assert math.isclose(
        props.get_beta_m1(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE),
        0.002491563166729926
        )
