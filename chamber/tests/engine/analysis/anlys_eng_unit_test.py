"""Unit test suite for analysis engine."""

from math import isclose, sqrt

import dacite
import pandas as pd
import pytest
from uncertainties import ufloat

from chamber.engine.analysis.service import AnalysisEngine
from chamber.utility.plot.contracts import Axis, DataSeries, Layout, Plot


# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture(scope='module')
def anlys_eng():
    """Create a module level instance of the analysis engine."""
    return AnalysisEngine()


@pytest.fixture(scope='function')
def observations():
    """Create observations DataFrame."""
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
    """Create observation layout."""
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


# ----------------------------------------------------------------------------
# AnalysisEngine


def test_get_observations(anlys_eng, data_spec, observations):  # noqa: D103
    # Act --------------------------------------------------------------------
    anlys_eng._get_observations(data_spec.observations)
    result = anlys_eng._observations

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


def test_layout_observations(anlys_eng, data_spec, observation_layout):  # noqa: D103
    # Act --------------------------------------------------------------------
    # TODO: Move observation_layout into this test.
    # NOTE: It does not need to be a fixture.
    anlys_eng._get_observations(data_spec.observations)
    layout = anlys_eng._layout_observations()
    # Assert -----------------------------------------------------------------
    assert layout.style == observation_layout.style
    # mass and temperature
    _compare_layouts(layout, observation_layout)
    # pressure and power
    # assert layout.plots[1] == observation_layout.plots[1]
    # # status
    # assert layout.plots[2] == observation_layout.plots[2]


@pytest.mark.parametrize(
    'center, expected',
    [
        (1, [ufloat(10, 1e-1), ufloat(9, 9e-2), ufloat(8, 8e-2)]),
        (2, [ufloat(10, 1e-1), ufloat(9, 9e-2), ufloat(8, 8e-2), ufloat(7, 7e-2), ufloat(6, 6e-2)]),
        (3, [ufloat(10, 1e-1), ufloat(9, 9e-2), ufloat(8, 8e-2), ufloat(7, 7e-2), ufloat(6, 6e-2), ufloat(5, 5e-2), ufloat(4, 4e-2)]),
        (4, [ufloat(8, 8e-2), ufloat(7, 7e-2), ufloat(6, 6e-2), ufloat(5, 5e-2), ufloat(4, 4e-2)]),
        (5, [ufloat(6, 6e-2), ufloat(5, 5e-2), ufloat(4, 4e-2)]),
        ]
    )
def test_max_slice(anlys_eng, center, expected):  # noqa: D103
    """
    Test get maximum slice.

    Assumptions
    -----------
    #. DataFrame has a pd.RangeIndex with start == 0 and step == 1.
    #. Each element in the desired column is a ufloat

    """
    # Arrange ----------------------------------------------------------------
    # Build the dataframe
    data = dict(
        my_col=[
            ufloat(10, 1e-1), ufloat(9, 9e-2), ufloat(8, 8e-2), ufloat(7, 7e-2),
            ufloat(6, 6e-2), ufloat(5, 5e-2), ufloat(4, 4e-2)
            ],
        not_my_col=[-999] * 7,
        )
    dataframe = pd.DataFrame(data=data)
    # Act --------------------------------------------------------------------
    slice_ = anlys_eng._max_slice(df=dataframe, center=center, col='my_col')
    # Assert -----------------------------------------------------------------
    assert len(slice_) == len(expected)
    for result, correct in zip(slice_, expected):
        assert isclose(result.nominal_value, correct.nominal_value)
        assert isclose(result.std_dev, correct.std_dev)


def test_fit(anlys_eng):  # noqa: D103
    # ------------------------------------------------------------------------
    # Arrange
    sample = [
        ufloat(0.01465781, 1e-07),
        ufloat(0.01465775, 1e-07),
        ufloat(0.0146577, 1e-07),
        ufloat(0.01465767, 1e-07),
        ufloat(0.01465762, 1e-07),
        ]
    # ------------------------------------------------------------------------
    # Act
    result = anlys_eng._fit(sample)
    # ------------------------------------------------------------------------
    # Assert
    assert isclose(result.a, 0.014657801999999996)
    assert isclose(result.sig_a, 7.745966692414835e-08)

    assert isclose(result.b, -4.600000000048961e-08)
    assert isclose(result.sig_b, 3.162277660168379e-08)

    assert isclose(result.r2, 0.9887850467276053)

    assert isclose(result.q, 0.9990182274301309)

    assert isclose(result.chi2, 0.02400000000040884)

    assert result.nu == 3


# ----------------------------------------------------------------------------
# Test helpers


def _compare_layouts(lay1, lay2):
    assert len(lay1.plots) == len(lay2.plots)
    assert lay1.style == lay2.style
    for p1, p2 in zip(lay1.plots, lay2.plots):
        _compare_plots(p1, p2)


def _compare_plots(p1, p2):
    _compare_data_series(p1.abscissa, p2.abscissa)
    assert len(p1.axes) == len(p2.axes)
    for a1, a2 in zip(p1.axes, p2.axes):
        _compare_axes(a1, a2)
    assert p1.x_label == p2.x_label
    assert p1.legend == p2.legend


def _compare_data_series(d1, d2):
    assert len(d1.values) == len(d2.values)
    for v1, v2 in zip(d1.values, d2.values):
        assert isclose(v1, v2)
    assert len(d1.sigma) == len(d2.sigma)
    for s1, s2 in zip(d1.sigma, d2.sigma):
        assert isclose(s1, s2)
    assert d1.label == d2.label


def _compare_axes(a1, a2):
    assert len(a1.data) == len(a2.data)
    for ds1, ds2 in zip(a1.data, a2.data):
        _compare_data_series(ds1, ds2)
    assert a1.y_label == a2.y_label
    assert a1.error_type == a2.error_type
