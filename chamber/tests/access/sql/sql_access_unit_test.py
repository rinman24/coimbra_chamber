"""Unit test suite for ChamberAccess."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import call, MagicMock

import pytest
from dacite import from_dict

from chamber.access.sql.service import ChamberAccess
from chamber.access.sql.models import Experiment, Observation, Pool
from chamber.access.sql.models import Setting, Temperature
from chamber.access.sql.contracts import ExperimentSpec, DataSpec, ObservationSpec
from chamber.access.sql.contracts import PoolSpec, SettingSpec, TemperatureSpec


# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture('function')
def access_mock(monkeypatch):
    """Mock of ChamberAccess fixture."""
    access_mock = MagicMock()
    # _add_pool
    access_mock._add_pool = MagicMock(return_value=1)
    monkeypatch.setattr(
        'chamber.access.sql.service.ChamberAccess._add_pool',
        access_mock._add_pool)
    # _add_setting
    access_mock._add_setting = MagicMock(return_value=1)
    monkeypatch.setattr(
        'chamber.access.sql.service.ChamberAccess._add_setting',
        access_mock._add_setting)
    # _add_experiment
    access_mock._add_experiment = MagicMock(return_value=1)
    monkeypatch.setattr(
        'chamber.access.sql.service.ChamberAccess._add_experiment',
        access_mock._add_experiment)
    # _add_observations
    return_value = dict(observations=2, temperatures=6)
    access_mock._add_observations = MagicMock(return_value=return_value)
    monkeypatch.setattr(
        'chamber.access.sql.service.ChamberAccess._add_observations',
        access_mock._add_observations)

    return access_mock


@pytest.fixture('module')
def access():
    """Chamber access fixture."""
    access = ChamberAccess()
    yield access
    access._teardown()


@pytest.fixture('module')
def pool_spec():
    """Pool specification."""
    data = dict(
        inner_diameter=Decimal('0.1'), outer_diameter=Decimal('0.2'),
        height=Decimal('0.3'), material='test_material', mass=Decimal('0.4'))
    pool_spec = from_dict(PoolSpec, data)
    return pool_spec


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
        pool_id=1,
        setting_id=1)
    experiment_spec = from_dict(ExperimentSpec, data)
    return experiment_spec


@pytest.fixture('module')
def observation_specs():
    """Observation specifications including temperatures."""
    # Now create a list of DTOs
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
        temperatures=[idx0_tc0, idx0_tc1, idx0_tc2])
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
        temperatures=[idx1_tc0, idx1_tc1, idx1_tc2])
    idx_1 = from_dict(ObservationSpec, data)
    # Now that we have the data we can construct a list of observations
    observation_specs = [idx_0, idx_1]

    return observation_specs


# ----------------------------------------------------------------------------
# ChamberAccess


# add_data -------------------------------------------------------------------


def test_add_data(
        pool_spec, setting_spec, experiment_spec, observation_specs, access,
        access_mock):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(
        pool=pool_spec,
        setting=setting_spec,
        experiment=experiment_spec,
        observations=observation_specs)
    data_specs = from_dict(DataSpec, data)
    correct_calls = [
        call._add_pool(pool_spec),
        call._add_setting(setting_spec),
        call._add_experiment(experiment_spec),
        call._add_observations(observation_specs, 1)
        ]
    # Act --------------------------------------------------------------------
    result = access.add_data(data_specs)
    # Assert -----------------------------------------------------------------
    assert result['pool_id'] == 1
    assert result['setting_id'] == 1
    assert result['experiment_id'] == 1
    assert result['observations'] == 2
    assert result['temperatures'] == 6

    access_mock.assert_has_calls(correct_calls)
