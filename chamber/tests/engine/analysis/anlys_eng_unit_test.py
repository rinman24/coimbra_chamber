"""Unit test suite for analysis engine."""

from math import isclose, sqrt

import dacite
import pandas as pd
import pytest
from uncertainties import ufloat

from chamber.engine.analysis.service import AnalysisEngine
from chamber.utility.plot.contracts import Axis, DataSeries, Layout, Plot


@pytest.fixture(scope='module')
def anlys_eng():
    """Create a module level instance of the analysis engine."""
    return AnalysisEngine()


@pytest.fixture(scope='module')
def observations():
    """Create a module level instance of the observations DataFrame."""
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

    return pd.DataFrame(index=time, data=observation_data)


@pytest.fixture('function')
def observation_layout():
    """Create an observation layout."""
    # First the DataSeries ---------------------------------------------------
    data_series = dict()

    # time, t
    data = {'values': [0, 1]}
    data_series['t'] = dacite.from_dict(DataSeries, data)

    # dew point, Tdp
    data = dict(
        values=[280.123456789, 280.2],
        sigma=[0.2, 0.2],
        label='Tdp')
    data_series['Tdp'] = dacite.from_dict(DataSeries, data)

    # mass, m
    data = dict(
        values=[0.1234567, 0.1222222],
        sigma=[1e-7, 1e-7],
        label='m')
    data_series['m'] = dacite.from_dict(DataSeries, data)

    # pow_ref, Jref
    data = dict(
        values=[0, 0],
        sigma=[0, 0],
        label='Jref')
    data_series['Jref'] = dacite.from_dict(DataSeries, data)

    # pressure, P
    data = dict(
        values=[987654, 987000],
        sigma=[1481, 1480],
        label='P')
    data_series['P'] = dacite.from_dict(DataSeries, data)

    # Ambient temp, Te
    data = dict(
        values=[300.2, 301.2],
        sigma=[0.2/sqrt(3), 0.2/sqrt(3)],
        label='Te')
    data_series['Te'] = dacite.from_dict(DataSeries, data)

    # Surface temp, Ts
    data = dict(
        values=[290.0, 290.2],
        sigma=[0.5, 0.5],
        label='Ts')
    data_series['Ts'] = dacite.from_dict(DataSeries, data)

    # IC temp, Tic
    data = dict(
        values=[291.0, 291.2],
        sigma=[0.2, 0.2],
        label='Tic')
    data_series['Tic'] = dacite.from_dict(DataSeries, data)

    # Cap-man status, cap_man
    data = dict(
        values=[True, False],
        label='cap_man')
    data_series['cap_man'] = dacite.from_dict(DataSeries, data)

    # Optidew status, optidew
    data = dict(
        values=[True, False],
        label='optidew')
    data_series['optidew'] = dacite.from_dict(DataSeries, data)

    # Now the Axis -----------------------------------------------------------
    axes = dict()

    data = dict(
        data=[data_series['m']], y_label='mass, [kg]',
        error_type='continuous')
    axes['mass'] = dacite.from_dict(Axis, data)

    data = dict(
        data=[data_series['Tdp'], data_series['Te'], data_series['Ts'],
              data_series['Tic']],
        y_label='temperature, [K]',
        error_type='continuous')
    axes['temp'] = dacite.from_dict(Axis, data)

    data = dict(
        data=[data_series['P']], y_label='pressure, [Pa]',
        error_type='continuous')
    axes['pressure'] = dacite.from_dict(Axis, data)

    data = dict(
        data=[data_series['Jref']], y_label='Ref power, [W]',
        error_type='continuous')
    axes['Jref'] = dacite.from_dict(Axis, data)

    data = dict(
        data=[data_series['cap_man'], data_series['optidew']],
        y_label='status')
    axes['status'] = dacite.from_dict(Axis, data)

    # Then the Plots ---------------------------------------------------------
    plots = dict()

    data = dict(
        abscissa=data_series['t'],
        axes=[axes['mass'], axes['temp']],
        x_label='index')
    plots['mass_and_temp'] = dacite.from_dict(Plot, data)

    data = dict(
        abscissa=data_series['t'],
        axes=[axes['pressure']],
        x_label='index')
    plots['pressure'] = dacite.from_dict(Plot, data)

    data = dict(
        abscissa=data_series['t'],
        axes=[axes['Jref'], axes['status']],
        x_label='index')
    plots['pow_and_status'] = dacite.from_dict(Plot, data)

    # Finally, the layout ----------------------------------------------------
    data = dict(
        plots=[
            plots['mass_and_temp'], plots['pressure'],
            plots['pow_and_status']
            ],
        style='seaborn-darkgrid')

    return dacite.from_dict(Layout, data)


def test_get_observations(anlys_eng, data_spec, observations):  # noqa: D103
    # Act --------------------------------------------------------------------
    result = anlys_eng._get_observations(data_spec.observations)

    # Assert -----------------------------------------------------------------
    status_set = {'cap_man', 'optidew'}
    for time in result.index:
        for key in result.columns:  # pylint: disable=not-an-iterable
            this_obs = result.loc[time, key]
            expect_this = observations.loc[time, key]
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


def test_layout_observations(anlys_eng, observations, observation_layout):  # noqa: D103
    # Act --------------------------------------------------------------------
    layout = anlys_eng._layout_observations(observations)
    # Assert -----------------------------------------------------------------
    assert layout.style == observation_layout.style
    # mass and temperature
    assert layout.plots[0] == observation_layout.plots[0]
    # pressure and power
    assert layout.plots[1] == observation_layout.plots[1]
    # status
    assert layout.plots[2] == observation_layout.plots[2]


def test_filter_observations(anlys_eng):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(
        a=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        b=[11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        )
    observations = pd.DataFrame(data=data)
    # Act --------------------------------------------------------------------
    observations = anlys_eng._filter_observations(observations, 3, 7)
    # Assert -----------------------------------------------------------------
    assert observations.index.tolist() == [3, 4, 5, 6, 7]
    assert observations.a.tolist() == [4, 5, 6, 7, 8]
    assert observations.b.tolist() == [14, 15, 16, 17, 18]
