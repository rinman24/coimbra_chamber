"""Analysis engine service."""


import pandas as pd
from uncertainties import ufloat

from chamber.access.experiment.service import ExperimentAccess


class AnalysisEngine(object):
    """Analysis engine."""

    def __init__(self):
        """Constructor."""
        self._exp_acc = ExperimentAccess()

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def perform_analysis(self, data, uncert):
        """TODO: docstring."""
        self._preprocess(data, uncert)
        self._regress_mass_flux()
        self._persist_results()

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

    def _preprocess(self, data, uncert):
        # TODO: Implement.
        pass

    def _regress_mass_flux(self):
        # TODO: Implement.
        pass

    def _persist_results(self):
        # TODO: Implement.
        pass
