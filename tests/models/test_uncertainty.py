"""Unit testing of `props` module."""

import numpy as np
import pytest

from chamber.models import film
from chamber.models import models
from chamber.models.props import *
from chamber.models import uncertainty as unc

P_VALUE = (101325, 1)
T_VALUE = (290, 1)
TDP_VALUE = (280, 1)
TS_VALUE = (285, 1)
RH_VALUE = (0.5, 0.01)


def test_prop_uncertainty():
    """Test prop_uncecrtainty."""
    assert all(
        np.isclose(
            unc.prop_uncertainty(get_h_fg_sat, TS_VALUE),
            (2472806.6902607535, 2367.4987125825137)
        )
    )
    assert all(
        np.isclose(
            unc.prop_uncertainty(get_rho_m_sat, P_VALUE, TS_VALUE),
            (1.2327562216963954,  0.004778162710130651)
        )
    )
    assert all(
        np.isclose(
            unc.prop_uncertainty(get_c_pm, P_VALUE, T_VALUE, TDP_VALUE),
            (1017.641910841458, 0.8642246765946311)
        )
    )
    assert all(
        np.isclose(
            unc.prop_uncertainty(
                get_d_12, P_VALUE, T_VALUE, TDP_VALUE, 'Mills'
            ),
            (2.4306504684558495e-05, 1.4163719437180477e-07)
        )
    )
    assert all(
        np.isclose(
            unc.prop_uncertainty(
                get_beta_m1, P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE
            ),
            (0.002491563166729926, 0.0010096089583837994)
        )
    )
    assert all(
        np.isclose(
            unc.prop_uncertainty(
                film.est_rho_m, P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/2'
            ),
            (1.2229936606324967, 0.0046506801681449605)
        )
    )
    assert all(
        np.isclose(
            unc.prop_uncertainty(
                film.est_rho_m, P_VALUE, T_VALUE, TDP_VALUE, TS_VALUE, '1/2'
            ),
            (1.2229936606324967, 0.0046506801681449605)
        )
    )
    assert all(
        np.isclose(
            unc.prop_uncertainty(
                film.est_d_12, P_VALUE, T_VALUE,
                TDP_VALUE, TS_VALUE, '1/2', 'Mills'
            ),
            (2.3955520502741308e-05, 1.4079791498654038e-07)
        )
    )


def test_liq_length():
    """Test tube_length."""
    assert all(
        np.isclose(
            unc.liq_length((0.099, 1e-6)),
            (0.04351613825556731, 0.00024147338460503518)
        )
    )


def test_mdpp_unc():
    """Test mdpp_unc."""
    p = 101325
    t_e = 290
    t_dp = 280
    m_l = 0.099
    ref = 'constant'
    rule = '1/2'
    spald = models.Spalding(m_l, p, t_e, t_dp, ref, rule)
    res = spald.solve_system(2e-7, 0.01, 0.1, 0.01)
    mdpp = unc.mdpp_unc(res.mdpp, spald)
    assert all(
        np.isclose(
            unc.mdpp_unc(res.mdpp, spald),
            (3.2693638078615516e-06, 6.845518757751997e-08)
        )
    )
