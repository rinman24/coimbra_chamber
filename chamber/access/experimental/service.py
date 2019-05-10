"""Module encapsulates access to experimental data."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from chamber.access.experimental.models import Pool
from chamber.ifx.configuration import get_value


class ExperimentalAccess(object):
    """
    Encapsulates all aspects of data access for an experiment.

    Attributes
    ----------
    engine : sqlalchemy.engine.base.Engine
        The engine used to create sessions with the database.

    """

    def __init__(self):
        """
        Create the SQLAlchemy engine for the MySQL database.

        Examples
        --------
        >>> from chamber.access.experimental.service import ExperimentalAccess
        >>> exp_acc = ExperimentalAccess()
        >>> exp_acc.engine
        Engine(mysql+mysqlconnector://root:***@127.0.0.1/experimental)

        """
        # Get server configuration
        host = get_value('host', 'MySQL-Server')
        database = get_value('database', 'MySQL-Server')
        user = get_value('user', 'MySQL-Server')
        password = get_value('password', 'MySQL-Server')

        # Create engine
        conn_string = f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'
        self.engine = create_engine(conn_string, echo=False)

    def add_pool(self, pool_spec):
        """
        Add a pool to the database.

        Parameters
        ----------
        pool_spec : chamber.access.experimental.models.Pool
            Specification for the pool to be added.

        Returns
        -------
        int
            Primary key for the pool that was added.

        Examples
        --------
        >>> from decimal import Decimal
        >>> from dacite import from_dict
        >>> from chamber.access.experimental.service import ExperimentalAccess
        >>> from chamber.access.experimental.contracts import PoolSpecs
        Specify the pool to add:
        >>> data = dict(
        ...     inner_diameter=Decimal('0.1'),
        ...     outer_diameter=Decimal('0.2'),
        ...     height=Decimal('0.3'),
        ...     material='Delrin',
        ...     mass=Decimal('0.4'))
        Use dacite to perform type checking:
        >>> pool_spec = from_dict(PoolSpecs, data)
        Finally, add the pool:
        >>> exp_acc = ExperimentalAccess()
        >>> pool_id = exp_acc.add_pool(pool_spec)
        >>> pool_id
        1

        """
        # Create session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Create pool
        pool_to_add = Pool(
            inner_diameter=pool_spec.inner_diameter,
            outer_diameter=pool_spec.outer_diameter,
            height=pool_spec.height,
            material=pool_spec.material,
            mass=pool_spec.mass)

        # Add pool
        session.add(pool_to_add)
        session.commit()

        # Get pool Id
        pool_id = pool_to_add.pool_id
        session.close()

        return pool_id
