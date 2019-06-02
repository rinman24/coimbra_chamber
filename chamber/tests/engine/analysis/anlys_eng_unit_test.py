"""Unit test suite for analysis engine."""

from math import isclose, sqrt

import pandas as pd
from uncertainties import ufloat

from chamber.engine.analysis.service import AnalysisEngine


def test_get_observations(data_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    anlys_eng = AnalysisEngine()

    observation_data = dict(
        Tdp=[ufloat(280.123456789, 0.2), ufloat(280.2, 0.2)],
        m=[ufloat(0.1234567, 1e-7), ufloat(0.1222222, 1e-7)],
        Jref=[ufloat(0, 0), ufloat(0, 0)],
        P=[ufloat(987654, 1481), ufloat(987000, 1480)],
        Te=[ufloat(300.2, 0.2/sqrt(3)), ufloat(301.2, 0.2/sqrt(3))],
        Ts=[ufloat(290.0, 0.5), ufloat(290.2, 0.5)],
        Tic=[ufloat(291.0, 0.2), ufloat(291.2, 0.2)],
        cap_man=[True, False],
        optidew=[True, False]
        )

    time = [0, 1]

    expected = pd.DataFrame(index=time, data=observation_data)

    # Act --------------------------------------------------------------------
    observations = anlys_eng._get_observations(data_spec.observations)

    # Assert -----------------------------------------------------------------
    status_set = {'cap_man', 'optidew'}
    for time in observations.index:
        for key in observations.columns:
            this_obs = observations.loc[time, key]
            expect_this = expected.loc[time, key]
            if key not in status_set:
                # First check the nominal value
                assert isclose(
                    this_obs.nominal_value, expect_this.nominal_value
                    )
                # Then the standard deviation
                assert isclose(
                    this_obs.std_dev, expect_this.std_dev
                    )
            else:
                assert this_obs is expect_this
