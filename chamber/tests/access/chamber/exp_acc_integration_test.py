"""Integration test suite for ExperimentalAccess."""

from decimal import Decimal

import pytest
from dacite import from_dict
from sqlalchemy.orm import sessionmaker

from chamber.access.chamber.service import ExperimentalAccess
from chamber.access.chamber.models import Pool, Setting
from chamber.access.chamber.contracts import PoolSpec, SettingSpec
from chamber.ifx.testing import MySQLTestHelper

# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture('module')
def mysql(request):
    """Set up and tear down for sql server resources."""
    client = MySQLTestHelper()

    client.run_script('experiment_test_data.sql')

    yield client

    client.clear_db()


# ----------------------------------------------------------------------------
# ExperimentalAccess


# add_pool -------------------------------------------------------------------


def test_add_pool_that_already_exist_in_database(mysql):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # The fixture has already added a pool when it ran the experiment test
    # data sql script. See script for details.
    data = dict(
        inner_diameter=Decimal('0.03'), outer_diameter=Decimal('0.04'),
        height=Decimal('0.06'), material='Delrin', mass=Decimal('0.05678'))
    my_pool = from_dict(PoolSpec, data)
    # Act --------------------------------------------------------------------
    access = ExperimentalAccess()
    pool_id = access.add_pool(my_pool)
    # Assert -----------------------------------------------------------------
    assert pool_id == 1


def test_add_pool_that_does_not_exist_in_database(mysql):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Create the pool to be added to database
    data = dict(
        inner_diameter=Decimal('0.1'), outer_diameter=Decimal('0.2'),
        height=Decimal('0.3'), material='test_material', mass=Decimal('0.4'))
    my_pool = from_dict(PoolSpec, data)
    # Act --------------------------------------------------------------------
    access = ExperimentalAccess()
    pool_id = access.add_pool(my_pool)
    # Assert -----------------------------------------------------------------
    # pool_id == 2 because mysql fixture added a pool
    assert pool_id == 2
    # Prepare query
    Session = sessionmaker(bind=access.engine)
    session = Session()
    query = session.query(Pool).filter(Pool.material == 'test_material')
    try:
        result = query.one()
        assert result.inner_diameter == Decimal('0.1000')
        assert result.outer_diameter == Decimal('0.2000')
        assert result.height == Decimal('0.3000')
        assert result.material == 'test_material'
        assert result.mass == Decimal('0.4000000')
    finally:
        session.close()
    # Cleanup ----------------------------------------------------------------
    session.delete(result)
    session.commit()
    assert not query.first()
    session.close()


# add_setting ----------------------------------------------------------------


def test_add_setting_that_already_exist_in_database(mysql):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # The fixture has already added a setting when it ran the experiment test
    # data sql script. See script for details.
    data = dict(
        duty=Decimal('0.0'), pressure=101325, temperature=Decimal('300.0'),
        time_step=Decimal('1.0'))
    my_setting = from_dict(SettingSpec, data)
    # Act --------------------------------------------------------------------
    access = ExperimentalAccess()
    setting_id = access.add_setting(my_setting)
    # Assert -----------------------------------------------------------------
    assert setting_id == 1


def test_add_setting_that_does_not_exist_in_database(mysql):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Create the setting to be added to database
    data = dict(
        duty=Decimal('0.0'), pressure=99000, temperature=Decimal(290),
        time_step=Decimal('1.0'))
    my_setting = from_dict(SettingSpec, data)
    # Act --------------------------------------------------------------------
    access = ExperimentalAccess()
    setting_id = access.add_setting(my_setting)
    # Assert -----------------------------------------------------------------
    # setting_id == 2 because mysql fixture added a setting
    assert setting_id == 2
    # Prepare query
    Session = sessionmaker(bind=access.engine)
    session = Session()
    query = session.query(Setting).filter(Setting.pressure == 99000)
    try:
        result = query.one()
        assert result.duty == Decimal('0.0')
        assert result.pressure == 99000
        assert result.temperature == Decimal('290.0')
        assert result.time_step == Decimal('1.00')
    finally:
        session.close()
    # Cleanup ----------------------------------------------------------------
    session.delete(result)
    session.commit()
    assert not query.first()
    session.close()
