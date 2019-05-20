"""Test fixtures."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest
from dacite import from_dict
from nptdms import TdmsFile

from chamber.access.sql.service import ChamberAccess
from chamber.access.sql.contracts import DataSpec, ExperimentSpec, ObservationSpec
from chamber.access.sql.contracts import TubeSpec, SettingSpec, TemperatureSpec
from chamber.access.tdms.service import TdmsAccess


# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture('module')
def chamber_access():
    """Chamber access fixture."""
    chamber_access = ChamberAccess()
    yield chamber_access
    chamber_access._teardown()


@pytest.fixture('module')
def tdms_access():
    """Tdms access fixture."""
    tdms_access = TdmsAccess()
    return tdms_access


@pytest.fixture('module')
def tube_spec():
    """Tube specification."""
    data = dict(
        inner_diameter=Decimal('0.1'), outer_diameter=Decimal('0.2'),
        height=Decimal('0.3'), material='test_material', mass=Decimal('0.4'))
    tube_spec = from_dict(TubeSpec, data)
    return tube_spec


@pytest.fixture('module')
def setting_spec():
    """Set the Setting specifications."""
    data = dict(
        duty=Decimal('0.0'), pressure=99000, temperature=Decimal(290),
        time_step=Decimal('1.0'))
    setting_spec = from_dict(SettingSpec, data)
    return setting_spec


@pytest.fixture('module')
def experiment_spec():
    """Experiment specification."""
    data = dict(
        author='RHI',
        datetime=datetime(2019, 9, 24, 7, 45, 0),
        description='The description is descriptive.',
        tube_id=1)
    experiment_spec = from_dict(ExperimentSpec, data)
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
    idx0_tc0 = from_dict(TemperatureSpec, data)
    # Idx = 0; TC = 1
    data = dict(
        thermocouple_num=1,
        temperature=Decimal('300.2'),
        idx=0)
    idx0_tc1 = from_dict(TemperatureSpec, data)
    # Idx = 0; TC = 2
    data = dict(
        thermocouple_num=2,
        temperature=Decimal('300.4'),
        idx=0)
    idx0_tc2 = from_dict(TemperatureSpec, data)
    # Idx = 1; TC = 0
    data = dict(
        thermocouple_num=0,
        temperature=Decimal('301.0'),
        idx=1)
    idx1_tc0 = from_dict(TemperatureSpec, data)
    # Idx = 1; TC = 1
    data = dict(
        thermocouple_num=1,
        temperature=Decimal('301.2'),
        idx=1)
    idx1_tc1 = from_dict(TemperatureSpec, data)
    # Idx = 1; TC = 2
    data = dict(
        thermocouple_num=2,
        temperature=Decimal('301.4'),
        idx=1)
    idx1_tc2 = from_dict(TemperatureSpec, data)
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
        surface_temp=Decimal('280.0'))
    idx_0 = from_dict(ObservationSpec, data)
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
        surface_temp=Decimal('280.2'))
    idx_1 = from_dict(ObservationSpec, data)
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
    data_spec = from_dict(DataSpec, data)
    return data_spec
