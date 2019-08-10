"""Test fixtures and constants."""

import datetime
from decimal import Decimal
from math import sqrt
from pathlib import Path
import pickle
from unittest.mock import MagicMock

import dacite
import pytest
from nptdms import TdmsFile

from chamber.access.experiment.contracts import (
    DataSpec,
    ExperimentSpec,
    FitSpec,
    ObservationSpec,
    TubeSpec,
    SettingSpec,
    TemperatureSpec)
from chamber.access.experiment.service import ExperimentAccess

from chamber.engine.analysis.service import AnalysisEngine

from chamber.utility.plot.contracts import (
    Axis,
    DataSeries,
    Layout,
    Plot)

# ----------------------------------------------------------------------------
# Constants


tdms_path = Path('chamber/tests/access/experiment/test_1.tdms')


# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture('module')
def exp_acc():
    """Experiment access fixture."""
    access = ExperimentAccess()
    yield access
    access._teardown()


@pytest.fixture('function')
def mock_io_util(monkeypatch):
    """Mock of IOUtility."""
    util = MagicMock()

    monkeypatch.setattr(
        'chamber.utility.io.service.IOUtility.get_input',
        util.get_input
    )

    return util


@pytest.fixture(scope='function')
def anlys_eng(exp_acc, monkeypatch):
    """
    Create a function level instance of the analysis engine.

    NOTE: For unit testing when we want a new instance each time.
    """
    engine = AnalysisEngine(experiment_id=1)
    engine._exp_acc = exp_acc

    # This instance of the AnalysisEngine has the get_raw_data method of its
    # instance of ExperimentAccess mocked to return a previously serialized
    # instance of a DataSpec dataclass. This dramatically speeds up loading
    # the data for testing.
    path = Path('chamber/tests/access/experiment/sample_data')
    with open(path, 'rb') as stream:
        data = pickle.load(stream)
    # Now that we have data, we want to make a mock that will return it.
    mock_get_raw_data = MagicMock(return_value=data)
    monkeypatch.setattr(
        'chamber.access.experiment.service.ExperimentAccess.get_raw_data',
        mock_get_raw_data)

    # This instance also has the plot method of its instance of PlotUtility
    # mocked to return and do nothing.
    mock_plot = MagicMock()
    monkeypatch.setattr(
        'chamber.utility.plot.service.PlotUtility.plot',
        mock_plot)

    return engine


@pytest.fixture('module')
def tube_spec():
    """Tube specification."""
    data = dict(
        inner_diameter=Decimal('0.1'), outer_diameter=Decimal('0.2'),
        height=Decimal('0.3'), material='test_material', mass=Decimal('0.4'))
    tube_spec = dacite.from_dict(TubeSpec, data)
    return tube_spec


@pytest.fixture('module')
def setting_spec():
    """Set the Setting specifications."""
    data = dict(
        duty=Decimal('0.0'), pressure=99000, temperature=Decimal(290),
        time_step=Decimal('1.0'))
    setting_spec = dacite.from_dict(SettingSpec, data)
    return setting_spec


@pytest.fixture('module')
def experiment_spec():
    """Experiment specification."""
    data = dict(
        author='RHI',
        datetime=datetime.datetime(2019, 9, 24, 7, 45, 0),
        description='The description is descriptive.',
        tube_id=1)
    experiment_spec = dacite.from_dict(ExperimentSpec, data)
    return experiment_spec


@pytest.fixture('module')
def observation_spec():
    """Observation specifications including temperatures."""
    # Create a list of DTOs
    # This will consist of two timesteps and three thermocouples
    # First temperatures -----------------------------------------------------
    # Idx = 0; TC = 0
    data = dict(
        thermocouple_num=0,
        temperature=Decimal('300.0'),
        idx=0)
    idx0_tc0 = dacite.from_dict(TemperatureSpec, data)
    # Idx = 0; TC = 1
    data = dict(
        thermocouple_num=1,
        temperature=Decimal('300.2'),
        idx=0)
    idx0_tc1 = dacite.from_dict(TemperatureSpec, data)
    # Idx = 0; TC = 2
    data = dict(
        thermocouple_num=2,
        temperature=Decimal('300.4'),
        idx=0)
    idx0_tc2 = dacite.from_dict(TemperatureSpec, data)
    # Idx = 1; TC = 0
    data = dict(
        thermocouple_num=0,
        temperature=Decimal('301.0'),
        idx=1)
    idx1_tc0 = dacite.from_dict(TemperatureSpec, data)
    # Idx = 1; TC = 1
    data = dict(
        thermocouple_num=1,
        temperature=Decimal('301.2'),
        idx=1)
    idx1_tc1 = dacite.from_dict(TemperatureSpec, data)
    # Idx = 1; TC = 2
    data = dict(
        thermocouple_num=2,
        temperature=Decimal('301.4'),
        idx=1)
    idx1_tc2 = dacite.from_dict(TemperatureSpec, data)
    # Then observations ------------------------------------------------------
    # Idx = 0
    data = dict(
        cap_man_ok=True,
        dew_point=Decimal('280.123456789'),
        idx=0,
        mass=Decimal('0.1234567'),
        optidew_ok=True,
        pow_out=Decimal('0.0'),
        pow_ref=Decimal('0.0'),
        pressure=987654,
        temperatures=[idx0_tc0, idx0_tc1, idx0_tc2],
        surface_temp=Decimal('290.0'),
        ic_temp=Decimal('291.0'))
    idx_0 = dacite.from_dict(ObservationSpec, data)
    # Idx = 1
    data = dict(
        cap_man_ok=False,
        dew_point=Decimal('280.2'),
        idx=1,
        mass=Decimal('0.1222222'),
        optidew_ok=False,
        pow_out=Decimal('0.0'),
        pow_ref=Decimal('0.0'),
        pressure=987000,
        temperatures=[idx1_tc0, idx1_tc1, idx1_tc2],
        surface_temp=Decimal('290.2'),
        ic_temp=Decimal('291.2'))
    idx_1 = dacite.from_dict(ObservationSpec, data)
    # Now that we have the data we can construct a list of observations
    observation_spec = [idx_0, idx_1]

    return observation_spec


@pytest.fixture('function')
def data_spec(setting_spec, experiment_spec, observation_spec):
    """Return data specification for an entire experiment."""
    data = dict(
        setting=setting_spec,
        experiment=experiment_spec,
        observations=observation_spec)
    data_spec = dacite.from_dict(DataSpec, data)
    return data_spec


@pytest.fixture('function')
def raw_layout():
    """Create a raw data layout."""
    # First the DataSeries ---------------------------------------------------
    data_series = dict()

    # Idx
    data = {'values': [1, 2, 3]}
    data_series['idx'] = dacite.from_dict(DataSeries, data)

    # Mass
    data = dict(
        values=[Decimal('0.0129683'), Decimal('0.0129682'), Decimal('0.0129682')],
        label='mass')
    data_series['mass'] = dacite.from_dict(DataSeries, data)

    # Thermocouples
    data = dict(
        values=[Decimal('290.21'), Decimal('290.23'), Decimal('290.23')],
        label='TC-4')
    data_series['TC4'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('289.9'), Decimal('289.9'), Decimal('289.91')],
        label='TC-5')
    data_series['TC5'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('289.88'), Decimal('289.89'), Decimal('289.9')],
        label='TC-6')
    data_series['TC6'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('290.21'), Decimal('290.23'), Decimal('290.23')],
        label='TC-7')
    data_series['TC7'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('290.21'), Decimal('290.22'), Decimal('290.23')],
        label='TC-8')
    data_series['TC8'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('289.82'), Decimal('289.83'), Decimal('289.84')],
        label='TC-9')
    data_series['TC9'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('289.72'), Decimal('289.73'), Decimal('289.74')],
        label='TC-10')
    data_series['TC10'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('289.91'), Decimal('289.92'), Decimal('289.93')],
        label='TC-11')
    data_series['TC11'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('289.7'), Decimal('289.72'), Decimal('289.73')],
        label='TC-12')
    data_series['TC12'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('290.1'), Decimal('290.11'), Decimal('290.11')],
        label='TC-13')
    data_series['TC13'] = dacite.from_dict(DataSeries, data)

    # Dew point
    data = dict(
        values=[Decimal('284.29'), Decimal('284.3'), Decimal('284.3')],
        label='dew point')
    data_series['dew point'] = dacite.from_dict(DataSeries, data)

    # Surface temp
    data = dict(
        values=[Decimal('291.34'), Decimal('291.3'), Decimal('291.22')],
        label='surface temp')
    data_series['surface temp'] = dacite.from_dict(DataSeries, data)

    # IC temp
    data = dict(
        values=[Decimal('294.86'), Decimal('294.86'), Decimal('294.86')],
        label='IC temp')
    data_series['ic temp'] = dacite.from_dict(DataSeries, data)

    # Pressure
    data = dict(
        values=[99732, 99749, 99727],
        label='pressure')
    data_series['pressure'] = dacite.from_dict(DataSeries, data)

    # Now the Axis -----------------------------------------------------------
    axes = dict()

    data = dict(data=[data_series['mass']], y_label='mass, [kg]')
    axes['mass'] = dacite.from_dict(Axis, data)

    data = dict(
        data=[data_series['TC4'], data_series['TC5'], data_series['TC6'],
              data_series['TC7'], data_series['TC8'], data_series['TC9'],
              data_series['TC10'], data_series['TC11'], data_series['TC12'],
              data_series['TC13'], data_series['dew point'],
              data_series['surface temp'], data_series['ic temp']],
        y_label='temperature, [K]')
    axes['temp'] = dacite.from_dict(Axis, data)

    data = dict(data=[data_series['pressure']], y_label='pressure, [Pa]')
    axes['pressure'] = dacite.from_dict(Axis, data)

    # Then the Plots ---------------------------------------------------------
    plots = dict()

    data = dict(
        abscissa=data_series['idx'],
        axes=[axes['mass'], axes['temp']],
        x_label='index', legend=False)
    plots['mass_and_temp'] = dacite.from_dict(Plot, data)

    data = dict(
        abscissa=data_series['idx'],
        axes=[axes['pressure']],
        x_label='index')
    plots['pressure'] = dacite.from_dict(Plot, data)

    # Finally, the layout ----------------------------------------------------
    data = dict(
        plots=[plots['mass_and_temp'], plots['pressure']],
        style='seaborn-darkgrid')

    return dacite.from_dict(Layout, data)


@pytest.fixture('function')
def fit_spec():
    """Fit specification."""
    data = dict(
        a=1.0,
        sig_a=2.0,
        b=-3.0,
        sig_b=4.0,
        r2=5.0,
        q=6.0,
        chi2=7.0,
        nu_chi=8,
        exp_id=1,
        idx=0,
        mddp=9.0,
        sig_mddp=9.1,
        x1s=10.0,
        sig_x1s=10.1,
        x1e=11.0,
        sig_x1e=11.1,
        x1=12.0,
        sig_x1=12.1,
        m1s=13.0,
        sig_m1s=13.1,
        m1e=14.0,
        sig_m1e=14.1,
        m1=15.0,
        sig_m1=15.1,
        rhos=16.0,
        sig_rhos=16.1,
        rhoe=17.0,
        sig_rhoe=17.1,
        rho=18.0,
        sig_rho=18.1,
        Bm1=19.0,
        sig_Bm1=19.1,
        T=20.0,
        sig_T=20.1,
        D12=21.0,
        sig_D12=21.1,
        hfg=22.0,
        sig_hfg=22.1,
        hu=23.0,
        sig_hu=23.1,
        hs=24.0,
        sig_hs=24.1,
        cpv=25.0,
        sig_cpv=25.1,
        he=26.0,
        sig_he=26.1,
        cpl=27.0,
        sig_cpl=27.1,
        hT=28.0,
        sig_hT=28.1,
        qcu=29.0,
        sig_qcu=29.1,
        Ebe=30.0,
        sig_Ebe=30.1,
        Ebs=31.0,
        sig_Ebs=31.1,
        qrs=32.0,
        sig_qrs=32.1,
        kv=33.0,
        sig_kv=33.1,
        alpha=34.0,
        sig_alpha=34.1,
        Bh=35.0,
        sig_Bh=35.1,
        M=36.0,
        sig_M=36.1,
        gamma1=37.0,
        sig_gamma1=37.1,
        beta=38.0,
        sig_beta=38.1,
        Delta_m=39.0,
        sig_Delta_m=39.1,
        Delta_T=40.0,
        sig_Delta_T=40.1,
        mu=41.0,
        sig_mu=41.1,
        nu=42.0,
        sig_nu=42.1,
        gamma2=43.0,
        sig_gamma2=43.1,
    )
    fit_spec = dacite.from_dict(FitSpec, data)
    return fit_spec
