"""Integration test suite for ChamberAccess."""

from datetime import datetime
from decimal import Decimal

import pytest
from dacite import from_dict
from sqlalchemy.orm import sessionmaker

from chamber.access.sql.service import ChamberAccess
from chamber.access.sql.models import Experiment, Observation, Pool
from chamber.access.sql.models import Setting, Temperature
from chamber.access.sql.contracts import ExperimentSpec, ObservationSpec
from chamber.access.sql.contracts import PoolSpec, SettingSpec, TemperatureSpec


# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture('module')
def access():
    """Chamber access fixture."""
    access = ChamberAccess()
    yield access
    access.teardown()


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


# _add_pool -------------------------------------------------------------------


def test_add_pool_that_does_not_exist(access, pool_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    pool_id = access._add_pool(pool_spec)
    # Assert -----------------------------------------------------------------
    assert pool_id == 1
    # Now query result -------------------------------------------------------
    session = access.Session()
    try:
        query = session.query(Pool).filter(Pool.material == 'test_material')
        result = query.one()
        session.commit()
        assert result.inner_diameter == Decimal('0.1000')
        assert result.outer_diameter == Decimal('0.2000')
        assert result.height == Decimal('0.3000')
        assert result.mass == Decimal('0.4000000')
    finally:
        session.close()


def test_add_pool_that_already_exists(access, pool_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the pool
    # NOTE: These tests are intended to be run sequently
    access._add_pool(pool_spec)
    # Act --------------------------------------------------------------------
    new_pool_id = access._add_pool(pool_spec)
    # Assert -----------------------------------------------------------------
    assert new_pool_id == 1

# _add_setting ----------------------------------------------------------------


def test_add_setting_that_does_not_exist(access, setting_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    setting_id = access._add_setting(setting_spec)
    # Assert -----------------------------------------------------------------
    assert setting_id == 1
    # Now query result -------------------------------------------------------
    session = access.Session()
    try:
        query = session.query(Setting)
        query = query.filter(Setting.pressure == setting_spec.pressure)
        result = query.one()
        session.commit()
        assert result.duty == Decimal('0.0')
        assert result.temperature == Decimal('290.0')
        assert result.time_step == Decimal('1.0')
    finally:
        session.close()


def test_add_setting_that_already_exists(access, setting_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the setting
    # NOTE: These tests are intended to be run sequently
    access._add_setting(setting_spec)
    # Act --------------------------------------------------------------------
    new_setting_id = access._add_setting(setting_spec)
    # Assert -----------------------------------------------------------------
    assert new_setting_id == 1


# _add_experiment -------------------------------------------------------------


def test_add_experiment_that_does_not_exist(access, experiment_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    experiment_id = access._add_experiment(experiment_spec)
    # Assert -----------------------------------------------------------------
    assert experiment_id == 1
    # Now query result -------------------------------------------------------
    session = access.Session()
    try:
        query = session.query(Experiment)
        query = query.filter(Experiment.datetime == experiment_spec.datetime)
        result = query.one()
        session.commit()
        assert result.author == 'RHI'
        assert result.description == 'The description is descriptive.'
        assert result.pool_id == 1
        assert result.setting_id == 1
    finally:
        session.close()


def test_add_experiment_that_already_exists(access, experiment_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the experiment
    # NOTE: These tests are intended to be run sequently
    access._add_experiment(experiment_spec)
    # Act --------------------------------------------------------------------
    new_experiment_id = access._add_experiment(experiment_spec)
    # Assert -----------------------------------------------------------------
    assert new_experiment_id == 1


# _add_observations -----------------------------------------------------------


def test_add_observations_that_do_not_exist(access, observation_specs):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    experiment_id = 1
    #  Act --------------------------------------------------------------------
    returned_experiment_id = access._add_observations(observation_specs, experiment_id)
    # Assert -----------------------------------------------------------------
    assert returned_experiment_id == experiment_id
    # Now query result -------------------------------------------------------
    session = access.Session()
    try:
        query = session.query(Observation)
        query = query.filter(Observation.experiment_id == experiment_id)
        observations = query.all()
        for observation in observations:
            if observation.idx == 0:
                assert observation.cap_man_ok
                assert observation.dew_point == Decimal('280.12')
                assert observation.idx == 0
                assert observation.mass == Decimal('0.1234567')
                assert observation.optidew_ok
                assert observation.pow_out == 0
                assert observation.pow_ref == 0
                assert observation.pressure == 987654
            elif observation.idx == 1:
                assert not observation.cap_man_ok
                assert observation.dew_point == Decimal('280.20')
                assert observation.idx == 1
                assert observation.mass == Decimal('0.1222222')
                assert not observation.optidew_ok
                assert observation.pow_out == 0
                assert observation.pow_ref == 0
                assert observation.pressure == 987000
        query = session.query(Temperature)
        temperatures = query.filter(Temperature.experiment_id == experiment_id)
        for temperature in temperatures:
            if temperature.idx == 0:
                if temperature.thermocouple_num == 0:
                    assert temperature.temperature == Decimal('300.0')
                elif temperature.thermocouple_num == 1:
                    assert temperature.temperature == Decimal('300.2')
                elif temperature.thermocouple_num == 2:
                    assert temperature.temperature == Decimal('300.4')
            elif temperature.idx == 1:
                if temperature.thermocouple_num == 0:
                    assert temperature.temperature == Decimal('301.0')
                elif temperature.thermocouple_num == 1:
                    assert temperature.temperature == Decimal('301.2')
                elif temperature.thermocouple_num == 2:
                    assert temperature.temperature == Decimal('301.4')
        session.commit()
    finally:
        session.close()


def test_add_observations_that_already_exist(access, observation_specs):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the observations
    # NOTE: These tests are intended to be run sequently
    experiment_id = 1
    # Act --------------------------------------------------------------------
    returned_experiment_id = access._add_observations(observation_specs, experiment_id)
    # Assert -----------------------------------------------------------------
    assert returned_experiment_id == experiment_id
