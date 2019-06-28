"""Analysis engine service."""


import dacite
import pandas as pd
from scipy.stats import chi2
from uncertainties import ufloat

from chamber.access.experiment.service import ExperimentAccess
from chamber.access.experiment.contracts import Fit

from chamber.utility.io.contracts import Prompt
from chamber.utility.io.service import IOUtility

from chamber.utility.plot.contracts import Axis, DataSeries, Layout, Plot
from chamber.utility.plot.service import PlotUtility


class AnalysisEngine(object):
    """TODO: docstring."""

    def __init__(self):
        """TODO: docstring."""
        self._exp_acc = ExperimentAccess()
        self._io_util = IOUtility()
        self._plot_util = PlotUtility()

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def perform_analysis(self, data):
        """TODO: docstring."""
        # Preprocess
        # observations = self._get_observations(data.observations)
        # layout = self._layout_observations(observations)
        self._plot_util.plot(layout)
        # Get user input
        data = dict(messages=['Lower limit: ', 'Upper limit: '])
        prompt = dacite.from_dict(Prompt, data)
        response = self._io_util.get_input(prompt)
        # Parse the anser out into two integers
        lower = int(response[0])
        upper = int(response[1])
        # Filter the observations
        observations = observations.loc[lower:upper, :]
        # Confirm that this was done correctly
        # layout = self._layout_observations(observations)
        self._plot_util.plot(layout)
        # NOTE: You are here.
        # self._regress_mass_flux()
        # self._persist_results()
        return observations

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _get_observations(self, observations):
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
            pow_ref.append(ufloat(obs.pow_ref, abs(float(obs.pow_ref)) * 0.05))
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

        self._observations = pd.DataFrame(index=time, data=data)

    def _layout_observations(self):
        # internal helper logic
        def nominal(ufloat_):
            return ufloat_.nominal_value

        def std_dev(ufloat_):
            return ufloat_.std_dev

        # DataSeries ---------------------------------------------------------
        data_series = dict()
        # First get the time data series
        data = dict(values=self._observations.index.tolist())
        data_series['t'] = dacite.from_dict(DataSeries, data)
        # dew point, Tdp
        data = dict(
            values=self._observations.Tdp.map(nominal).tolist(),
            sigma=self._observations.Tdp.map(std_dev).tolist(),
            label='Tdp')
        data_series['Tdp'] = dacite.from_dict(DataSeries, data)
        # mass, m
        data = dict(
            values=self._observations.m.map(nominal).tolist(),
            sigma=self._observations.m.map(std_dev).tolist(),
            label='m')
        data_series['m'] = dacite.from_dict(DataSeries, data)
        # pow_ref, Jref
        data = dict(
            values=self._observations.Jref.map(nominal).to_list(),
            sigma=self._observations.Jref.map(std_dev).to_list(),
            label='Jref')
        data_series['Jref'] = dacite.from_dict(DataSeries, data)
        # pressure, P
        data = dict(
            values=self._observations.P.map(nominal).tolist(),
            sigma=self._observations.P.map(std_dev).tolist(),
            label='P')
        data_series['P'] = dacite.from_dict(DataSeries, data)
        # Ambient temp, Te
        data = dict(
            values=self._observations.Te.map(nominal).tolist(),
            sigma=self._observations.Te.map(std_dev).tolist(),
            label='Te')
        data_series['Te'] = dacite.from_dict(DataSeries, data)
        # Surface temp, Ts
        data = dict(
            values=self._observations.Ts.map(nominal).tolist(),
            sigma=self._observations.Ts.map(std_dev).tolist(),
            label='Ts')
        data_series['Ts'] = dacite.from_dict(DataSeries, data)
        # IC temp, Tic
        data = dict(
            values=self._observations.Tic.map(nominal).tolist(),
            sigma=self._observations.Tic.map(std_dev).tolist(),
            label='Tic')
        data_series['Tic'] = dacite.from_dict(DataSeries, data)
        # Cap-man status, cap_man
        data = dict(
            values=self._observations.cap_man.tolist(),
            label='cap_man')
        data_series['cap_man'] = dacite.from_dict(DataSeries, data)
        # Optidew status, optidew
        data = dict(
            values=self._observations.optidew.tolist(),
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
            axes=[axes['pressure']],
            x_label='index')
        plots['pressure'] = dacite.from_dict(Plot, data)

        data = dict(
            abscissa=data_series['t'],
            axes=[axes['Jref'], axes['status']],
            x_label='index')
        plots['pow_and_status'] = dacite.from_dict(Plot, data)

        # Finally, the layout ----------------------------------------------------
        data = dict(
            plots=[
                plots['mass_and_temp'], plots['pressure'],
                plots['pow_and_status']
                ],
            style='seaborn-darkgrid')

        return dacite.from_dict(Layout, data)

    @staticmethod
    def _max_slice(df, center, col):
        left = (2 * center) - len(df) + 1
        right = 2 * center
        result = df.loc[left:right, col].tolist()
        return result

    @staticmethod
    def _fit(sample):
        # Prepare the data
        y = [i.nominal_value for i in sample]
        sig = [i.std_dev for i in sample]
        x = list(range(len(y)))  # Always indexed at zero

        # Determine fit components
        S = sum(1/sig[i]**2 for i in range(len(x)))
        Sx = sum(x[i]/sig[i]**2 for i in range(len(x)))
        Sy = sum(y[i]/sig[i]**2 for i in range(len(x)))
        Sxx = sum(x[i]**2/sig[i]**2 for i in range(len(x)))
        Sxy = sum(x[i]*y[i]/sig[i]**2 for i in range(len(x)))
        Delta = S*Sxx - Sx**2

        # Now calculate model parameters: y = a + bx
        a = (Sxx*Sy - Sx*Sxy) / Delta
        sig_a = (Sxx/Delta)**0.5
        b = (S*Sxy - Sx*Sy) / Delta
        sig_b = (S/Delta)**0.5

        return dict(
            a=a,
            sig_a=sig_a,
            b=b,
            sig_b=sig_b,
            )

    def _best_fit(self, sample, center, steps, error):
        total = len(sample)
        while center + steps <= total:
            this_sample = sample[center - steps: center + steps + 1]
            fit = self._fit(this_sample)
            if fit['sig_b']/abs(fit['b']) <= error:
                best_fit = self._evaluate_fit(this_sample, fit)
                return best_fit
            else:
                steps += steps

    @staticmethod
    def _evaluate_fit(sample, fit):
        # Prepare the data
        y = [i.nominal_value for i in sample]
        sig = [i.std_dev for i in sample]
        x = list(range(len(y)))  # Always indexed at zero

        a = fit['a']
        b = fit['b']

        # Calculate R^2
        predicted = [a + b*i for i in x]
        y_bar = sum(y)/len(y)
        SSres = sum((y[i] - predicted[i])**2 for i in range(len(x)))
        SStot = sum((y[i] - y_bar)**2 for i in range(len(x)))
        R2 = 1 - SSres/SStot

        # Now for the merit function; i.e. chi^2
        merit_value = sum(((y[i] - a - b*x[i])/sig[i])**2 for i in range(len(x)))

        # And the goodness of fit; i.e. Q from Numerical Recipes
        Q = chi2.sf(merit_value, len(x)-2)

        # Prepare payload
        data = fit  # copy of a, b, sig_a, and sig_b
        data['r2'] = R2
        data['q'] = Q
        data['chi2'] = merit_value
        data['nu'] = len(x) - 2

        return dacite.from_dict(Fit, data)
