"""Analysis engine service."""


import dacite
import pandas as pd
from uncertainties import ufloat

from chamber.access.experiment.service import ExperimentAccess
from chamber.utility.plot.contracts import Axis, DataSeries, Layout, Plot


class AnalysisEngine(object):
    """Analysis engine."""

    def __init__(self):
        """Constructor."""
        self._exp_acc = ExperimentAccess()

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def perform_analysis(self, data):
        """TODO: docstring."""
        # Preprocess
        observations = self._get_observations(data.observations)
        # NOTE: You are here.
        self._regress_mass_flux()
        self._persist_results()
        assert observations

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _get_observations(self, observations):
        """Return a dataframe of experimental data with uncertainties."""
        # Create empty lists to hold data as we iterate through observations.
        dew_point = []
        mass = []
        pow_ref = []
        pressure = []
        surface_temp = []
        ic_temp = []

        cap_man = []
        optidew = []

        temp = []

        time = []

        # Interate and append observations while adding uncertainties
        initial_idx = observations[0].idx
        for obs in observations:
            dew_point.append(ufloat(obs.dew_point, 0.2))
            mass.append(ufloat(obs.mass, 1e-7))
            pow_ref.append(ufloat(obs.pow_ref, float(obs.pow_ref) * 0.05))
            pressure.append(ufloat(obs.pressure, int(obs.pressure * 0.0015)))
            surface_temp.append(ufloat(obs.surface_temp, 0.5))
            ic_temp.append(ufloat(obs.ic_temp, 0.2))

            # Average temperatures with error propagation
            temps = obs.temperatures
            temp.append(
                sum(ufloat(temp.temperature, 0.2) for temp in temps)
                / len(temps)
                )

            # Bools for equipment status
            cap_man.append(obs.cap_man_ok)
            optidew.append(obs.optidew_ok)

            # Ensure that time starts at zero
            time.append(obs.idx - initial_idx)

        # DataFrame payload
        data = dict(
            Tdp=dew_point,
            m=mass,
            Jref=pow_ref,
            P=pressure,
            Te=temp,
            Ts=surface_temp,
            Tic=ic_temp,
            cap_man=cap_man,
            optidew=optidew,
            )

        return pd.DataFrame(index=time, data=data)

    def _layout_observations(self, observations):
        # internal helper logic
        def nominal(ufloat_):
            return ufloat_.nominal_value

        def std_dev(ufloat_):
            return ufloat_.std_dev

        # DataSeries ---------------------------------------------------------
        data_series = dict()
        # First get the time data series
        data = dict(values=observations.index.tolist())
        data_series['t'] = dacite.from_dict(DataSeries, data)
        # dew point, Tdp
        data = dict(
            values=observations.Tdp.map(nominal).tolist(),
            sigma=observations.Tdp.map(std_dev).tolist(),
            label='Tdp')
        data_series['Tdp'] = dacite.from_dict(DataSeries, data)
        # mass, m
        data = dict(
            values=observations.m.map(nominal).tolist(),
            sigma=observations.m.map(std_dev).tolist(),
            label='m')
        data_series['m'] = dacite.from_dict(DataSeries, data)
        # pow_ref, Jref
        data = dict(
            values=observations.Jref.map(nominal).to_list(),
            sigma=observations.Jref.map(std_dev).to_list(),
            label='Jref')
        data_series['Jref'] = dacite.from_dict(DataSeries, data)
        # pressure, P
        data = dict(
            values=observations.P.map(nominal).tolist(),
            sigma=observations.P.map(std_dev).tolist(),
            label='P')
        data_series['P'] = dacite.from_dict(DataSeries, data)
        # Ambient temp, Te
        data = dict(
            values=observations.Te.map(nominal).tolist(),
            sigma=observations.Te.map(std_dev).tolist(),
            label='Te')
        data_series['Te'] = dacite.from_dict(DataSeries, data)
        # Surface temp, Ts
        data = dict(
            values=observations.Ts.map(nominal).tolist(),
            sigma=observations.Ts.map(std_dev).tolist(),
            label='Ts')
        data_series['Ts'] = dacite.from_dict(DataSeries, data)
        # IC temp, Tic
        data = dict(
            values=observations.Tic.map(nominal).tolist(),
            sigma=observations.Tic.map(std_dev).tolist(),
            label='Tic')
        data_series['Tic'] = dacite.from_dict(DataSeries, data)
        # Cap-man status, cap_man
        data = dict(
            values=observations.cap_man.tolist(),
            label='cap_man')
        data_series['cap_man'] = dacite.from_dict(DataSeries, data)
        # Optidew status, optidew
        data = dict(
            values=observations.optidew.tolist(),
            label='optidew')
        data_series['optidew'] = dacite.from_dict(DataSeries, data)

        # Axes ---------------------------------------------------------------
        axes = dict()

        data = dict(
            data=[data_series['m']], y_label='mass, [kg]',
            error_type='continuous')
        axes['mass'] = dacite.from_dict(Axis, data)

        data = dict(
            data=[data_series['Tdp'], data_series['Te'], data_series['Ts'],
                  data_series['Tic']],
            y_label='temperature, [K]',
            error_type='continuous')
        axes['temp'] = dacite.from_dict(Axis, data)

        data = dict(
            data=[data_series['P']], y_label='pressure, [Pa]',
            error_type='continuous')
        axes['pressure'] = dacite.from_dict(Axis, data)

        data = dict(
            data=[data_series['Jref']], y_label='Ref power, [W]',
            error_type='continuous')
        axes['Jref'] = dacite.from_dict(Axis, data)

        data = dict(
            data=[data_series['cap_man'], data_series['optidew']],
            y_label='status')
        axes['status'] = dacite.from_dict(Axis, data)

        # Then the Plots ---------------------------------------------------------
        plots = dict()

        data = dict(
            abscissa=data_series['t'],
            axes=[axes['mass'], axes['temp']],
            x_label='index')
        plots['mass_and_temp'] = dacite.from_dict(Plot, data)

        data = dict(
            abscissa=data_series['t'],
            axes=[axes['pressure'], axes['Jref']],
            x_label='index')
        plots['pressure_and_pow'] = dacite.from_dict(Plot, data)

        data = dict(
            abscissa=data_series['t'],
            axes=[axes['status']],
            x_label='index')
        plots['status'] = dacite.from_dict(Plot, data)

        # Finally, the layout ----------------------------------------------------
        data = dict(
            plots=[
                plots['mass_and_temp'], plots['pressure_and_pow'],
                plots['status']
                ],
            style='seaborn-darkgrid')

        return dacite.from_dict(Layout, data)

    def _regress_mass_flux(self):
        # TODO: Implement.
        pass

    def _persist_results(self):
        # TODO: Implement.
        pass
