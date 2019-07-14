"""Unit test suite for analysis engine."""

from math import isclose, sqrt
from unittest.mock import call, MagicMock

import dacite
import pandas as pd
import pytest
from uncertainties import ufloat

from chamber.access.experiment.contracts import FitSpec

from chamber.utility.io.contracts import Prompt
from chamber.utility.plot.contracts import Axis, DataSeries, Layout, Plot


# ----------------------------------------------------------------------------
# Fixtures


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


@pytest.fixture('module')
def sample():
    """Sample uses for regression analysis."""
    return [
        ufloat(0.01465781, 1e-07),
        ufloat(0.01465775, 1e-07),
        ufloat(0.0146577, 1e-07),
        ufloat(0.01465767, 1e-07),
        ufloat(0.01465762, 1e-07),
        ]


@pytest.fixture('function')
def mock_ols_fit(monkeypatch):
    """Mock of AnalysisEngine._ols_fit."""
    return_values = [
        dict(a=1.0, sig_a=1.0, b=1.0, sig_b=0.1),
        dict(a=1.0, sig_a=1.0, b=1.0, sig_b=0.01),
        dict(a=1.0, sig_a=1.0, b=1.0, sig_b=0.001),
        ]
    fit = MagicMock(side_effect=return_values)
    monkeypatch.setattr(
        'chamber.engine.analysis.service.AnalysisEngine._ols_fit',
        fit)
    return fit


@pytest.fixture('function')
def mock_evaluate_fit(monkeypatch):
    """Mock of AnalysisEngine._evaluate_fit."""
    # Define logic
    def mock_logic(this_sample, fit):
        data = dict(fit)
        data['r2'] = 0.99
        data['q'] = 0.01
        data['chi2'] = 1.5
        data['nu'] = 1
        data['exp_id'] = 1
        data['idx'] = 1
        return dacite.from_dict(FitSpec, data)

    # Assign side effect
    evaluate_fit = MagicMock(side_effect=mock_logic)

    # Patch
    monkeypatch.setattr(
        'chamber.engine.analysis.service.AnalysisEngine._evaluate_fit',
        evaluate_fit)

    return evaluate_fit


@pytest.fixture('function')
def mock_get_best_local_fit(monkeypatch):
    """Mock of AnalysisEngine._get_best_local_fit."""
    # Create two mock FitSpec DTOs for mock_get_best_local_fit to return
    fit_dto_1 = MagicMock()
    fit_dto_1.nu = 21
    fit_dto_2 = MagicMock()
    fit_dto_2.nu = 29

    # Create the mock
    fits = [None, None, fit_dto_1, fit_dto_2]
    get_best_local_fit = MagicMock(side_effect=fits)

    monkeypatch.setattr(
        'chamber.engine.analysis.service.AnalysisEngine._get_best_local_fit',
        get_best_local_fit)

    return get_best_local_fit


@pytest.fixture('function')
def mock_engine(monkeypatch):
    """Mock of AnalysisEngine._process_fits logic."""
    engine = MagicMock()

    monkeypatch.setattr(
        'chamber.engine.analysis.service.AnalysisEngine._get_observations',
        engine._get_observations)

    engine._layout_observations = MagicMock(return_value='test_layout')
    monkeypatch.setattr(
        'chamber.engine.analysis.service.AnalysisEngine._layout_observations',
        engine._layout_observations)

    monkeypatch.setattr(
        'chamber.utility.plot.service.PlotUtility.plot',
        engine._plot_util.plot)

    engine._io_util.get_input = MagicMock(return_value='y')
    monkeypatch.setattr(
        'chamber.utility.io.service.IOUtility.get_input',
        engine._io_util.get_input)

    monkeypatch.setattr(
        'chamber.engine.analysis.service.AnalysisEngine._get_fits',
        engine._get_fits)

    monkeypatch.setattr(
        'chamber.engine.analysis.service.AnalysisEngine._persist_fits',
        engine._persist_fits)

    return engine

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
    anlys_eng._get_observations(data_spec.observations)
    layout = anlys_eng._layout_observations()
    # Assert -----------------------------------------------------------------
    assert layout.style == observation_layout.style
    _compare_layouts(layout, observation_layout)


def test_ols_fit(anlys_eng, sample):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    anlys_eng._this_sample = sample
    # ------------------------------------------------------------------------
    # Act
    result = anlys_eng._ols_fit()
    # ------------------------------------------------------------------------
    # Assert
    assert isclose(result['a'], 0.014657801999999996)
    assert isclose(result['sig_a'], 7.745966692414835e-08)

    assert isclose(result['b'], -4.600000000048961e-08)
    assert isclose(result['sig_b'], 3.162277660168379e-08)


def test_evaluate_fit(anlys_eng, sample):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    anlys_eng._this_sample = sample
    anlys_eng._this_fit = anlys_eng._ols_fit()
    # ------------------------------------------------------------------------
    # Act
    anlys_eng._evaluate_fit()
    # ------------------------------------------------------------------------
    # Assert
    result = anlys_eng._evaluated_fit

    assert isclose(result['a'], 0.014657801999999996)
    assert isclose(result['sig_a'], 7.745966692414835e-08)

    assert isclose(result['b'], -4.600000000048961e-08)
    assert isclose(result['sig_b'], 3.162277660168379e-08)

    assert isclose(result['r2'], 0.9887850467276053)

    assert isclose(result['q'], 0.9990182274301309)

    assert isclose(result['chi2'], 0.02400000000040884)

    assert result['nu'] == 3


@pytest.mark.parametrize(
    'steps, limits',
    [
        (1, [(1, 3), (0, 4), ]),
        (2, [(0, 4), ]),
        ]
    )
def test_get_best_local_fit_takes_correct_steps(
        anlys_eng, steps, limits, sample, mock_ols_fit, mock_evaluate_fit):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    calls = [call() for i, j in limits]
    anlys_eng._sample = sample
    anlys_eng._steps = steps
    # Act --------------------------------------------------------------------
    anlys_eng._get_best_local_fit()
    # Assert -----------------------------------------------------------------
    assert len(calls) == len(mock_ols_fit.mock_calls)
    mock_ols_fit.assert_has_calls(calls)


@pytest.mark.parametrize(
    'requested_error, expected_result',
    [
        (0.1, 0.1),
        (0.01, 0.01),
        (0.001, None),
        ]
    )
def test_get_best_local_fit_stops_with_correct_error(
        anlys_eng, sample, requested_error, expected_result, mock_ols_fit,
        mock_evaluate_fit):  # noqa: D103
    # ------------------------------------------------------------------------
    # Act
    result = anlys_eng._get_best_local_fit()
    # ------------------------------------------------------------------------
    # Assert
    if result:  # Best fit found a fit before running out of samples
        slope_error = result.sig_b/abs(result.b)
        assert isclose(slope_error, requested_error)
    else:  # Error theshold never reached and therefore no best fit
        assert not result


def test_process_fits(anlys_eng, data_spec, mock_engine):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    expected_calls = [
        call._get_observations(data_spec.observations),
        call._layout_observations(),
        call._plot_util.plot('test_layout'),
        call._io_util.get_input(
            Prompt(messages=['Would you like to continue?: [y]/n '])),
        call._get_fits(),
        call._persist_fits(),
    ]
    # Act --------------------------------------------------------------------
    anlys_eng.process_fits(data_spec)
    # Assert -----------------------------------------------------------------
    mock_engine.assert_has_calls(expected_calls)


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
