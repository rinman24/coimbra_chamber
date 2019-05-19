"""Module encapsulates access to tdms data."""

from decimal import Decimal

from dacite import from_dict
from nptdms import TdmsFile

from chamber.access.sql.contracts import ExperimentSpec, ObservationSpec
from chamber.access.sql.contracts import SettingSpec, TemperatureSpec


class TdmsAccess(object):
    """Encapsulates all aspects of tdms access for an experiment."""

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def connect(self, path):
        """Connect to a tdms file."""
        try:
            self._tdms_file = TdmsFile(path)
            self._settings = self._tdms_file.object('Settings').as_dataframe()
            self._data = self._tdms_file.object('Data').as_dataframe()
            self._properties = self._tdms_file.object().properties
        except FileNotFoundError as err:
            print(f'File not found: `{err}`')

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

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
                this_spec = from_dict(TemperatureSpec, data)
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
            temperatures=self._get_temperature_specs(index))

        return from_dict(ObservationSpec, observation_data)

    def _get_experiment_specs(self, setting_id):
        data = dict(
            author=self._properties['author'],
            datetime=self._properties['DateTime'],
            description=self._properties['description'],
            pool_id=int(self._settings['TubeID']),
            setting_id=setting_id)
        return from_dict(ExperimentSpec, data)

    def _get_setting_specs(self):
        data = dict(
            duty=Decimal(self._settings.DutyCycle[0]),
            pressure=int(5e3*round(self._data.Pressure.mean()/5e3)),
            temperature=Decimal(str(5*round(self._data.TC10.mean()/5))),
            time_step=Decimal(str(self._settings.TimeStep[0])),
            )
        return from_dict(SettingSpec, data)
