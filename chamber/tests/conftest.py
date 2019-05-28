"""Test fixtures and constants."""

import datetime
from decimal import Decimal
from pathlib import Path

import dacite
import pytest
from nptdms import TdmsFile

from chamber.access.experiment.contracts import (
    DataSpec,
    ExperimentSpec,
    ObservationSpec,
    TubeSpec,
    SettingSpec,
    TemperatureSpec)
from chamber.access.experiment.service import ExperimentAccess

from chamber.utility.plot.contracts import (
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
        surface_temp=Decimal('290.0'))
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
        surface_temp=Decimal('290.2'))
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
    """Create a dictionary of DataSeries contracts."""
    # First the DataSeries ---------------------------------------------------
    data_series = dict()

    # Idx
    data = dict(
        values=[1, 2, 3],
        sigma=[0, 0, 0])
    data_series['idx'] = dacite.from_dict(DataSeries, data)

    # Mass
    data = dict(
        values=[Decimal('0.0118974'), Decimal('0.0118974'), Decimal('0.0118974')],
        sigma=[0, 0, 0],
        label='mass')
    data_series['mass'] = dacite.from_dict(DataSeries, data)

    # Thermocouples
    data = dict(
        values=[Decimal('296.58'), Decimal('296.58'), Decimal('296.58')],
        sigma=[0, 0, 0],
        label='TC-4')
    data_series['TC4'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('297.33'), Decimal('297.32'), Decimal('297.32')],
        sigma=[0, 0, 0],
        label='TC-5')
    data_series['TC5'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('297.08'), Decimal('297.09'), Decimal('297.07')],
        sigma=[0, 0, 0],
        label='TC-6')
    data_series['TC6'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('296.46'), Decimal('296.45'), Decimal('296.45')],
        sigma=[0, 0, 0],
        label='TC-7')
    data_series['TC7'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('297.08'), Decimal('297.08'), Decimal('297.08')],
        sigma=[0, 0, 0],
        label='TC-8')
    data_series['TC8'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('297.03'), Decimal('297.03'), Decimal('297.02')],
        sigma=[0, 0, 0],
        label='TC-9')
    data_series['TC9'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('297.66'), Decimal('297.65'), Decimal('297.65')],
        sigma=[0, 0, 0],
        label='TC-10')
    data_series['TC10'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('296.59'), Decimal('296.58'), Decimal('296.57')],
        sigma=[0, 0, 0],
        label='TC-11')
    data_series['TC11'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('297.42'), Decimal('297.42'), Decimal('297.42')],
        sigma=[0, 0, 0],
        label='TC-12')
    data_series['TC12'] = dacite.from_dict(DataSeries, data)

    data = dict(
        values=[Decimal('296.36'), Decimal('296.36'), Decimal('296.36')],
        sigma=[0, 0, 0],
        label='TC-13')
    data_series['TC13'] = dacite.from_dict(DataSeries, data)

    # Dew point
    data = dict(
        values=[Decimal('286.43'), Decimal('286.41'), Decimal('286.46')],
        sigma=[0, 0, 0],
        label='dew point')
    data_series['dew point'] = dacite.from_dict(DataSeries, data)

    # Surface temp
    data = dict(
        values=[Decimal('296.02'), Decimal('295.92'), Decimal('295.82')],
        sigma=[0, 0, 0],
        label='surface temp')
    data_series['surface temp'] = dacite.from_dict(DataSeries, data)

    # Pressure
    data = dict(
        values=[100025, 99981, 100016],
        sigma=[0, 0, 0],
        label='pressure')
    data_series['pressure'] = dacite.from_dict(DataSeries, data)

    # Then the Plots ---------------------------------------------------------
    plots = dict()

    data = dict(
        abscissae=[data_series['idx']],
        ordinates=[data_series['mass']],
        title='Mass with time',
        x_label='time, [s]',
        y_label='mass, [kg]')
    plots['mass'] = dacite.from_dict(Plot, data)

    data = dict(
        abscissae=[data_series['idx']] * 12,
        ordinates=[
            data_series['TC4'], data_series['TC5'], data_series['TC6'],
            data_series['TC7'], data_series['TC8'], data_series['TC9'],
            data_series['TC10'], data_series['TC11'], data_series['TC12'],
            data_series['TC13'], data_series['dew point'],
            data_series['surface temp']],
        title='Temperature with time',
        x_label='time, [s]',
        y_label='temperature, [K]')
    plots['temperature'] = dacite.from_dict(Plot, data)

    data = dict(
        abscissae=[data_series['idx']],
        ordinates=[data_series['pressure']],
        title='Pressure with time',
        x_label='time, [s]',
        y_label='pressure, [Pa]')
    plots['pressure'] = dacite.from_dict(Plot, data)

    # Finally, the layout ----------------------------------------------------
    data = dict(
        plots=[plots['mass'], plots['temperature'], plots['pressure']],
        style='seaborn-darkgrid')
    return dacite.from_dict(Layout, data)
