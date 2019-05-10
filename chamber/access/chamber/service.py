"""Module encapsulates access to experimental data."""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from chamber.access.chamber.models import Experiment, Pool, Setting
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
        >>> from chamber.access.chamber.service import ExperimentalAccess
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
        Add a pool to the database and return its primary key.

        If the pool already exists in the database, no new pool is added and
        the primary key for the existing pool is returned.

        Parameters
        ----------
        pool_spec : chamber.access.chamber.models.PoolSpec
            Specification for the pool to be added.

        Returns
        -------
        int
            Primary key for the pool that was added.

        Examples
        --------
        >>> from decimal import Decimal
        >>> from dacite import from_dict
        >>> from chamber.access.chamber.service import ExperimentalAccess
        >>> from chamber.access.chamber.contracts import PoolSpec
        Specify the pool to add:
        >>> data = dict(
        ...     inner_diameter=Decimal('0.1'),
        ...     outer_diameter=Decimal('0.2'),
        ...     height=Decimal('0.3'),
        ...     material='Delrin',
        ...     mass=Decimal('0.4'))
        Use dacite to perform type checking:
        >>> pool_spec = from_dict(PoolSpec, data)
        Finally, add the pool:
        >>> exp_acc = ExperimentalAccess()
        >>> pool_id = exp_acc.add_pool(pool_spec)
        >>> pool_id
        1

        If we try to add the pool again, we get the same id:
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

        # Check if the pool exists
        query = session.query(Pool.pool_id).filter(
            and_(
                Pool.inner_diameter == pool_spec.inner_diameter,
                Pool.outer_diameter == pool_spec.outer_diameter,
                Pool.height == pool_spec.height,
                Pool.material == pool_spec.material,
                Pool.mass == pool_spec.mass
                )
            )
        pool_id = query.first()

        if pool_id:
            session.close()
            return pool_id[0]
        else:
            # Add pool
            session.add(pool_to_add)
            session.commit()

            # Get pool id
            pool_id = pool_to_add.pool_id
            session.close()

            return pool_id

    def add_setting(self, setting_spec):
        """
        Add a setting to the database and return its primary key.

        If the setting already exists in the database, no new setting is added
        and the primary key for the existing setting is returned.

        Parameters
        ----------
        setting_spec : chamber.access.chamber.models.SettingSpec
            Specification for the setting to be added.

        Returns
        -------
        int
            Primary key for the setting that was added.

        Examples
        --------
        >>> from decimal import Decimal
        >>> from dacite import from_dict
        >>> from chamber.access.chamber.service import ExperimentalAccess
        >>> from chamber.access.chamber.contracts import SettingSpec
        Specify the setting to add:
        >>> data = dict(
        ...     duty=Decimal('0.0'),
        ...     pressure=99000,
        ...     temperature=Decimal('290.0'),
        ...     time_stamp=Decimal('1.0'))
        Use dacite to perform type checking:
        >>> setting_spec = from_dict(SettingSpec, data)
        Finally, add the setting:
        >>> exp_acc = ExperimentalAccess()
        >>> setting_id = exp_acc.add_setting(setting_spec)
        >>> setting_id
        1

        If we try to add the setting again, we get the same id:
        >>> setting_id = exp_acc.add_setting(setting_spec)
        >>> setting_id
        1

        """
        # Create session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Create setting
        setting_to_add = Setting(
            duty=setting_spec.duty,
            pressure=setting_spec.pressure,
            temperature=setting_spec.temperature,
            time_step=setting_spec.time_step)

        # Check if the setting exists
        query = session.query(Setting.setting_id).filter(
            and_(
                Setting.duty == setting_spec.duty,
                Setting.pressure == setting_spec.pressure,
                Setting.temperature == setting_spec.temperature,
                Setting.time_step == setting_spec.time_step
                )
            )
        setting_id = query.first()

        if setting_id:
            session.close()
            return setting_id[0]
        else:
            # Add setting
            session.add(setting_to_add)
            session.commit()

            # Get setting id
            setting_id = setting_to_add.setting_id
            session.close()

            return setting_id

    def add_experiment(self, experiment_spec):
        """
        Add an experiment to the database and return its primary key.

        If the experiment already exists in the database, no new experiment is
        added and the primary key for the existing experiment is returned.

        Parameters
        ----------
        experiment_spec : chamber.access.chamber.models.ExperimentSpec
            Specification for the experiment to be added.

        Returns
        -------
        int
            Primary key for the experiment that was added.

        Examples
        --------
        >>> from decimal import Decimal
        >>> from dacite import from_dict
        >>> from datetime import datetime
        >>> from chamber.access.chamber.service import ExperimentalAccess
        >>> from chamber.access.chamber.contracts import ExperimentSpec
        Specify the experiment to add (assuming that the corresponding pool
        and setting exist):
        >>> data = dict(
        ...     author='RHI',
        ...     date_time=datetime.now(),
        ...     decsription='Tell me more about yourself.',
        ...     pool_id=1,
        ...     setting_id=1)
        Use dacite to perform type checking:
        >>> experiment_spec = from_dict(ExperimentSpec, data)
        Finally, add the experiment:
        >>> exp_acc = ExperimentalAccess()
        >>> experiment_id = exp_acc.add_experiment(experiment_spec)
        >>> experiment_id
        1

        If we try to add the experiment again, we get the same id:
        >>> experiment_id = exp_acc.add_experiment(experiment_spec)
        >>> experiment_id
        1

        """
        # Create session
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Create experiment
        experiment_to_add = Experiment(
            author=experiment_spec.author,
            date_time=experiment_spec.date_time,
            description=experiment_spec.description,
            pool_id=experiment_spec.pool_id,
            setting_id=experiment_spec.setting_id)

        # Check if the experiment exists
        query = session.query(Experiment.experiment_id)
        query = query.filter(Experiment.date_time == experiment_spec.date_time)
        experiment_id = query.first()

        if experiment_id:
            session.close()
            return experiment_id[0]
        else:
            # Add experiment
            session.add(experiment_to_add)
            session.commit()

            # Get experiment id
            experiment_id = experiment_to_add.experiment_id
            session.close()

            return experiment_id
