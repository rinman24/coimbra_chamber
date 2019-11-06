"""Analysis engine service."""


import dacite
import pandas as pd
from math import log, pi

from CoolProp.CoolProp import PropsSI
from CoolProp.HumidAirProp import HAPropsSI
from scipy.stats import chi2
from uncertainties import ufloat

from coimbra_chamber.access.experiment.service import ExperimentAccess
from coimbra_chamber.access.experiment.contracts import FitSpec

from coimbra_chamber.utility.io.contracts import Prompt
from coimbra_chamber.utility.io.service import IOUtility

from coimbra_chamber.utility.plot.contracts import Axis, DataSeries, Layout, Plot
from coimbra_chamber.utility.plot.service import PlotUtility


class AnalysisEngine(object):
    """Encapsulate all aspects of analysis."""

    def __init__(self, experiment_id):  # noqa: D107
        self._experiment_id = experiment_id

        self._exp_acc = ExperimentAccess()
        self._io_util = IOUtility()
        self._plot_util = PlotUtility()

        self._error = 0.01
        self._fits = []
        self._idx = 1
        self._steps = 1
        self._bounds = (None, None)

        # IR sensor calibration
        self._a = ufloat(-2.34, 0.07)
        self._b = ufloat(1.0445, 0.0022)

        # Tube radius
        self._R = ufloat(0.0355, 0.0001)
        self._A = pi*self._R**2
        self._M1 = 18.015
        self._M2 = 28.964
        self._SIGMA = 5.67036713e-8
        self._eps_chamber = 0.1
        self._eps_h20 = 0.99
        self._R_chamber = 0.3
        self._L_chamber = 0.7
        self._A_chamber = (
            2*pi*self._R_chamber**2 + 2*pi*self._R_chamber*self._L_chamber
        )
        self._RAD_FACT = (
            self._A * (
                (1-self._eps_chamber)/(self._eps_chamber*self._A_chamber)
                + 1/self._A
                + (1-self._eps_h20)/(self._eps_h20*self._A)
            )
        )
        self._ACC_G = 9.81

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    def process_fits(self, data):
        """
        Process fits from data.

        Parameters
        ----------
        data : comimbra_chamber.access.experiment.contracts.DataSpec.

        """
        self._data = data
        self._get_observations()
        self._get_fits()
        self._persist_fits()

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    def _get_observations(self):
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
        observations = self._data.observations
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

        self._layout = dacite.from_dict(Layout, data)

    def _get_fits(self):
        # len - 2 because we want to make sure we never end up at the last
        # index and can't take a max slice
        while self._idx < len(self._observations) - 2:
            # Get a new sample centered at the self._idx that is as large as
            # possible.
            left = (2 * self._idx) - len(self._observations) + 1
            right = 2 * self._idx
            self._sample = self._observations.loc[left:right, :]
            # Then search for the best fit in self._sample
            self._get_best_local_fit()
            if self._this_fit:  # We got a fit that met the error threshold
                self._evaluate_fit()
                self._set_local_exp_state()
                self._set_local_properties()
                self._set_nondim_groups()
                self._fits.append(self._this_fit)
                # Length of the best fit is the degrees of freedom plus 2 for
                # a linear fit.
                self._idx += self._this_fit['nu_chi'] + 2
            else:  # _get_best_local_fit returned None
                self._idx += len(self._sample)

    def _persist_fits(self):
        counter = 0
        for data in self._fits:
            fit_spec = dacite.from_dict(FitSpec, data)
            self._exp_acc.add_fit(fit_spec, self._experiment_id)
            counter += 1
        return counter

    # Properties .............................................................

    def _set_local_exp_state(self):
        samples = len(self._this_sample)
        data = self._this_sample
        offset = 273.15

        # Use calibration for ifrared sensor
        Ts_bar_K = sum(data.Ts)/samples
        Ts_bar_C = Ts_bar_K - offset
        Ts_bar_C = self._a + self._b*Ts_bar_C
        Ts_bar_K = Ts_bar_C + offset

        # Now the rest of the state variables
        Te_bar = sum(data.Te)/samples
        # Round experimental state to the nearest 5 for reference
        Te_bar = ufloat(5 * round(Te_bar.nominal_value/5), Te_bar.std_dev)
        Tdp_bar = sum(data.Tdp)/samples
        P_bar = sum(data.P)/samples

        self._experimental_state = dict(
            Te=Te_bar,
            Tdp=Tdp_bar,
            Ts=Ts_bar_K,
            P=P_bar,
        )

    def _set_local_properties(self):
        # Internal mapper ----------------------------------------------------
        def x1_2_m1(self, x1):
            num = self._M1 * x1
            den = num + (self._M2 * (1 - x1))
            return num/den

        Ts = self._experimental_state['Ts']
        P = self._experimental_state['P']
        Te = self._experimental_state['Te']
        Tdp = self._experimental_state['Tdp']

        # mddp ---------------------------------------------------------------
        mdot = ufloat(-self._this_fit['b'], self._this_fit['sig_b'])
        mddp = mdot/self._A

        # x1 -----------------------------------------------------------------
        # s-state
        x1s_nv = HAPropsSI(
            'psi_w',
            'T', Ts.nominal_value,
            'P', P.nominal_value,
            'RH', 1)
        x1s_sig = x1s_nv - HAPropsSI(
            'psi_w',
            'T', Ts.nominal_value + Ts.std_dev,
            'P', P.nominal_value,
            'RH', 1)
        x1s = ufloat(x1s_nv, abs(x1s_sig))
        # e-state
        x1e_nv = HAPropsSI(
            'psi_w',
            'T', Te.nominal_value,
            'P', P.nominal_value,
            'Tdp', Tdp.nominal_value)
        x1e_sig = x1e_nv - HAPropsSI(
            'psi_w',
            'T', Te.nominal_value + Te.std_dev,
            'P', P.nominal_value,
            'Tdp', Tdp.nominal_value + Tdp.std_dev)
        x1e = ufloat(x1e_nv, abs(x1e_sig))
        # film
        x1 = (x1s+x1e) / 2

        # m1 -----------------------------------------------------------------
        # s-state
        m1s = x1_2_m1(self, x1s)
        # e-state
        m1e = x1_2_m1(self, x1e)
        # film
        m1 = (m1s+m1e) / 2

        # rho ---------------------------------------------------------------
        # s-state
        rhos_nv = 1 / HAPropsSI(
            'Vha',
            'T', Ts.nominal_value,
            'P', P.nominal_value,
            'Y', x1s_nv)
        rhos_sig = rhos_nv - (
            1 / HAPropsSI(
                'Vha',
                'T', Ts.nominal_value + Ts.std_dev,
                'P', P.nominal_value,
                'Y', x1s_nv)
        )
        rhos = ufloat(rhos_nv, abs(rhos_sig))
        # e-state
        rhoe_nv = 1 / HAPropsSI(
            'Vha',
            'T', Te.nominal_value,
            'P', P.nominal_value,
            'Y', x1e_nv)
        rhoe_sig = rhoe_nv - (
            1 / HAPropsSI(
                'Vha',
                'T', Te.nominal_value + Te.std_dev,
                'P', P.nominal_value,
                'Y', x1e_nv)
        )
        rhoe = ufloat(rhoe_nv, abs(rhoe_sig))
        # film
        rho = (rhos+rhoe) / 2

        # Bm1 ----------------------------------------------------------------
        Bm1 = (m1s - m1e)/(1-m1s)

        # T ------------------------------------------------------------------
        T = (Te+Ts) / 2

        # D12 ----------------------------------------------------------------
        D12 = 1.97e-5 * (101325/P) * pow(T/256, 1.685)

        # hfg -----------------------------------------------------------------
        # hg
        hg_nv = PropsSI(
            'H',
            'T', Ts.nominal_value,
            'Q', 1,
            'water')
        hg_sig = hg_nv - PropsSI(
            'H',
            'T', Ts.nominal_value + Ts.std_dev,
            'Q', 1,
            'water')
        hg = ufloat(hg_nv, abs(hg_sig))
        # hf
        hf_nv = PropsSI(
            'H',
            'T', Ts.nominal_value,
            'Q', 0,
            'water')
        hf_sig = hf_nv - PropsSI(
            'H',
            'T', Ts.nominal_value + Ts.std_dev,
            'Q', 0,
            'water')
        hf = ufloat(hf_nv, abs(hf_sig))
        # hfg
        hfg = hg - hf

        # hu -----------------------------------------------------------------
        hu = -hfg

        # hs -----------------------------------------------------------------
        hs = ufloat(0, 0)

        # cpv ----------------------------------------------------------------
        cpv_nv = HAPropsSI(
            'cp_ha',
            'P', P.nominal_value,
            'T', T.nominal_value,
            'Y', x1.nominal_value,
            )
        cpv_sig = cpv_nv - HAPropsSI(
            'cp_ha',
            'P', P.nominal_value,
            'T', T.nominal_value + T.std_dev,
            'Y', x1.nominal_value,
            )
        cpv = ufloat(cpv_nv, abs(cpv_sig))

        # he -----------------------------------------------------------------
        he = cpv * (Te - Ts)

        # cpl ----------------------------------------------------------------
        cpl_nv = PropsSI(
            'Cpmass',
            'T', T.nominal_value,
            'Q', 0,
            'water')
        cpl_sig = cpl_nv - PropsSI(
            'Cpmass',
            'T', T.nominal_value + T.std_dev,
            'Q', 0,
            'water')
        cpl = ufloat(cpl_nv, abs(cpl_sig))

        # hT -----------------------------------------------------------------
        hT = cpl * (Te - Ts)

        # qcu ----------------------------------------------------------------
        qcu = mddp * (hT - hu)

        # Ebe ----------------------------------------------------------------
        Ebe = self._SIGMA*Te**4

        # Ebs ----------------------------------------------------------------
        Ebs = self._SIGMA*Ts**4

        # qrs ----------------------------------------------------------------
        qrs = (Ebe - Ebs)/self._RAD_FACT

        # kv -----------------------------------------------------------------
        kv_nv = HAPropsSI(
            'k',
            'P', P.nominal_value,
            'T', T.nominal_value,
            'Y', x1.nominal_value,
            )
        kv_sig = kv_nv - HAPropsSI(
            'k',
            'P', P.nominal_value,
            'T', T.nominal_value + T.std_dev,
            'Y', x1.nominal_value,
            )
        kv = ufloat(kv_nv, abs(kv_sig))

        # alpha --------------------------------------------------------------
        alpha = kv / (rho*cpv)

        # Bh -----------------------------------------------------------------
        Bh = (hs-he) / (hu + (qcu+qrs)/mddp - hs)

        # M ------------------------------------------------------------------
        M = (m1 * self._M1) + ((1 - m1) * self._M2)

        # gamma1 -------------------------------------------------------------
        gamma1 = (1/rho) * (M/self._M1 - 1)

        # gamma2 -------------------------------------------------------------
        gamma2 = (1/rho) * (M/self._M2 - 1)

        # beta ---------------------------------------------------------------
        beta = 1/T

        # Delta_m ------------------------------------------------------------
        Delta_m = m1s - m1e

        # Delta_T ------------------------------------------------------------
        Delta_T = Ts - Te

        # mu -----------------------------------------------------------------
        mu_nv = HAPropsSI(
            'mu',
            'P', P.nominal_value,
            'T', T.nominal_value,
            'Y', x1.nominal_value,
            )
        mu_sig = mu_nv - HAPropsSI(
            'mu',
            'P', P.nominal_value,
            'T', T.nominal_value + T.std_dev,
            'Y', x1.nominal_value,
            )
        mu = ufloat(mu_nv, abs(mu_sig))

        # nu -----------------------------------------------------------------
        nu = mu/rho

        # set properties
        self._properties = dict(
            mddp=mddp,
            x1s=x1s,
            x1e=x1e,
            x1=x1,
            m1s=m1s,
            m1e=m1e,
            m1=m1,
            rhos=rhos,
            rhoe=rhoe,
            rho=rho,
            Bm1=Bm1,
            T=T,
            D12=D12,
            hfg=hfg,
            hu=hu,
            hs=hs,
            cpv=cpv,
            he=he,
            cpl=cpl,
            hT=hT,
            qcu=qcu,
            Ebe=Ebe,
            Ebs=Ebs,
            qrs=qrs,
            kv=kv,
            alpha=alpha,
            Bh=Bh,
            M=M,
            gamma1=gamma1,
            gamma2=gamma2,
            beta=beta,
            Delta_m=Delta_m,
            Delta_T=Delta_T,
            mu=mu,
            nu=nu,
            Ts=Ts,
        )

        # Update this fit
        for key, value in self._properties.items():
            self._this_fit[key] = value.nominal_value
            self._this_fit[f'sig_{key}'] = value.std_dev

    def _set_nondim_groups(self):
        Bm1 = self._properties['Bm1']
        mddp = self._properties['mddp']
        R = self._R
        rho = self._properties['rho']
        D12 = self._properties['D12']
        alpha = self._properties['alpha']
        Bh = self._properties['Bh']
        g = self._ACC_G
        nu = self._properties['nu']
        beta = self._properties['beta']
        Delta_T = self._properties['Delta_T']
        gamma1 = self._properties['gamma1']
        Delta_m = self._properties['Delta_m']
        mu = self._properties['mu']
        rhoe = self._properties['rhoe']
        rhos = self._properties['rhos']

        # Manual natural log error propagation -------------------------------
        # Bm1
        ln_Bm1_nv = log(1 + Bm1.nominal_value)
        ln_Bm1_sig = ln_Bm1_nv - log(1 + Bm1.nominal_value + Bm1.std_dev)
        ln_Bm1 = ufloat(ln_Bm1_nv, abs(ln_Bm1_sig))
        # Bh
        ln_Bh_nv = log(1 + Bh.nominal_value)
        ln_Bh_sig = ln_Bh_nv - log(1 + Bh.nominal_value + Bh.std_dev)
        ln_Bh = ufloat(ln_Bh_nv, abs(ln_Bh_sig))

        # ShR ----------------------------------------------------------------
        ShR = (mddp * R) / (ln_Bm1 * rho * D12)

        # NuR ----------------------------------------------------------------
        NuR = (mddp * R) / (ln_Bh * rho * alpha)

        # Le -----------------------------------------------------------------
        Le = D12/alpha

        # GrR_binary ---------------------------------------------------------
        GrR_binary = (g * R**3 / nu**2) * (beta*Delta_T + gamma1*rho*Delta_m)

        # GrR_primary --------------------------------------------------------
        GrR_primary = (g * R**3 / mu**2) * (rho * (rhos - rhoe))

        self._nondim_groups = dict(
            ShR=ShR,
            NuR=NuR,
            Le=Le,
            GrR_binary=GrR_binary,
            GrR_primary=GrR_primary,
        )

        # Update this fit
        for key, value in self._nondim_groups.items():
            self._this_fit[key] = value.nominal_value
            self._this_fit[f'sig_{key}'] = value.std_dev

    # ------------------------------------------------------------------------
    # Class helpers: internal use only

    def _ols_fit(self):
        sample = self._this_sample['m'].tolist()
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

    def _get_best_local_fit(self):
        # self._sample always has an odd length, so we use integer division.
        center = len(self._sample) // 2
        steps = int(self._steps)  # Explicitly make a copy
        delta = int(steps)  # Explicityly make a copy
        while center + steps + 1 <= len(self._sample):
            self._this_sample = (
                self._sample.iloc[center - steps: center + steps + 1, :]
            )
            fit = self._ols_fit()
            # With small sample sizes, b is sometimes zero.
            # If this is the case we want to continue.
            if fit['b'] == 0:
                steps += delta
                continue
            elif fit['sig_b']/abs(fit['b']) <= self._error:
                self._this_fit = fit
                return
            else:
                steps += delta
        # We did not find a fit
        self._this_fit = None

    def _evaluate_fit(self):
        # Prepare the data
        y = [i.nominal_value for i in self._this_sample['m']]
        sig = [i.std_dev for i in self._this_sample['m']]
        x = list(range(len(y)))  # Always indexed at zero

        # Fit parameters
        a = self._this_fit['a']
        b = self._this_fit['b']

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

        # update this fit
        self._this_fit['r2'] = R2
        self._this_fit['q'] = Q
        self._this_fit['chi2'] = merit_value
        self._this_fit['nu_chi'] = len(x) - 2
        self._this_fit['exp_id'] = self._experiment_id
        self._this_fit['idx'] = self._idx
