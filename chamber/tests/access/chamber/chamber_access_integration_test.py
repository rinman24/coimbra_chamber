"""Integration test suite for ExperimentalAccess."""

from datetime import datetime
from decimal import Decimal

import pytest
from dacite import from_dict
from sqlalchemy.orm import sessionmaker

from chamber.access.chamber.service import ExperimentalAccess
from chamber.access.chamber.models import Experiment, Pool, Setting
from chamber.access.chamber.contracts import PoolSpec, SettingSpec, ExperimentSpec

# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture('module')
def access():
    """Experimental access fixture."""
    access = ExperimentalAccess()
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
    """Setting specifications."""
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


# ----------------------------------------------------------------------------
# ExperimentalAccess


# add_pool -------------------------------------------------------------------


def test_add_pool_that_does_not_exist(access, pool_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    pool_id = access.add_pool(pool_spec)
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
    access.add_pool(pool_spec)
    # Act --------------------------------------------------------------------
    new_pool_id = access.add_pool(pool_spec)
    # Assert -----------------------------------------------------------------
    assert new_pool_id == 1
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


# add_setting ----------------------------------------------------------------


def test_add_setting_that_does_not_exist(access, setting_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    setting_id = access.add_setting(setting_spec)
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
    access.add_setting(setting_spec)
    # Act --------------------------------------------------------------------
    new_setting_id = access.add_setting(setting_spec)
    # Assert -----------------------------------------------------------------
    assert new_setting_id == 1
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


# add_experiment -------------------------------------------------------------

def test_add_experiment_that_does_not_exist(
        access, experiment_spec, pool_spec, setting_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    access.add_pool(pool_spec)
    access.add_setting(setting_spec)
    # Act --------------------------------------------------------------------
    experiment_id = access.add_experiment(experiment_spec)
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


def test_add_experiment_that_already_exists(
        access, experiment_spec, pool_spec, setting_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    access.add_pool(pool_spec)
    access.add_setting(setting_spec)
    access.add_experiment(experiment_spec)
    # Act --------------------------------------------------------------------
    new_experiment_id = access.add_experiment(experiment_spec)
    # Assert -----------------------------------------------------------------
    assert new_experiment_id == 1
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
