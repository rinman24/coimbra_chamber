"""Docstring."""
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI

import numpy as np

from scipy import integrate
import scipy.optimize as opt

import chamber.const as const


class Model(object):
    """Object to hold the state of a heat and mass transfer model."""

    learning_rate = 5e-3

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Constructor."""

        # Settings:
        self.settings = dict()
        self.settings['L_t'] = settings['L_t']
        self.settings['P'] = settings['P']
        self.settings['ref'] = ref
        self.settings['rule'] = rule
        self.settings['T_DP'] = settings['T_DP']
        self.settings['T_e'] = settings['T_e']

        # Properties:
        self.props = dict()
        # Default: temp_s = mean of temp_e and temp_dp
        self.props['alpha_m'] = None
        self.props['beta_m'] = None
        self.props['beta*_m'] = None
        self.props['c_pm'] = None
        self.props['c_p1'] = None
        self.props['D_12'] = None
        self.props['h_fg'] = None
        self.props['k_m'] = None
        self.props['m_1e'] = None
        self.props['m_1s'] = None
        self.props['mu_m'] = None
        self.props['nu_m'] = None
        self.props['rho_m'] = None
        self.props['T_s'] = \
            (self.settings['T_e'] + self.settings['T_DP']) / 2
        self.props['x_1e'] = None
        self.props['x_1s'] = None

        # Reference state:
        self.ref_state = dict()
        self.ref_state['x_1'] = None
        self.ref_state['m_1'] = None
        self.ref_state['T_m'] = None

        # Dimensionless parameters:
        self.params = dict()
        self.params['Gr_h'] = None
        self.params['Gr_mt'] = None
        self.params['Ja_v'] = None
        self.params['Le'] = None
        self.params['Pr'] = None
        self.params['Ra'] = None
        self.params['Ra_h'] = None
        self.params['Ra_mt'] = None

        # Radiation properties, default to black surfaces:
        self.rad_props = dict()
        self.rad_props['eps_1'] = 1
        self.rad_props['eps_2'] = 1
        self.rad_props['eps_3'] = 1

        # Attribute for solution of model:
        self.solution = dict()

        # Hidden attribute for unknowns in model:
        self._unknowns = []

        # Attribute for the initial guess
        self.initial_guess = []

        # Populate self.props:
        self.eval_props()

        # Populate self.params:
        self.eval_params()

    def __repr__(self):
        """print(repr(<MODEL>))"""
        pt1 = "settings = dict(L_t={}, P={}, T_DP={}, T_e={})\n"\
            .format(self.settings['L_t'], self.settings['P'],
                    self.settings['T_DP'], self.settings['T_e'])

        pt2 = type(self).__name__ + "(settings, ref='{}', rule='{}')"\
            .format(self.settings['ref'], self.settings['rule'])

        return pt1 + pt2

    def __str__(self):
        """print(<MODEL>)"""
        return ('------ Settings ------\n'
                'L_t:\t{:.6g}\t[m]\n'
                'P:\t{:.6g}\t[Pa]\n'
                'T_DP:\t{:.6g}\t[K]\n'
                'T_e:\t{:.6g}\t[K]\n'
                'ref:\t{}\t[-]\n'
                'rule:\t{}\t[-]\n')\
            .format(self.settings['L_t'], self.settings['P'],
                    self.settings['T_DP'], self.settings['T_e'],
                    self.settings['ref'], self.settings['rule'])

    def show_settings(self, show_res=True):
        res = ('------ Settings ------\n'
               'L_t:\t{:.6g}\t[m]\n'
               'P:\t{:.6g}\t[Pa]\n'
               'T_DP:\t{:.6g}\t[K]\n'
               'T_e:\t{:.6g}\t[K]\n'
               'ref:\t{}\t[-]\n'
               'rule:\t{}\t[-]\n')\
            .format(self.settings['L_t'], self.settings['P'],
                    self.settings['T_DP'], self.settings['T_e'],
                    self.settings['ref'], self.settings['rule'])
        if show_res:
            print(res)
        else:
            return res

    def show_props(self, show_res=True):
        """Docstring."""
        res = ('--------------- Properties ---------------\n'
               'alpha_m:\t{:.6g}\t[m^2 / s]\n'
               'beta_m:\t\t{:.6g}\t[1 / K]\n'
               'beta*_m:\t{:.6g}\t[-]\n'
               'c_pm:\t\t{:.6g}\t\t[J / kg]\n'
               'c_p1:\t\t{:.6g}\t\t[J / kg]\n'
               'D_12:\t\t{:.6g}\t[m^2 / s]\n'
               'h_fg:\t\t{:.6g}\t[J / kg]\n'
               'k_m:\t\t{:.6g}\t[W / m K]\n'
               'm_1e:\t\t{:.6g}\t[-]\n'
               'm_1s:\t\t{:.6g}\t[-]\n'
               'mu_m:\t\t{:.6g}\t[kg / m s]\n'
               'nu_m:\t\t{:.6g}\t[m^2 / s]\n'
               'rho_m:\t\t{:.6g}\t\t[kg / m^3]\n'
               'T_s:\t\t{:.6g}\t\t[K]\n'
               'x_1e:\t\t{:.6g}\t[-]\n'
               'x_1s:\t\t{:.6g}\t[-]\n')\
            .format(self.props['alpha_m'], self.props['beta_m'],
                    self.props['beta*_m'], self.props['c_pm'],
                    self.props['c_p1'], self.props['D_12'],
                    self.props['h_fg'], self.props['k_m'],
                    self.props['m_1e'], self.props['m_1s'],
                    self.props['mu_m'], self.props['nu_m'],
                    self.props['rho_m'], self.props['T_s'],
                    self.props['x_1e'], self.props['x_1s'])
        if show_res:
            print(res)
        else:
            return res

    def show_rad_props(self, show_res=True):
        """Docstring."""
        res = ('--- Rad. Props. ---\n'
               'eps_1:\t{:.6g}\t[-]\n'
               'eps_2:\t{:.6g}\t[-]\n'
               'eps_3:\t{:.6g}\t[-]\n')\
            .format(self.rad_props['eps_1'], self.rad_props['eps_2'],
                    self.rad_props['eps_3'])
        if show_res:
            print(res)
        else:
            return res

    def show_ref_state(self, show_res=True):
        """Docstring."""
        res = ('-------- Ref. State --------\n'
               'm_1:\t{:.6g}\t[-]\n'
               'T_m:\t{:.6g}\t\t[K]\n'
               'x_1:\t{:.6g}\t[-]\n')\
            .format(self.ref_state['m_1'], self.ref_state['T_m'],
                    self.ref_state['x_1'])
        if show_res:
            print(res)
        else:
            return res

    def show_params(self, show_res=True):
        """Docstring."""
        res = ('-------- Parameters --------\n'
               'Gr_h:\t{:.6g}\t[-]\n'
               'Gr_mt:\t{:.6g}\t\t[-]\n'
               'Ja_v:\t{:.6g}\t[-]\n'
               'Le:\t{:.6g}\t\t[-]\n'
               'Pr:\t{:.6g}\t[-]\n'
               'Ra:\t{:.6g}\t[-]\n'
               'Ra_h:\t{:.6g}\t[-]\n'
               'Ra_mt:\t{:.6g}\t\t[-]\n')\
            .format(self.params['Gr_h'], self.params['Gr_mt'],
                    self.params['Ja_v'], self.params['Le'],
                    self.params['Pr'], self.params['Ra'],
                    self.params['Ra_h'], self.params['Ra_mt'])
        if show_res:
            print(res)
        else:
            return res

    def describe(self):
        """Docstring."""
        self.show_settings()
        self.show_props()
        self.show_rad_props()
        self.show_ref_state()
        self.show_params()
        self.show_solution()

    @staticmethod
    def get_ref_state(e_state, s_state, rule):
        """Calculate ref state based on rule."""
        return {'mean': lambda e, s: (e + s) / 2,
                'one-third': lambda e, s: s + (e - s) / 3
                }[rule](e_state, s_state)

    @staticmethod
    def get_bin_diff_coeff(ref_temp, pressure, ref):
        """Get binary diffusion coefficient based on ref."""
        # See Table A.17a in `Mass Transfer` by Mills and Coimbra for details.
        return {'Mills': lambda t, p: 1.97e-5 * (1 / p) * pow(t / 256, 1.685),
                'Marrero': lambda t, p: 1.87e-10 * pow(t, 2.072) / p
                }[ref](ref_temp, pressure / 101325)

    def eval_props(self):
        """Use CoolProp to populate self.props.

        Everything here associated with Ts is a guess."""

        # Reference states:
        self.props['x_1e'] = HAPropsSI('Y',
                                       'T', self.settings['T_e'],
                                       'T_dp', self.settings['T_DP'],
                                       'P', self.settings['P'])

        self.props['x_1s'] = HAPropsSI('Y',
                                       'T', self.props['T_s'], 'RH', 1,
                                       'P', self.settings['P'])

        self.ref_state['x_1'] = self.get_ref_state(self.props['x_1e'],
                                                   self.props['x_1s'],
                                                   self.settings['rule'])

        self.ref_state['m_1'] = (self.ref_state['x_1'] * const.M1) /\
            (self.ref_state['x_1'] * const.M1 +
             (1 - self.ref_state['x_1']) * const.M2)

        self.ref_state['T_m'] = self.get_ref_state(self.settings['T_e'],
                                                   self.props['T_s'],
                                                   self.settings['rule'])

        # Primary properties:
        # These can be calculated with the information we have now as opposed
        # composite properties that can be calculated as groups of primary
        # properties; e.g., alpha = k / (rho * c)
        self.props['beta_m'] = 1 / self.ref_state['T_m']

        self.props['c_pm'] = HAPropsSI('cp_ha',
                                       'T', self.ref_state['T_m'],
                                       'Y', self.ref_state['x_1'],
                                       'P', self.settings['P'])

        self.props['c_p1'] = PropsSI('Cpmass',
                                     'P', self.settings['P'] *
                                     self.ref_state['x_1'],
                                     'Q', 1,
                                     'Water')

        self.props['c_pliq'] = PropsSI('Cpmass',
                                       'T', self.ref_state['T_m'],
                                       'Q', 0,
                                       'water')

        self.props['D_12'] = self.get_bin_diff_coeff(self.ref_state['T_m'],
                                                     self.settings['P'],
                                                     self.settings['ref'])

        self.props['h_fg'] = \
            PropsSI('H', 'T', self.props['T_s'], 'Q', 1, 'water') - \
            PropsSI('H', 'T', self.props['T_s'], 'Q', 0, 'water')

        self.props['k_m'] = HAPropsSI('k',
                                      'T', self.ref_state['T_m'],
                                      'Y', self.ref_state['x_1'],
                                      'P', self.settings['P'])

        self.props['m_1e'] = (self.props['x_1e'] * const.M1) /\
            (self.props['x_1e'] * const.M1 +
             (1 - self.props['x_1e']) * const.M2)

        self.props['m_1s'] = (self.props['x_1s'] * const.M1) /\
            (self.props['x_1s'] * const.M1 +
             (1 - self.props['x_1s']) * const.M2)

        self.props['mu_m'] = HAPropsSI('mu',
                                       'T', self.ref_state['T_m'],
                                       'Y', self.ref_state['x_1'],
                                       'P', self.settings['P'])

        self.props['rho_m'] = 1 / HAPropsSI('Vha',
                                            'T', self.ref_state['T_m'],
                                            'Y', self.ref_state['x_1'],
                                            'P', self.settings['P'])

        # Composite properties
        self.props['alpha_m'] = self.props['k_m'] /\
            (self.props['c_pm'] * self.props['rho_m'])

        self.props['nu_m'] = self.props['mu_m'] / self.props['rho_m']

        self.props['beta*_m'] = (const.M2 - const.M1) /\
            (self.ref_state['m_1'] * (const.M2 - const.M1) + const.M1)

    def eval_params(self):
        """Use self.props to calculate the self.params"""
        delta_t = self.props['T_s'] - self.settings['T_e']

        delta_m = self.props['m_1s'] - self.props['m_1e']

        beta_term = (self.props['beta_m'] * (delta_t) +
                     self.props['beta*_m'] * (delta_m))

        # Grashof number for heat transfer
        self.params['Gr_h'] = const.ACC_GRAV *\
            self.props['beta_m'] * delta_t * pow(self.settings['L_t'], 3) /\
            pow(self.props['nu_m'], 2)

        # Grashof number for mass transfer
        self.params['Gr_mt'] = const.ACC_GRAV *\
            self.props['beta*_m'] * delta_m * pow(self.settings['L_t'], 3) /\
            pow(self.props['nu_m'], 2)

        # vapor-phase Jakob number
        if self.settings['rule'] == 'mean':
            self.params['Ja_v'] = self.props['c_p1'] * abs(delta_t) /\
                self.props['h_fg']
        elif self.settings['rule'] == 'one-third':
            self.params['Ja_v'] = self.props['c_pm'] * abs(delta_t) /\
                self.props['h_fg']

        # Le number
        self.params['Le'] = self.props['D_12'] * self.props['rho_m'] /\
            (self.props['k_m'] / self.props['c_pm'])

        # Prandtl number
        self.params['Pr'] = self.props['c_pm'] * self.props['mu_m'] /\
            self.props['k_m']

        # Rayleigh number
        self.params['Ra'] = const.ACC_GRAV * beta_term * \
            pow(self.settings['L_t'], 3) /\
            (self.props['alpha_m'] * self.props['nu_m'])

        # Rayleigh number for heat transfer
        self.params['Ra_h'] = const.ACC_GRAV *\
            self.props['beta_m'] * delta_t * pow(self.settings['L_t'], 3) /\
            (self.props['alpha_m'] * self.props['nu_m'])

        # Rayleigh number for heat transfer
        self.params['Ra_mt'] = const.ACC_GRAV *\
            self.props['beta*_m'] * delta_m * pow(self.settings['L_t'], 3) /\
            (self.props['alpha_m'] * self.props['nu_m'])

    def solve(self):
        """Docstring."""
        delta, count = 1, 0
        sol = self.initial_guess
        while abs(delta) > 1e-9:
            # Get the solution with the current properties evaluated at
            # self.temp_s:
            sol = opt.fsolve(self.eval_model, sol)
            self.set_solution(sol)

            # Make new guess @ self.props['T_s'] based on self.solution['T_s']:
            delta = self.solution['T_s'] - self.props['T_s']
            # print(delta)
            self.props['T_s'] = self.props['T_s'] + (self.learning_rate*delta)

            # Evaluate the new properties before solving again:
            self.eval_props()
            self.eval_Eb()
            self.eval_Jsys()

            # Bookkeeping
            count += 1
        self.eval_params()
        return count

    def run(self):
        """Docstring."""
        self.solve()
        self.describe()

    @ staticmethod
    def e_b(temp):
        """Docstring."""
        return const.SIGMA * pow(temp, 4)

    def set_solution(self, solution):
        """Docstring."""
        self.solution = {key: solution[index]
                         for (index, key)
                         in enumerate(self._unknowns)}

    # Methods that are defined here but overwritten by children.
    def eval_Eb(self):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass

    def eval_Jsys(self):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass

    def eval_model(self, vec_in):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass

    def show_solution(self):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass


class SpaldingIsoNoRadHydroStatic(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Docstring."""
        super(SpaldingIsoNoRadHydroStatic, self)\
            .__init__(settings, ref=ref, rule=rule)

        self._unknowns = ['mddp', 'T_s']
        self.set_solution([None] * len(self._unknowns))
        self.initial_guess = [1e-6, self.settings['T_DP']]

    def eval_model(self, vec_in):
        """Docstring."""
        mddp,  T_s = vec_in
        res = [0 for _ in range(len(self.solution))]

        rho_m = self.props['rho_m']
        D_12 = self.props['D_12']
        L = self.settings['L_t']
        m_1e = self.props['m_1e']
        T_e = self.settings['T_e']
        alpha_m = self.props['alpha_m']
        c_pm = self.props['c_pm']
        h_fg = self.props['h_fg']

        g_m = rho_m * D_12 / L
        B_m = (self.props['m_1s'] - m_1e) / (1 - self.props['m_1s'])

        g_h = rho_m * alpha_m / L
        B_h = c_pm * (T_e-T_s)/(h_fg)

        res[0] = mddp - (g_m * B_m)
        res[1] = mddp - (g_h * B_h)
        return res

    def show_solution(self, show_res=True):
        """Docstring."""
        # If the model has been solved
        if self.solution['mddp']:
            res = ('------------- Solution -------------\n'
                   'mddp:\t{:.6g}\t[kg / m^2 s]\n'
                   'T_s:\t{:.6g}\t\t[K]\n')\
                .format(self.solution['mddp'], self.solution['T_s'])
        else:
            res = ('------------- Solution -------------\n'
                   '......... Not solved yet ...........\n')

        if show_res:
            print(res)
        else:
            return res


class SpaldingIsoHydroStatic(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Docstring."""
        super(SpaldingIsoHydroStatic, self)\
            .__init__(settings, ref=ref, rule=rule)

        self._unknowns = ['mddp', 'q_rs', 'T_s']
        self.set_solution([None] * len(self._unknowns))
        self.initial_guess = [1e-6, 0.1, self.settings['T_DP']]

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_rs, T_s = vec_in
        res = [0 for _ in range(len(self.solution))]

        rho_m = self.props['rho_m']
        D_12 = self.props['D_12']
        L = self.settings['L_t']
        m_1e = self.props['m_1e']
        T_e = self.settings['T_e']
        alpha_m = self.props['alpha_m']
        c_pm = self.props['c_pm']
        h_fg = self.props['h_fg']
        sig = const.SIGMA

        g_m = rho_m * D_12 / L
        B_m = (self.props['m_1s'] - m_1e) / (1 - self.props['m_1s'])

        g_h = rho_m * alpha_m / L
        B_h = c_pm * (T_e - T_s) / (h_fg - (q_rs/mddp))

        res[0] = mddp - (g_m * B_m)
        res[1] = q_rs - sig*(pow(T_e, 4) - pow(T_s, 4))
        res[2] = mddp - (g_h * B_h)
        return res

    def show_solution(self, show_res=True):
        """Docstring."""
        # If the model has been solved
        if self.solution['mddp']:
            res = ('------------- Solution -------------\n'
                   'mddp:\t{:.6g}\t[kg / m^2 s]\n'
                   'q_rs:\t{:.6g}\t[W / m^2]\n'
                   'T_s:\t{:.6g}\t\t[K]\n')\
                .format(self.solution['mddp'], self.solution['q_rs'], self.solution['T_s'])
        else:
            res = ('------------- Solution -------------\n'
                   '......... Not solved yet ...........\n')

        if show_res:
            print(res)
        else:
            return res


class SpaldingHydroStatic(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Docstring."""
        super(SpaldingHydroStatic, self)\
            .__init__(settings, ref=ref, rule=rule)

        self._unknowns = ['mddp', 'q_cu', 'q_rs', 'T_s']
        self.set_solution([None] * len(self._unknowns))
        self.initial_guess = [1e-6, 0.1, 0.1, self.settings['T_DP']]

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_cu, q_rs, T_s = vec_in
        res = [0 for _ in range(len(self.solution))]

        rho_m = self.props['rho_m']
        D_12 = self.props['D_12']
        L = self.settings['L_t']
        m_1e = self.props['m_1e']
        T_e = self.settings['T_e']
        alpha_m = self.props['alpha_m']
        c_pm = self.props['c_pm']
        h_fg = self.props['h_fg']
        sig = const.SIGMA
        c_pliq = self.props['c_pliq']

        g_m = rho_m * D_12 / L
        B_m = (self.props['m_1s'] - m_1e) / (1 - self.props['m_1s'])

        g_h = rho_m * alpha_m / L
        B_h = c_pm * (T_e - T_s) / (h_fg - ((q_rs+q_cu)/mddp))

        res[0] = mddp - (g_m * B_m)
        res[1] = q_cu - mddp*c_pliq*(T_e-T_s)
        res[2] = q_rs - sig*(pow(T_e, 4) - pow(T_s, 4))
        res[3] = mddp - (g_h * B_h)
        return res

    def show_solution(self, show_res=True):
        """Docstring."""
        # If the model has been solved
        if self.solution['mddp']:
            res = ('------------- Solution -------------\n'
                   'mddp:\t{:.6g}\t[kg / m^2 s]\n'
                   'q_cu:\t{:.6g}\t[W / m^2]\n'
                   'q_rs:\t{:.6g}\t[W / m^2]\n'
                   'T_s:\t{:.6g}\t\t[K]\n')\
                .format(self.solution['mddp'], self.solution['q_cu'],
                        self.solution['q_rs'], self.solution['T_s'])
        else:
            res = ('------------- Solution -------------\n'
                   '......... Not solved yet ...........\n')

        if show_res:
            print(res)
        else:
            return res


class OneDimIsoLiqNoRad(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """The f_matrix and j_matrix are constant, can be set in __init__()."""
        super(OneDimIsoLiqNoRad, self)\
            .__init__(settings, ref=ref, rule=rule)

        self._unknowns = ['mddp', 'q_cs', 'T_s']
        self.set_solution([None] * len(self._unknowns))
        self.initial_guess = [1e-6, 10, self.settings['T_DP']]

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_cs, T_s = vec_in
        res = [0 for _ in range(len(self.solution))]
        res[0] = q_cs + \
            (self.props['k_m'] / self.settings['L_t']) * \
            (self.settings['T_e'] - T_s)
        res[1] = mddp + \
            (self.props['rho_m'] * self.props['D_12'] /
             self.settings['L_t']) * \
            (self.props['m_1e'] - self.props['m_1s'])
        res[2] = mddp * self.props['h_fg'] + q_cs
        return res

    def show_solution(self, show_res=True):
        """Docstring."""
        # If the model has been solved
        if self.solution['mddp']:
            res = ('------------- Solution -------------\n'
                   'mddp:\t{:.6g}\t[kg / m^2 s]\n'
                   'q_cs:\t{:.6g}\t[W / m^2]\n'
                   'T_s:\t{:.6g}\t\t[K]\n')\
                .format(self.solution['mddp'], self.solution['q_cs'],
                        self.solution['T_s'])
        else:
            res = ('------------- Solution -------------\n'
                   '......... Not solved yet ...........\n')

        if show_res:
            print(res)
        else:
            return res


class OneDimIsoLiqBlackRad(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Docstring."""
        super(OneDimIsoLiqBlackRad, self)\
            .__init__(settings, ref=ref, rule=rule)

        self._unknowns = ['mddp', 'q_cs', 'q_rad', 'T_s']
        self.set_solution([None] * len(self._unknowns))
        self.initial_guess = [1e-6, 10, 10, self.settings['T_DP']]

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_cs, q_rad, T_s = vec_in
        res = [0 for _ in range(len(self.solution))]
        res[0] = q_cs + \
            (self.props['k_m'] / self.settings['L_t']) * \
            (self.settings['T_e'] - T_s)
        res[1] = mddp + \
            (self.props['rho_m'] * self.props['D_12'] /
             self.settings['L_t']) * \
            (self.props['m_1e'] - self.props['m_1s'])
        res[2] = mddp * self.props['h_fg'] + q_cs + q_rad
        res[3] = q_rad + \
            const.SIGMA * (pow(self.settings['T_e'], 4) - pow(T_s, 4))
        return res

    def show_solution(self, show_res=True):
        """Docstring."""
        # If the model has been solved
        if self.solution['mddp']:
            res = ('------------- Solution -------------\n'
                   'mddp:\t{:.6g}\t[kg / m^2 s]\n'
                   'q_cs:\t{:.6g}\t[W / m^2]\n'
                   'q_rad:\t{:.6g}\t[W / m^2]\n'
                   'T_s:\t{:.6g}\t\t[K]\n')\
                .format(self.solution['mddp'], self.solution['q_cs'],
                        self.solution['q_rad'], self.solution['T_s'])
        else:
            res = ('------------- Solution -------------\n'
                   '......... Not solved yet ...........\n')

        if show_res:
            print(res)
        else:
            return res


class OneDimIsoLiqBlackGrayRad(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Docstring."""
        super(OneDimIsoLiqBlackGrayRad, self)\
            .__init__(settings, ref=ref, rule=rule)

        # Blackbody emissive power
        self.Eb = [0 for _ in range(3)]

        # Emissivity
        self.eps = settings['eps']

        # View factor matrix
        self.F_matx = np.zeros((3, 3))

        # Radiosity system
        self.Amatx_J = np.zeros(shape=(3, 3))
        self.Bmatx_J = np.zeros(shape=(3,))
        self.J_sol = None

        self._unknowns = ['mddp', 'q_cs', 'q_rad', 'T_s']
        self.set_solution([None] * len(self._unknowns))
        self.initial_guess = [1e-6, 10, 10, self.settings['T_DP']]

        # Populate self.Eb
        self.eval_Eb()

        # Populate self.F_matx
        self.eval_F_matx()

        # Populate radiosity system
        self.eval_Jsys()

    @staticmethod
    def get_Fab_c14(r_a, r_b, s):
        """Docstring."""

        # Get view factor a->b from configuration 14
        R_a = r_a/s
        R_b = r_b/s
        x = 1 + ((1 + pow(R_b, 2)) / (pow(R_a, 2)))
        return 0.5 * (x - pow(pow(x, 2) - 4 * pow(R_b / R_a, 2), 1/2))

    def eval_F_matx(self):
        """Calculate the view factor matrix"""
        # View factors from material 0
        self.F_matx[0, 2] = self.get_Fab_c14(0.05, 0.05, self.settings['L_t'])
        self.F_matx[0, 1] = 1 - self.F_matx[0, 2]

        # View factors from material 2
        self.F_matx[2, 0] = self.get_Fab_c14(0.05, 0.05, self.settings['L_t'])
        self.F_matx[2, 1] = 1 - self.F_matx[2, 0]

        # View factors from material 1
        self.F_matx[1, 0] = np.pi * pow(0.05, 2) * self.F_matx[0, 1] /\
            (2 * np.pi * 0.05 * self.settings['L_t'])
        self.F_matx[1, 2] = np.pi * pow(0.05, 2) * self.F_matx[2, 1] /\
            (2 * np.pi * 0.05 * self.settings['L_t'])
        self.F_matx[1, 1] = 1 - self.F_matx[1, 2] - self.F_matx[1, 0]

    def eval_Eb(self):
        """Evaluate the blackbody emissive power for each surface"""
        self.Eb[0] = self.e_b(self.props['T_s'])
        self.Eb[1] = self.e_b(self.settings['T_e'])
        self.Eb[2] = self.e_b(self.settings['T_e'])

    def eval_Jsys(self):
        """Evaluate matrices A and B from radiosity system (J system)"""
        ident = np.identity(3)
        for m in range(3):
            self.Bmatx_J[m] = self.eps[m] * self.Eb[m]
            for n in range(3):
                self.Amatx_J[m, n] = - (1 - self.eps[m]) * self.F_matx[m, n] +\
                    ident[m, n]

    def solve_J(self):
        """Solve the radiosity system to obtain the J at each surface"""
        return np.linalg.solve(self.Amatx_J, self.Bmatx_J)

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_cs, q_rad, T_s = vec_in

        # Solve the J system first
        self.J_sol = self.solve_J()

        # Solve the model
        res = [0 for _ in range(len(self.solution))]
        res[0] = q_cs + \
            (self.props['k_m'] / self.settings['L_t']) * \
            (self.settings['T_e'] - T_s)
        res[1] = mddp + \
            (self.props['rho_m'] * self.props['D_12'] /
             self.settings['L_t']) * \
            (self.props['m_1e'] - self.props['m_1s'])
        res[2] = mddp * self.props['h_fg'] + q_cs + q_rad
        res[3] = q_rad + \
            (- self.Eb[0] + sum(self.J_sol[:] * self.F_matx[0, :]))
        return res

    def show_solution(self, show_res=True):
        """Docstring."""
        # If the model has been solved
        if self.solution['mddp']:
            res = ('------------- Solution -------------\n'
                   'mddp:\t{:.6g}\t[kg / m^2 s]\n'
                   'q_cs:\t{:.6g}\t[W / m^2]\n'
                   'q_rad:\t{:.6g}\t[W / m^2]\n'
                   'T_s:\t{:.6g}\t\t[K]\n')\
                .format(self.solution['mddp'], self.solution['q_cs'],
                        self.solution['q_rad'], self.solution['T_s'])
        else:
            res = ('------------- Solution -------------\n'
                   '......... Not solved yet ...........\n')

        if show_res:
            print(res)
        else:
            return res


class OneDimIsoLiqIntEmitt(Model):

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Docstring."""
        super(OneDimIsoLiqIntEmitt, self)\
            .__init__(settings, ref=ref, rule=rule)

        self.alpha_w = settings['alpha_w']
        self.lamb = settings['lamb']
        self.eps = None

        self._unknowns = ['mddp', 'q_cs', 'q_rad', 'T_s']
        self.set_solution([None] * len(self._unknowns))

    @ staticmethod
    def get_stigma(lamb, Temp):
        """Get stigma value."""
        # lamb in [micrometer], Temp in [Kelvin]
        # C_2 is the constant appearing in the Planck's law
        # for the monochromatic emissive power for a black surface
        return const.C_2/(lamb * Temp)

    @staticmethod
    def get_internal_fractional_value(stigma):
        """Integrate internal fractional function."""
        # stigma must be a floting point

        def fun(x): return (15 / (4 * np.pi**4)) * pow(x, 4) * np.exp(x) /\
            pow(np.exp(x) - 1, 2)

        x_vec = np.arange(stigma, 100., 0.01)
        y_vec = [fun(x) for x in x_vec]

        return integrate.trapz(y_vec, x_vec)

    def eval_eps(self, alpha, lamb):
        """Evaluate the emissivity using the internal emittance method."""

        absorptance = [1 - pow(10, - alpha * self.settings['L_t'] / np.log(10))
                       for alpha in alpha]
        self.eps = absorptance[1] * 0.005

        for k in range(1, len(absorptance)):

            stigma_0 = self.get_stigma(lamb[k - 1], self.props['T_s'])
            stigma_1 = self.get_stigma(lamb[k], self.props['T_s'])

            fi_0 = self.get_internal_fractional_value(stigma_0)
            fi_1 = self.get_internal_fractional_value(stigma_1)

            self.eps += absorptance[k] * (fi_1 - fi_0)

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_cs, q_rad, T_s = vec_in

        # Evaluate the emissivity of the water
        self.eval_eps(self.alpha_w, self.lamb)

        # Solve the model
        res = [0 for _ in range(len(self.solution))]
        res[0] = q_cs + \
            (self.props['k_m'] / self.settings['L_t']) * \
            (self.settings['T_e'] - T_s)
        res[1] = mddp + \
            (self.props['rho_m'] * self.props['D_12'] /
             self.settings['L_t']) * \
            (self.props['m_1e'] - self.props['m_1s'])
        res[2] = mddp * self.props['h_fg'] + q_cs + q_rad
        res[3] = q_rad + \
            (-1 * self.eps * 4 * const.SIGMA * pow(T_s, 3) *
             (T_s - self.settings['T_e']))
        return res

    def show_solution(self, show_res=True):
        """Docstring."""
        # If the model has been solved
        if self.solution['mddp']:
            res = ('------------- Solution -------------\n'
                   'mddp:\t{:.6g}\t[kg / m^2 s]\n'
                   'q_cs:\t{:.6g}\t[W / m^2]\n'
                   'q_rad:\t{:.6g}\t[W / m^2]\n'
                   'T_s:\t{:.6g}\t\t[K]\n')\
                .format(self.solution['mddp'], self.solution['q_cs'],
                        self.solution['q_rad'], self.solution['T_s'])
        else:
            res = ('------------- Solution -------------\n'
                   '......... Not solved yet ...........\n')

        if show_res:
            print(res)
        else:
            return res
