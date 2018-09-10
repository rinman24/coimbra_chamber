"""Unit testing of `props` module."""

import numpy as np
import pytest

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
