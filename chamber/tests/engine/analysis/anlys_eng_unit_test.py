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
# Module level globals


TOL = dict(abs_tol=1e-12, rel_tol=1e-5)


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
    data = dict(
        m=[
            ufloat(0.01465781, 1e-07),
            ufloat(0.01465775, 1e-07),
            ufloat(0.0146577, 1e-07),
            ufloat(0.01465767, 1e-07),
            ufloat(0.01465762, 1e-07),
        ],
        Te=[
            ufloat(290.052, 0.06324),
            ufloat(290.048, 0.06324),
            ufloat(290.055, 0.06324),
            ufloat(290.051, 0.06324),
            ufloat(290.057, 0.06324),
        ],
        Tdp=[
            ufloat(284.12, 0.2),
            ufloat(284.18, 0.2),
            ufloat(284.18, 0.2),
            ufloat(284.18, 0.2),
            ufloat(284.22, 0.2),
        ],
        Ts=[
            ufloat(290.36, 0.5),
            ufloat(290.32, 0.5),
            ufloat(290.34, 0.5),
            ufloat(290.24, 0.5),
            ufloat(290.24, 0.5),
        ],
        P=[
            ufloat(100086.0, 150.0),
            ufloat(100108.0, 150.0),
            ufloat(100091.0, 150.0),
            ufloat(100069.0, 150.0),
            ufloat(100064.0, 150.0),
        ],
    )
    return pd.DataFrame(data=data)


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


@pytest.fixture('function')
def mock_io_util(monkeypatch):
    """Mock of IOUtility."""
    util = MagicMock()

    util.get_input = MagicMock(
        side_effect=[['string', 3.14], [None, None], [10, 1], [10, 20], ])

    monkeypatch.setattr(
        'chamber.utility.io.service.IOUtility.get_input',
        util.get_input
    )

    return util


# ----------------------------------------------------------------------------
# AnalysisEngine


def test_get_observations(anlys_eng, data_spec, observations):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    anlys_eng._data = data_spec
    # Act --------------------------------------------------------------------
    anlys_eng._get_observations()
    # Assert -----------------------------------------------------------------
    result = anlys_eng._observations
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
    # Arrange ----------------------------------------------------------------
    anlys_eng._data = data_spec
    # Act --------------------------------------------------------------------
    anlys_eng._get_observations()
    # Assert -----------------------------------------------------------------
    layout = anlys_eng._layout_observations()
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
    result = anlys_eng._this_fit

    assert isclose(result['a'], 0.014657801999999996)
    assert isclose(result['sig_a'], 7.745966692414835e-08)

    assert isclose(result['b'], -4.600000000048961e-08)
    assert isclose(result['sig_b'], 3.162277660168379e-08)

    assert isclose(result['r2'], 0.9887850467276053)

    assert isclose(result['q'], 0.9990182274301309)

    assert isclose(result['chi2'], 0.02400000000040884)

    assert result['nu_chi'] == 3


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
    # Arrange ----------------------------------------------------------------
    anlys_eng._sample = sample
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
    anlys_eng._data = data_spec
    expected_calls = [
        call._get_observations(),
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


def test_set_local_exp_state(anlys_eng, sample):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    anlys_eng._this_sample = sample
    # Act --------------------------------------------------------------------
    anlys_eng._set_local_exp_state()
    # Assert -----------------------------------------------------------------
    result = anlys_eng._experimental_state

    assert isclose(result['Tdp'].nominal_value, 284.176)
    assert isclose(result['Te'].nominal_value, 290.0526)
    assert isclose(result['Ts'].nominal_value, 288.723175)
    assert isclose(result['P'].nominal_value, 100083.6)

    assert isclose(result['Tdp'].std_dev, 0.0894427191)
    assert isclose(result['Te'].std_dev, 0.028281787779)
    assert isclose(result['Ts'].std_dev, 0.246723662)
    assert isclose(result['P'].std_dev, 67.0820393)


def test_set_local_properties(anlys_eng, sample):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    anlys_eng._this_sample = sample
    anlys_eng._set_local_exp_state()
    anlys_eng._this_fit = dict(b=-1.95962946e-8, sig_b=1.943679571e-10)
    # Act --------------------------------------------------------------------
    anlys_eng._set_local_properties()
    # Assert -----------------------------------------------------------------
    # Properties first .......................................................
    # We want to keep these properties as ufloats to ensure error propagation
    # is automatic.
    result = anlys_eng._properties

    assert isclose(result['mddp'].nominal_value, 2.772308579e-05, **TOL)
    assert isclose(result['x1s'].nominal_value, 0.01775459089, **TOL)
    assert isclose(result['x1e'].nominal_value, 0.01319417284, **TOL)
    assert isclose(result['x1'].nominal_value, 0.01547438186, **TOL)
    assert isclose(result['m1s'].nominal_value, 0.01111759981, **TOL)
    assert isclose(result['m1e'].nominal_value, 0.008247635057, **TOL)
    assert isclose(result['m1'].nominal_value, 0.009682617432, **TOL)
    assert isclose(result['rhos'].nominal_value, 1.200089891, **TOL)
    assert isclose(result['rhoe'].nominal_value, 1.1966254259, **TOL)
    assert isclose(result['rho'].nominal_value, 1.198357659, **TOL)
    assert isclose(result['Bm1'].nominal_value, 0.002902230588, **TOL)
    assert isclose(result['T'].nominal_value, 289.3878875, **TOL)
    assert isclose(result['D12'].nominal_value, 2.452053646e-05, **TOL)
    assert isclose(result['hfg'].nominal_value, 2463995.459, **TOL)
    assert isclose(result['hu'].nominal_value, -2463995.459, **TOL)
    assert isclose(result['hs'].nominal_value, 0, **TOL)
    assert isclose(result['cpv'].nominal_value, 1014.5270579, **TOL)
    assert isclose(result['he'].nominal_value, 1348.737634, **TOL)
    assert isclose(result['cpl'].nominal_value, 4187.515626, **TOL)
    assert isclose(result['hT'].nominal_value, 5566.987961, **TOL)
    assert isclose(result['qcu'].nominal_value, 68.46389159, **TOL)
    assert isclose(result['Ebe'].nominal_value, 401.3453444, **TOL)
    assert isclose(result['Ebs'].nominal_value, 394.0376841, **TOL)
    assert isclose(result['qrs'].nominal_value, 7.210491646, **TOL)
    assert isclose(result['kv'].nominal_value, 0.0255848377, **TOL)
    assert isclose(result['alpha'].nominal_value, 2.104420756e-05, **TOL)
    assert isclose(result['Bh'].nominal_value, -0.00507699306, **TOL)
    assert isclose(result['M'].nominal_value, 28.8579850, **TOL)
    assert isclose(result['gamma1'].nominal_value, 0.5022594719, **TOL)
    assert isclose(result['gamma2'].nominal_value, -0.00305437414, **TOL)
    assert isclose(result['beta'].nominal_value, 0.003455569646, **TOL)
    assert isclose(result['Delta_m'].nominal_value, 0.00286996475, **TOL)
    assert isclose(result['Delta_T'].nominal_value, -1.329425, **TOL)
    assert isclose(result['mu'].nominal_value, 1.794143889e-05, **TOL)
    assert isclose(result['nu'].nominal_value, 1.49716896e-05, **TOL)

    assert isclose(result['mddp'].std_dev, 4.60701097856e-07, **TOL)
    assert isclose(result['x1s'].std_dev, 0.0002828675954, **TOL)
    assert isclose(result['x1e'].std_dev, 7.86428302795e-05, **TOL)
    assert isclose(result['x1'].std_dev, 0.0001467981363, **TOL)
    assert isclose(result['m1s'].std_dev, 0.0001783233466, **TOL)
    assert isclose(result['m1e'].std_dev, 4.940580078e-05, **TOL)
    assert isclose(result['m1'].std_dev, 9.2520469498e-05, **TOL)
    assert isclose(result['rhos'].std_dev, 0.001027878884, **TOL)
    assert isclose(result['rhoe'].std_dev, 0.0001170215376, **TOL)
    assert isclose(result['rho'].std_dev, 0.00051725937395, **TOL)
    assert isclose(result['Bm1'].std_dev, 0.00018762568497, **TOL)
    assert isclose(result['T'].std_dev, 0.12416966710916158, **TOL)
    assert isclose(result['D12'].std_dev, 2.417443588e-08, **TOL)
    assert isclose(result['hfg'].std_dev, 1126.860038, **TOL)
    assert isclose(result['hu'].std_dev, 1126.860038, **TOL)
    assert isclose(result['hs'].std_dev, 0, **TOL)
    assert isclose(result['cpv'].std_dev, 0.002956749426, **TOL)
    assert isclose(result['he'].std_dev, 251.9469741, **TOL)
    assert isclose(result['cpl'].std_dev, 0.1216812541, **TOL)
    assert isclose(result['hT'].std_dev, 1039.924855, **TOL)
    assert isclose(result['qcu'].std_dev, 1.138524024, **TOL)
    assert isclose(result['Ebe'].std_dev, 0.1565338681, **TOL)
    assert isclose(result['Ebs'].std_dev, 1.346873806, **TOL)
    assert isclose(result['qrs'].std_dev, 1.337909842, **TOL)
    assert isclose(result['kv'].std_dev, 9.186775478e-06, **TOL)
    assert isclose(result['alpha'].std_dev, 1.181578989e-08, **TOL)
    assert isclose(result['Bh'].std_dev, 8.26715095e-05, **TOL)
    assert isclose(result['M'].std_dev, 0.001013006621, **TOL)
    assert isclose(result['gamma1'].std_dev, 0.0002218153945, **TOL)
    assert isclose(result['gamma2'].std_dev, 2.9215272676e-05, **TOL)
    assert isclose(result['beta'].std_dev, 1.4827052243e-06, **TOL)
    assert isclose(result['Delta_m'].std_dev, 0.000185040939, **TOL)
    assert isclose(result['Delta_T'].std_dev, 0.24833933421832313, **TOL)
    assert isclose(result['mu'].std_dev, 5.968184047e-09, **TOL)
    assert isclose(result['nu'].std_dev, 8.158787725e-09, **TOL)

    # Then the fit ...........................................................
    # The fit has them broken out into separate floats that can be stored in
    # the database.
    result = anlys_eng._this_fit

    assert isclose(result['mddp'], 2.772308579e-05, **TOL)
    assert isclose(result['x1s'], 0.01775459089, **TOL)
    assert isclose(result['x1e'], 0.01319417284, **TOL)
    assert isclose(result['x1'], 0.01547438186, **TOL)
    assert isclose(result['m1s'], 0.01111759981, **TOL)
    assert isclose(result['m1e'], 0.008247635057, **TOL)
    assert isclose(result['m1'], 0.009682617432, **TOL)
    assert isclose(result['rhos'], 1.200089891, **TOL)
    assert isclose(result['rhoe'], 1.1966254259, **TOL)
    assert isclose(result['rho'], 1.198357659, **TOL)
    assert isclose(result['Bm1'], 0.002902230588, **TOL)
    assert isclose(result['T'], 289.3878875, **TOL)
    assert isclose(result['D12'], 2.452053646e-05, **TOL)
    assert isclose(result['hfg'], 2463995.459, **TOL)
    assert isclose(result['hu'], -2463995.459, **TOL)
    assert isclose(result['hs'], 0, **TOL)
    assert isclose(result['cpv'], 1014.5270579, **TOL)
    assert isclose(result['he'], 1348.737634, **TOL)
    assert isclose(result['cpl'], 4187.515626, **TOL)
    assert isclose(result['hT'], 5566.987961, **TOL)
    assert isclose(result['qcu'], 68.46389159, **TOL)
    assert isclose(result['Ebe'], 401.3453444, **TOL)
    assert isclose(result['Ebs'], 394.0376841, **TOL)
    assert isclose(result['qrs'], 7.210491646, **TOL)
    assert isclose(result['kv'], 0.0255848377, **TOL)
    assert isclose(result['alpha'], 2.104420756e-05, **TOL)
    assert isclose(result['Bh'], -0.00507699306, **TOL)
    assert isclose(result['M'], 28.8579850, **TOL)
    assert isclose(result['gamma1'], 0.5022594719, **TOL)
    assert isclose(result['gamma2'], -0.00305437414, **TOL)
    assert isclose(result['beta'], 0.003455569646, **TOL)
    assert isclose(result['Delta_m'], 0.00286996475, **TOL)
    assert isclose(result['Delta_T'], -1.329425, **TOL)
    assert isclose(result['mu'], 1.794143889e-05, **TOL)
    assert isclose(result['nu'], 1.49716896e-05, **TOL)

    assert isclose(result['sig_mddp'], 4.60701097856e-07, **TOL)
    assert isclose(result['sig_x1s'], 0.0002828675954, **TOL)
    assert isclose(result['sig_x1e'], 7.86428302795e-05, **TOL)
    assert isclose(result['sig_x1'], 0.0001467981363, **TOL)
    assert isclose(result['sig_m1s'], 0.0001783233466, **TOL)
    assert isclose(result['sig_m1e'], 4.940580078e-05, **TOL)
    assert isclose(result['sig_m1'], 9.2520469498e-05, **TOL)
    assert isclose(result['sig_rhos'], 0.001027878884, **TOL)
    assert isclose(result['sig_rhoe'], 0.0001170215376, **TOL)
    assert isclose(result['sig_rho'], 0.00051725937395, **TOL)
    assert isclose(result['sig_Bm1'], 0.00018762568497, **TOL)
    assert isclose(result['sig_T'], 0.12416966710916158, **TOL)
    assert isclose(result['sig_D12'], 2.417443588e-08, **TOL)
    assert isclose(result['sig_hfg'], 1126.860038, **TOL)
    assert isclose(result['sig_hu'], 1126.860038, **TOL)
    assert isclose(result['sig_hs'], 0, **TOL)
    assert isclose(result['sig_cpv'], 0.002956749426, **TOL)
    assert isclose(result['sig_he'], 251.9469741, **TOL)
    assert isclose(result['sig_cpl'], 0.1216812541, **TOL)
    assert isclose(result['sig_hT'], 1039.924855, **TOL)
    assert isclose(result['sig_qcu'], 1.138524024, **TOL)
    assert isclose(result['sig_Ebe'], 0.1565338681, **TOL)
    assert isclose(result['sig_Ebs'], 1.346873806, **TOL)
    assert isclose(result['sig_qrs'], 1.337909842, **TOL)
    assert isclose(result['sig_kv'], 9.186775478e-06, **TOL)
    assert isclose(result['sig_alpha'], 1.181578989e-08, **TOL)
    assert isclose(result['sig_Bh'], 8.26715095e-05, **TOL)
    assert isclose(result['sig_M'], 0.001013006621, **TOL)
    assert isclose(result['sig_gamma1'], 0.0002218153945, **TOL)
    assert isclose(result['sig_gamma2'], 2.9215272676e-05, **TOL)
    assert isclose(result['sig_beta'], 1.4827052243e-06, **TOL)
    assert isclose(result['sig_Delta_m'], 0.000185040939, **TOL)
    assert isclose(result['sig_Delta_T'], 0.24833933421832313, **TOL)
    assert isclose(result['sig_mu'], 5.968184047e-09, **TOL)
    assert isclose(result['sig_nu'], 8.158787725e-09, **TOL)


def test_set_nondim_groups(anlys_eng, sample):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    anlys_eng._this_sample = sample
    anlys_eng._set_local_exp_state()
    anlys_eng._this_fit = dict(b=-1.95962946e-8, sig_b=1.943679571e-10)
    anlys_eng._set_local_properties()
    # Act --------------------------------------------------------------------
    anlys_eng._set_nondim_groups()
    # Assert -----------------------------------------------------------------
    # Groups first ...........................................................
    result = anlys_eng._nondim_groups

    assert isclose(result['ShR'].nominal_value, 4.883306014, **TOL)
    assert isclose(result['NuR'].nominal_value, -3.239682362, **TOL)
    assert isclose(result['Le'].nominal_value, 1.165191723, **TOL)
    assert isclose(result['GrR_binary'].nominal_value, -423.4062806, **TOL)
    assert isclose(result['GrR_primary'].nominal_value, 427.0226524, **TOL)

    assert isclose(result['ShR'].std_dev, 0.3206133366, **TOL)
    assert isclose(result['NuR'].std_dev, 0.06555358581, **TOL)
    assert isclose(result['Le'].std_dev, 0.001321978489, **TOL)
    assert isclose(result['GrR_binary'].std_dev, 128.377472, **TOL)
    assert isclose(result['GrR_primary'].std_dev, 127.9778022, **TOL)

    # Then the fit ...........................................................
    result = anlys_eng._this_fit

    assert isclose(result['ShR'], 4.883306014, **TOL)
    assert isclose(result['NuR'], -3.239682362, **TOL)
    assert isclose(result['Le'], 1.165191723, **TOL)
    assert isclose(result['GrR_binary'], -423.4062806, **TOL)
    assert isclose(result['GrR_primary'], 427.0226524, **TOL)

    assert isclose(result['sig_ShR'], 0.3206133366, **TOL)
    assert isclose(result['sig_NuR'], 0.06555358581, **TOL)
    assert isclose(result['sig_Le'], 0.001321978489, **TOL)
    assert isclose(result['sig_GrR_binary'], 128.377472, **TOL)
    assert isclose(result['sig_GrR_primary'], 127.9778022, **TOL)


def test_get_bounds_to_filter(anlys_eng, mock_io_util):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    prompt = anlys_eng._filter_observations_prompt
    expected_calls = [call(prompt)] * 4
    expected_bounds = (10, 20)
    # Act --------------------------------------------------------------------
    anlys_eng._get_bounds_to_filter()
    # Assert -----------------------------------------------------------------
    mock_io_util.get_input.assert_has_calls(expected_calls)
    assert anlys_eng._bounds == expected_bounds


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
