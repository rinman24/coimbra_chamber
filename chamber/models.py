"""Docstring."""
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI

import scipy.optimize as opt

import chamber.const as const


class Model(object):
    """Object to hold the state of a heat and mass transfer model."""

    learning_rate = 0.05

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
        self.params['Ra'] = None
        self.params['Pr'] = None
        self.params['Le'] = None
        self.params['Gr_h'] = None

        # Radiation properties, default to black surfaces.
        self.rad_props = dict()
        self.rad_props['eps_1'] = 1
        self.rad_props['eps_2'] = 1
        self.rad_props['eps_3'] = 1

        # Container for solution of model
        self.solution = None

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
                    self.props['D_12'], self.props['h_fg'], self.props['k_m'],
                    self.props['m_1e'], self.props['m_1s'], self.props['mu_m'],
                    self.props['nu_m'], self.props['rho_m'], self.props['T_s'],
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
               'Ra:\t{:.6g}\t[-]\n'
               'Pr:\t{:.6g}\t[-]\n'
               'Le:\t{:.6g}\t\t[-]\n'
               'Gr_h:\t{:.6g}\t[-]\n')\
            .format(self.params['Ra'], self.params['Pr'],
                    self.params['Le'], self.params['Gr_h'])
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
        """Use CoolProp to populate self.props."""

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

        self.props['c_pm'] = HAPropsSI('cp',
                                       'T', self.ref_state['T_m'],
                                       'Y', self.ref_state['x_1'],
                                       'P', self.settings['P'])

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

        # Rayleigh number
        self.params['Ra'] = const.ACC_GRAV * beta_term * \
            pow(self.settings['L_t'], 3) /\
            (self.props['alpha_m'] * self.props['nu_m'])

        # Prandtl number
        self.params['Pr'] = self.props['c_pm'] * self.props['mu_m'] /\
            self.props['k_m']

        # Le number
        self.params['Le'] = self.props['D_12'] * self.props['rho_m'] /\
            (self.props['k_m'] / self.props['c_pm'])

        # Grashof number for heat transfer
        self.params['Gr_h'] = const.ACC_GRAV * self.props['beta_m'] *\
            delta_t * pow(self.settings['L_t'], 3) / pow(self.props['nu_m'], 2)

    def solve(self):
        """Docstring."""
        delta, count = 1, 0
        sol = [1 for _ in range(len(self.solution))]
        while abs(delta) > 1e-9:
            # Get the solution with the current properties evaluated at
            # self.temp_s:
            sol = opt.fsolve(self.eval_model, sol)
            self.set_solution(sol)

            # Make new guess @ self.props['T_s'] based on self.solution['T_s']:
            delta = self.solution['T_s'] - self.props['T_s']
            self.props['T_s'] += self.learning_rate * delta

            # Evaluate the new properties before solving again:
            self.eval_props()

            # Bookkeeping
            count += 1
        self.eval_params()
        return count

    def run(self):
        """Docstring."""
        self.solve()
        self.describe()

    # @ staticmethod
    def e_b(temp):
        """Docstring."""
        return const.SIGMA * pow(temp, 4)

    # Methods that are defined here but overwritten by children.

    def eval_model(self, vec_in):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass

    def set_solution(self):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass

    def show_solution(self):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass


class OneDimIsoLiqNoRad(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """The f_matrix and j_matrix are constant, can be set in __init__()."""
        super(OneDimIsoLiqNoRad, self)\
            .__init__(settings, ref=ref, rule=rule)

        self.solution = dict(mddp=None, q_cs=None, T_s=None)

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

    def set_solution(self, solution):
        """Docstring."""
        self.solution['mddp'] = solution[0]
        self.solution['q_cs'] = solution[1]
        self.solution['T_s'] = solution[2]

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

        self.solution = dict(mddp=None, q_cs=None, q_rad=None, T_s=None)

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

    def set_solution(self, solution):
        """Docstring."""
        self.solution['mddp'] = solution[0]
        self.solution['q_cs'] = solution[1]
        self.solution['q_rad'] = solution[2]
        self.solution['T_s'] = solution[3]

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


# class OneDimIsoLiqBlackGrayRad(OneDimIsoLiqBlackRad):
#     """Docstring."""
