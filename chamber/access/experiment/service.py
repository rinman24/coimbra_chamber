"""Experiment access service."""


from decimal import Decimal

import dacite
from nptdms import TdmsFile
from sqlalchemy import and_, create_engine, func
from sqlalchemy.orm import sessionmaker

from chamber.access.experiment.models import (
    Base,
    Experiment,
    Fit,
    Observation,
    Tube,
    Setting,
    Temperature)
from chamber.access.experiment.contracts import (
    DataSpec,
    ExperimentSpec,
    ObservationSpec,
    SettingSpec,
    TemperatureSpec)

from chamber.utility.plot.contracts import (
    Axis,
    DataSeries,
    Layout,
    Plot)

import chamber.ifx.configuration as config


class ExperimentAccess(object):
    """Experiment access."""

    # ------------------------------------------------------------------------
    # Constructors

    def __init__(self):
        """Create the SQLAlchemy engine for the MySQL database."""
        # Get database specific connection string.
        database_type = config.get_value('database_type')
        if database_type.lower() == 'mysql':  # pragma: no cover
            # Configure MySQL server connection string
            host = config.get_value('host', 'MySQL-Server')
            user = config.get_value('user', 'MySQL-Server')
            password = config.get_value('password', 'MySQL-Server')
            conn_string = f'mysql+mysqlconnector://{user}:{password}@{host}/'
        else:
            # Use in memory database
            conn_string = 'sqlite:///:memory:'

        # Create engine
        self._engine = create_engine(conn_string, echo=False)

        # Create the schema if it doesn't exist (MySQL only)
        if database_type.lower() == 'mysql':  # pragma: no cover
            self._schema = 'chamber'
            self._engine.execute(
                f'CREATE DATABASE IF NOT EXISTS `{self._schema}`;')
            self._engine.execute(f'USE `{self._schema}`;')

        # Create tables if they don't exist
        Base.metadata.create_all(self._engine)

        # Session factory
        self.Session = sessionmaker(bind=self._engine)

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def get_raw_data(self, path):
        """
        Use path to get raw data for an experiment.

        Parameters
        ----------
        path : str
            Path to the file containing data to load.

        Returns
        -------
        mvso.access.external.contracts.DataSpec

        """
        self._connect(path)
        observations = []
        for index in self._data.index:
            observations.append(self._get_observation_specs(index))
        data = dict(
            setting=self._get_setting_specs(),
            experiment=self._get_experiment_specs(),
            observations=observations,
            )
        return dacite.from_dict(DataSpec, data)

    def add_raw_data(self, data_specs):
        """
        Add experimental data to the database.

        This method does not rewite data that already exists in the databse.
        NOTE: The tube must already exist in the database in order to add the
        experimental data.

        Parameters
        ----------
        data_specs : list of chamber.access.experiment.contracts.DataSpec
            All observations for a given experiment.

        Returns
        -------
        dict of {str: int}
            Dictionary summarizing the database insert.

        See Also
        --------
        ExperimentAccess.get_data_spec : Get a valid DataSpec from tdms file.

        Notes
        -----
        You can use ExperimentAccess to build a valid DataSpec object.
        The example below assumes you already have a valid `DataSpec` object.
        If you do not, the easiest way to get one is to call
        `ExperimentAccess.get_data_spec()` which will return a valid `DataSpec`
        object to use as input.

        Examples
        --------
        Assuming that you have a valid `DataSpec` object called `data_spec`
        containing two observations with three temperatures each:
        >>> access = ExperimentAccess()
        >>> result = access.add_raw_data(data_spec)
        >>> result
        {'tube_id': 1, 'setting_id': 1, 'experiment_id': 1, 'observations': 2,
        'temperatures': 6}

        """
        tube_id = data_specs.experiment.tube_id
        try:
            # look for the tube using the tube id
            session = self.Session()
            tube = session.query(Tube).filter(Tube.tube_id == tube_id).first()
            session.close()
            assert tube
        except AssertionError:
            err_msg = (
                'You must add your tube to the database: '
                f'tube_id `{tube_id}` does not exist.')
            print(err_msg)
            return
        else:
            # The tube is there so we can call the other functions
            setting_id = self._add_setting(data_specs.setting)
            experiment_id = self._add_experiment(data_specs.experiment, setting_id)
            observations_dict = self._add_observations(
                data_specs.observations, experiment_id)
            result = dict(
                tube_id=tube_id,
                setting_id=setting_id,
                experiment_id=experiment_id,
                observations=observations_dict['observations'],
                temperatures=observations_dict['temperatures'])
            return result
        finally:
            session.close()

    def layout_raw_data(self, data_specs):
        """
        Use `data_specs` to return a layout contract.

        Parameters
        ----------
        data_specs : mvso.access.external.contracts.DataSpec
            Raw data from an experiment.

        Returns
        -------
        mvso.utility.plot.contracts.Layout

        See Also
        --------
        ExternalAccess.get_raw_data : Get raw data for an experiment

        """
        # Idx DataSeries
        idx = [obs.idx for obs in data_specs.observations]
        data = dict(values=idx)
        idx = dacite.from_dict(DataSeries, data)

        # Mass DataSeries
        mass = [obs.mass for obs in data_specs.observations]
        data = dict(values=mass, label='mass')
        mass = dacite.from_dict(DataSeries, data)

        # Mass Axis
        axes = dict()
        data = dict(data=[mass], y_label='mass, [kg]')
        axes['mass'] = dacite.from_dict(Axis, data)

        # Temp DataSeries
        thermocouple_count = len(data_specs.observations[0].temperatures)
        temp_lists = [[] for _ in range(thermocouple_count)]
        for observation in data_specs.observations:
            # Now that I am inside a single observation I have 10 temperature
            # steps, but I wouldn't have known that off the bat.
            for i, temp_spec in enumerate(observation.temperatures):
                observation
                temp_lists[i].append(temp_spec.temperature)

        # Now I can begin the list of ordinates for the temperature plot
        ordinates = []
        initial_temps = data_specs.observations[0].temperatures
        for i, temps in enumerate(temp_lists):
            # Create the y-axis
            data = dict(
                values=temps,
                label=f'TC-{initial_temps[i].thermocouple_num}')
            this_data_series = dacite.from_dict(DataSeries, data)
            ordinates.append(this_data_series)

        # Dew point
        dew_point = [obs.dew_point for obs in data_specs.observations]
        data = dict(values=dew_point, label='dew point')
        data_series = dacite.from_dict(DataSeries, data)
        ordinates.append(data_series)

        # Surface temp
        surface_temp = [obs.surface_temp for obs in data_specs.observations]
        data = dict(values=surface_temp, label='surface temp')
        data_series = dacite.from_dict(DataSeries, data)
        ordinates.append(data_series)

        # IC temp
        ic_temp = [obs.ic_temp for obs in data_specs.observations]
        data = dict(values=ic_temp, label='IC temp')
        data_series = dacite.from_dict(DataSeries, data)
        ordinates.append(data_series)

        # Temp Axis
        data = dict(data=ordinates, y_label='temperature, [K]')
        axes['temp'] = dacite.from_dict(Axis, data)

        # Pressure DataSeries
        pressure = [obs.pressure for obs in data_specs.observations]
        data = dict(values=pressure, label='pressure')
        pressure = dacite.from_dict(DataSeries, data)

        # Pressure Axis
        data = dict(data=[pressure], y_label='pressure, [Pa]')
        axes['pressure'] = dacite.from_dict(Axis, data)

        # Mass and temperature Plot
        plots = dict()
        data = dict(
            abscissa=idx,
            axes=[axes['mass'], axes['temp']],
            x_label='index',
            legend=False)
        plots['mass_and_temp'] = dacite.from_dict(Plot, data)

        # Pressure
        data = dict(
            abscissa=idx,
            axes=[axes['pressure']],
            x_label='index')
        plots['pressure'] = dacite.from_dict(Plot, data)

        # Finally put together the layout
        data = dict(
            plots=[plots['mass_and_temp'], plots['pressure']],
            style='seaborn-darkgrid')
        layout = dacite.from_dict(Layout, data)
        return layout

    def add_fit(self, fit_spec, experiment_id):
        """
        Add fit to the database.

        This method does not rewite data that already exists in the databse.
        NOTE: The experiment and observations must already exist in the
        database in order to add the fit.

        Parameters
        ----------
        fit_spec : chamber.access.experiment.contracts.FitSpec
            Parameters for a given fit.

        Returns
        -------
        int
            ExperimentId for the given fit.
        int
            Index in the test for the given fit.

        Examples
        --------
        Assuming that you have a valid `FitSpec` object called `fit_spec`:
        >>> access = ExperimentAccess()
        >>> exp_id, idx = access.add_fit(fit_spec)
        >>> exp_id
        1
        >>> idx
        10

        """
        session = self.Session()

        try:
            # Check if tube exists
            query = session.query(Fit).filter(
                and_(
                    Fit.idx == fit_spec.idx,
                    Fit.experiment_id == fit_spec.exp_id,
                    )
                )
            fit = query.first()
            # If not, insert it
            if not fit:
                fit_to_add = Fit(
                    a=fit_spec.a,
                    sig_a=fit_spec.sig_a,
                    b=fit_spec.b,
                    sig_b=fit_spec.sig_b,
                    r2=fit_spec.r2,
                    q=fit_spec.q,
                    chi2=fit_spec.chi2,
                    nu_chi=fit_spec.nu_chi,
                    idx=fit_spec.idx,
                    experiment_id=fit_spec.exp_id,
                    mddp=fit_spec.mddp,
                    x1s=fit_spec.x1s,
                    x1e=fit_spec.x1e,
                    x1=fit_spec.x1,
                    m1s=fit_spec.m1s,
                    m1e=fit_spec.m1e,
                    m1=fit_spec.m1,
                    rhos=fit_spec.rhos,
                    rhoe=fit_spec.rhoe,
                    rho=fit_spec.rho,
                    Bm1=fit_spec.Bm1,
                    T=fit_spec.T,
                    D12=fit_spec.D12,
                    hfg=fit_spec.hfg,
                    hu=fit_spec.hu,
                    hs=fit_spec.hs,
                    cpv=fit_spec.cpv,
                    he=fit_spec.he,
                    cpl=fit_spec.cpl,
                    hT=fit_spec.hT,
                    qcu=fit_spec.qcu,
                    Ebe=fit_spec.Ebe,
                    Ebs=fit_spec.Ebs,
                    qrs=fit_spec.qrs,
                    kv=fit_spec.kv,
                    alpha=fit_spec.alpha,
                    Bh=fit_spec.Bh,
                    M=fit_spec.M,
                    gamma1=fit_spec.gamma1,
                    beta=fit_spec.beta,
                    Deltam=fit_spec.Deltam,
                    DeltaT=fit_spec.DeltaT,
                    mu=fit_spec.mu,
                    nu=fit_spec.nu,
                )
                session.add(fit_to_add)
                session.commit()
                return fit_to_add.experiment_id, fit_to_add.idx
            else:
                return fit.experiment_id, fit.idx
        except:  # pragma: no cover
            session.rollback()
        finally:
            session.close()

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _connect(self, path):
        try:
            self._tdms_file = TdmsFile(path)
            self._settings = self._tdms_file.object('Settings').as_dataframe()
            self._data = self._tdms_file.object('Data').as_dataframe()
            self._properties = self._tdms_file.object().properties
        except FileNotFoundError as err:
            print(f'File not found: `{err}`')

    def _get_temperature_specs(self, index):
        temperature_specs = []
        # thermocouple_readings is a pd.Series indexed by strings like 'TC0'.
        thermocouple_readings = self._data.loc[
            index, self._data.columns.str.contains('TC')]
        # Get the idx for all of the temperature readings.
        idx = int(self._data.loc[index, 'Idx'])
        for tc_str, value in thermocouple_readings.items():
            temperature = Decimal(str(round(value, 2)))
            # Thermocouples that are not connected will read above 2500 K.
            # Temperatures less than 1000 are valid.
            if temperature < 1000:
                thermocouple_num = int(tc_str.strip('TC'))
                data = dict(
                    thermocouple_num=thermocouple_num,
                    temperature=temperature,
                    idx=idx)
                this_spec = dacite.from_dict(TemperatureSpec, data)
                temperature_specs.append(this_spec)

        return temperature_specs

    def _get_observation_specs(self, index):
        data = self._data
        observation_data = dict(
            cap_man_ok=True if data.loc[index, 'CapManOk'] else False,
            dew_point=Decimal(str(round(data.loc[index, 'DewPoint'], 2))),
            idx=int(data.loc[index, 'Idx']),
            mass=Decimal(str(round(data.loc[index, 'Mass'], 7))),
            optidew_ok=True if data.loc[index, 'OptidewOk'] else False,
            pow_out=Decimal(str(round(data.loc[index, 'PowOut'], 4))),
            pow_ref=Decimal(str(round(data.loc[index, 'PowRef'], 4))),
            pressure=int(data.loc[index, 'Pressure']),
            surface_temp=Decimal(str(round(data.loc[index, 'SurfaceTemp'], 2))),
            ic_temp=Decimal(str(round(data.loc[index, 'IC Temp'], 2))),
            temperatures=self._get_temperature_specs(index))

        return dacite.from_dict(ObservationSpec, observation_data)

    def _get_experiment_specs(self):
        data = dict(
            author=self._properties['author'],
            datetime=self._properties['DateTime'],
            description=self._properties['description'],
            tube_id=int(self._settings['TubeID']))
        return dacite.from_dict(ExperimentSpec, data)

    def _get_setting_specs(self):
        data = dict(
            duty=Decimal(self._settings.DutyCycle[0]),
            pressure=int(5e3*round(self._data.Pressure.mean()/5e3)),
            temperature=Decimal(str(5*round(self._data.TC10.mean()/5))),
            time_step=Decimal(str(self._settings.TimeStep[0])),
            )
        return dacite.from_dict(SettingSpec, data)

    def _add_tube(self, tube_spec):
        session = self.Session()

        try:
            # Check if tube exists
            query = session.query(Tube.tube_id).filter(
                and_(
                    Tube.inner_diameter == tube_spec.inner_diameter,
                    Tube.outer_diameter == tube_spec.outer_diameter,
                    Tube.height == tube_spec.height,
                    Tube.material == tube_spec.material,
                    Tube.mass == tube_spec.mass
                    )
                )
            tube_id = query.first()
            # If not, insert it
            if not tube_id:
                tube_to_add = Tube(
                    inner_diameter=tube_spec.inner_diameter,
                    outer_diameter=tube_spec.outer_diameter,
                    height=tube_spec.height,
                    material=tube_spec.material,
                    mass=tube_spec.mass)
                session.add(tube_to_add)
                session.commit()
                return tube_to_add.tube_id
            else:
                return tube_id[0]
        except:  # pragma: no cover
            session.rollback()
        finally:
            session.close()

    def _add_setting(self, setting_spec):
        session = self.Session()

        try:
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
            # If not, insert it
            if not setting_id:
                setting_to_add = Setting(
                    duty=setting_spec.duty,
                    pressure=setting_spec.pressure,
                    temperature=setting_spec.temperature,
                    time_step=setting_spec.time_step)
                session.add(setting_to_add)
                session.commit()
                return setting_to_add.setting_id
            else:
                return setting_id[0]
        except:  # pragma: no cover
            session.rollback()
        finally:
            session.close()

    def _add_experiment(self, experiment_spec, setting_id):
        session = self.Session()

        try:
            # Check if the experiment exists
            query = session.query(Experiment.experiment_id)
            query = query.filter(Experiment.datetime == experiment_spec.datetime)
            experiment_id = query.first()
            # If not, insert it
            if not experiment_id:
                experiment_to_add = Experiment(
                    author=experiment_spec.author,
                    datetime=experiment_spec.datetime,
                    description=experiment_spec.description,
                    tube_id=experiment_spec.tube_id,
                    setting_id=setting_id)
                session.add(experiment_to_add)
                session.commit()
                return experiment_to_add.experiment_id
            else:
                return experiment_id[0]
        except:  # pragma: no cover
            session.rollback()
        finally:
            session.close()

    def _add_observations(self, observations, experiment_id):
        session = self.Session()

        try:
            # Check if the experiment exists
            query = session.query(Observation.experiment_id)
            query = query.filter(Observation.experiment_id == experiment_id)
            returned_experiment_id = query.first()
            # If not, insert it
            if not returned_experiment_id:
                objects = []
                for observation in observations:
                    # Construct the observation orm object
                    this_observation = Observation(
                        cap_man_ok=observation.cap_man_ok,
                        dew_point=observation.dew_point,
                        idx=observation.idx,
                        mass=observation.mass,
                        optidew_ok=observation.optidew_ok,
                        pow_out=observation.pow_out,
                        pow_ref=observation.pow_ref,
                        pressure=observation.pressure,
                        experiment_id=experiment_id,
                        surface_temp=observation.surface_temp,
                        ic_temp=observation.ic_temp)
                    # Append
                    objects.append(this_observation)
                    for temperature in observation.temperatures:
                        # Construct the temperature orm object
                        this_temperature = Temperature(
                            thermocouple_num=temperature.thermocouple_num,
                            temperature=temperature.temperature,
                            idx=temperature.idx,
                            experiment_id=experiment_id)
                        # Append
                        objects.append(this_temperature)
                # Perform a bulk insert
                session.bulk_save_objects(objects)
                session.commit()
        except:  # pragma: no cover
            session.rollback()
        finally:
            # Observation counts for the experiment
            query = session.query(func.count(Observation.experiment_id))
            query = query.filter(Observation.experiment_id == experiment_id)
            obs_count = query.one()[0]
            # Temperature counts for the experiment
            query = session.query(func.count(Temperature.experiment_id))
            query = query.filter(Temperature.experiment_id == experiment_id)
            temp_count = query.one()[0]

            session.close()

            return dict(observations=obs_count, temperatures=temp_count)

    def _teardown(self):
        """
        Completely teardown database.

        This drops all of the tables, delets the databse, and disposes of the
        objects engine.

        """
        # Drop all tables
        Base.metadata.drop_all(self._engine)
        # Dispose of the engine
        self._engine.dispose()
