"""Unit testing of `props` module."""

import math

import numpy as np
import pytest

from chamber.models import props

P_VALUE = (101325, 1)
T_VALUE = (290, 1)
TDP_VALUE = (280, 1)
TS_VALUE = (285, 1)
RH_VALUE = (0.5, 0.01)


def test_get_c_pm():
    """Test get_c_pm."""
    assert math.isclose(
        props.get_c_pm(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        1017.641910841458
        )
    assert all(
        np.isclose(
            props.get_c_pm(P_VALUE, T_VALUE, TDP_VALUE),
            (1017.641910841458, 0.8642246765946311)
        )
    )


def test_get_c_pm_sat():
    """Test get_c_pm_sat."""
    assert math.isclose(
        props.get_c_pm_sat(P_VALUE[0], TS_VALUE[0]),
        1022.2835902558337
        )
    assert all(
        np.isclose(
            props.get_c_pm_sat(P_VALUE, TS_VALUE),
            (1022.2835902558337, 1.163174765231247)
        )
    )


def test_get_rho_m():
    """Test get_rho_m."""
    assert math.isclose(
        props.get_rho_m(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        1.213231099568598
        )
    assert all(
        np.isclose(
            props.get_rho_m(P_VALUE, T_VALUE, TDP_VALUE),
            (1.213231099568598, 0.00452319762615927)
        )
    )


def test_get_rho_m_sat():
    """Test get_rho_m_sat."""
    assert math.isclose(
        props.get_rho_m_sat(P_VALUE[0], TS_VALUE[0]),
        1.2327562216963954
        )
    assert all(
        np.isclose(
            props.get_rho_m_sat(P_VALUE, TS_VALUE),
            (1.2327562216963954,  0.004778162710130651)
        )
    )


def test_get_k_m():
    """Test get_k_m."""
    assert math.isclose(
        props.get_k_m(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        0.02563350730647246
        )
    assert all(
        np.isclose(
            props.get_k_m(P_VALUE, T_VALUE, TDP_VALUE),
            (0.02563350730647246, 7.465143177219635e-05)
        )
    )


def test_get_k_m_sat():
    """Test get_k_m_sat."""
    assert math.isclose(
        props.get_k_m_sat(P_VALUE[0], TS_VALUE[0]),
        0.025260388108991345
        )
    assert all(
        np.isclose(
            props.get_k_m_sat(P_VALUE, TS_VALUE),
            (0.025260388108991345, 7.454320267070297e-05)
        )
    )


def test_get_alpha_m():
    """Test get_alpha_m."""
    assert math.isclose(
        props.get_alpha_m(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        2.076201562300882e-05
        )
    assert all(
        np.isclose(
            props.get_alpha_m(P_VALUE, T_VALUE, TDP_VALUE),
            (2.076201562300882e-05, 1.432817367533441e-07)
        )
    )


def test_get_alpha_m_sat():
    """Test get_alpha_m_sat."""
    assert math.isclose(
        props.get_alpha_m_sat(P_VALUE[0], TS_VALUE[0]),
        2.0044324561030463e-05
        )
    assert all(
        np.isclose(
            props.get_alpha_m_sat(P_VALUE, TS_VALUE),
            (2.0044324561030463e-05, 1.1495765792420251e-07)
        )
    )


def test_get_d_12():
    """Test get_d_12."""
    # Test Mills
    assert math.isclose(
        props.get_d_12(P_VALUE[0], T_VALUE[0], TDP_VALUE[0], 'Mills'),
        2.4306504684558495e-05
        )
    assert all(
        np.isclose(
            props.get_d_12(P_VALUE, T_VALUE, TDP_VALUE, 'Mills'),
            (2.4306504684558495e-05, 1.4163719437180477e-07)
        )
    )

    # Test Marrero
    assert math.isclose(
        props.get_d_12(P_VALUE[0], T_VALUE[0], TDP_VALUE[0], 'Marrero'),
        2.365539793302829e-05
        )
    assert all(
        np.isclose(
            props.get_d_12(P_VALUE, T_VALUE, TDP_VALUE, 'Marrero'),
            (2.365539793302829e-05, 1.695612836276839e-07)
        )
    )

    # Test constant
    assert math.isclose(
        props.get_d_12(P_VALUE[0], T_VALUE[0], TDP_VALUE[0], 'constant'),
        2.416458085635347e-05
        )
    assert all(
        np.isclose(
            props.get_d_12(P_VALUE, T_VALUE, TDP_VALUE, 'constant'),
            (2.416458085635347e-05, 1.5030027598073996e-07)
        )
    )

    # Test raises ValueError
    with pytest.raises(ValueError) as err:
        props.get_d_12(P_VALUE[0], T_VALUE[0], TDP_VALUE[0], 'Inman')
    err_msg = ("'Inman' is not a valid ref;"
               " try 'Mills', 'Marrero', or 'constant'.")
    assert err_msg in str(err.value)

    with pytest.raises(ValueError) as err:
        props.get_d_12(P_VALUE, T_VALUE, TDP_VALUE, 'Inman')
    err_msg = ("'Inman' is not a valid ref;"
               " try 'Mills', 'Marrero', or 'constant'.")
    assert err_msg in str(err.value)


def test_get_x_1():
    """Test get_x_1."""
    assert math.isclose(
        props.get_x_1(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        0.00982822815586041
    )
    assert all(
        np.isclose(
            props.get_x_1(P_VALUE, T_VALUE, TDP_VALUE),
            (0.00982822815586041, 0.0006963488001588882)
        )
    )


def test_get_x_1_sat():
    """Test get_x_1_sat."""
    assert math.isclose(
        props.get_x_1_sat(P_VALUE[0], TS_VALUE[0]),
        0.01376427605764327
    )
    assert all(
        np.isclose(
            props.get_x_1_sat(P_VALUE, TS_VALUE),
            (0.01376427605764327, 0.0009358863844873)
        )
    )


def test_get_m_1():
    """Test get_m_1."""
    assert math.isclose(
        props.get_m_1(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        0.0061357476021502095
    )
    assert all(
        np.isclose(
            props.get_m_1(P_VALUE, T_VALUE, TDP_VALUE),
            (0.0061357476021502095, 0.0004364659611057649)
        )
    )


def test_get_m_1_sat():
    """Test get_m_1_sat."""
    assert math.isclose(
        props.get_m_1_sat(P_VALUE[0], TS_VALUE[0]),
        0.008605868703401028
    )
    assert all(
        np.isclose(
            props.get_m_1_sat(P_VALUE, TS_VALUE),
            (0.008605868703401028, 0.0005884161208112876)
        )
    )


def test_get_h_fg_sat():
    """Test get_h_fg_sat."""
    assert math.isclose(
        props.get_h_fg_sat(TS_VALUE[0]),
        2472806.6902607535
        )
    assert all(
        np.isclose(
            props.get_h_fg_sat(TS_VALUE),
            (2472806.6902607535, 2367.4987125825137)
        )
    )


def test_get_rh():
    """Test get_rh."""
    assert math.isclose(
        props.get_rh(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        0.5165573311068835
        )
    assert all(
        np.isclose(
            props.get_rh(P_VALUE, T_VALUE, TDP_VALUE),
            (0.5165573311068835, 0.07299917217578145)
        )
    )


def test_x1_2_m1():
    """Test x1_2_m1."""
    assert math.isclose(
        props.x1_2_m1(0.01),
        0.006243391414375084
    )
    assert all(
        np.isclose(
            props.x1_2_m1((0.01, 0.001)),
            (0.006243391414375084, 0.0006269461282050444)
        )
    )


def test_get_c_pl():
    """Test get_c_pl."""
    assert math.isclose(
        props.get_c_pl(TS_VALUE[0]),
        4192.729295040042
        )
    assert all(
        np.isclose(
            props.get_c_pl(TS_VALUE),
            (4192.729295040042, 1.4683242561413863)
        )
    )


def test_get_mu():
    """Test get_mu."""
    assert math.isclose(
        props.get_mu(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        1.800077369582236e-5
        )
    assert all(
        np.isclose(
            props.get_mu(P_VALUE, T_VALUE, TDP_VALUE),
            (1.800077369582236e-5, 5.197108679739007e-08)
        )
    )


def test_get_tdp():
    """Test get_tdp."""
    assert math.isclose(
        props.get_tdp(P_VALUE[0], T_VALUE[0], RH_VALUE[0]),
        279.5268317988297
        )
    assert all(
        np.isclose(
            props.get_tdp(P_VALUE, T_VALUE, RH_VALUE),
            (279.5268317988297, 1.2109280624741814)
        )
    )


def test_get_mol_wgt():
    """Test get_mol_wgt."""
    assert math.isclose(
        props.get_mol_wgt(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        28.856390729921483
        )
    assert all(
        np.isclose(
            props.get_mol_wgt(P_VALUE, T_VALUE, TDP_VALUE),
            (28.856390729921483, 0.0076243230129406925)
        )
    )


def test_get_gamma():
    """Test get_gamma."""
    assert math.isclose(
        props.get_gamma(P_VALUE[0], T_VALUE[0], TDP_VALUE[0]),
        0.49602914637400736
        )
    assert all(
        np.isclose(
            props.get_gamma(P_VALUE, T_VALUE, TDP_VALUE),
            (0.49602914637400736, 0.0019386355678004952)
        )
    )


def test_get_beta_m1():
    """Test get_beta_m1."""
    assert math.isclose(
        props.get_beta_m1(P_VALUE[0], T_VALUE[0], TDP_VALUE[0], TS_VALUE[0]),
        0.002491563166729926
        )
    assert all(
        np.isclose(
            props.get_beta_m1(P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE),
            (0.002491563166729926, 0.0010096089583837994)
        )
    )
