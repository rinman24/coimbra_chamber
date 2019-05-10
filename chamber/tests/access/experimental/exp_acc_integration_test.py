"""Integration test suite for ExperimentalAccess."""

from decimal import Decimal

import pytest
from dacite import from_dict
from sqlalchemy.orm import sessionmaker

from chamber.access.experimental.service import ExperimentalAccess
from chamber.access.experimental.models import Pool
from chamber.access.experimental.contracts import PoolSpecs
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
# Scenario Access

def test_add_tube_that_does_not_exist_in_database(mysql):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Create the pool to be added to database
    data = dict(
        inner_diameter=Decimal('0.1'), outer_diameter=Decimal('0.2'),
        height=Decimal('0.3'), material='test_material', mass=Decimal('0.4'))
    my_pool = from_dict(PoolSpecs, data)
    # Act --------------------------------------------------------------------
    access = ExperimentalAccess()
    pool_id = access.add_pool(my_pool)
    # Assert -----------------------------------------------------------------
    assert pool_id == 2  # pool_id == 2 because mysql fixture added a tube
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
