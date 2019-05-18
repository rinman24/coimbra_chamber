"""Module encapsulates access to tdms data."""

from decimal import Decimal

from dacite import from_dict
from nptdms import TdmsFile

from chamber.access.sql.contracts import TemperatureSpec


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
