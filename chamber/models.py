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

        # Radiation properties
        self.eps = [1, 1, 1]  # Default to black surface

        # Container for solution of model
        self.solution = None

        # Populate self.props:
        self.eval_props()

    def __repr__(self):
        """print(repr(<MODEL>))"""
        pt1 = "settings = dict(L_t={}, P={}, T_DP={}, T_e={})"\
            .format(self.settings['L_t'], self.settings['P'],
                    self.settings['T_DP'], self.settings['T_e'])

        pt2 = "\nModel(settings, ref='{}', rule='{}')"\
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
        res = ('---- Parameters ----\n'
               'Ra:\t{:.6g}\t[-]\n')\
            .format(self.params['Ra'])
        if show_res:
            print(res)
        else:
            return res

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

        delta_t = self.props['T_s'] - self.settings['T_e']

        delta_m = self.props['m_1s'] - self.props['m_1e']

        beta_term = (self.props['beta_m'] * (delta_t) +
                     self.props['beta*_m'] * (delta_m))

        self.params['Ra'] = const.ACC_GRAV * beta_term * \
            pow(self.settings['L_t'], 3) /\
            (self.props['alpha_m'] * self.props['nu_m'])

    def iter_solve(self):
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
        return count

    def eval_model(self, vec_in):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass

    def set_solution(self):
        """Docstring."""
        # These are overridden by the sub-classes that extend this class
        pass


class OneDimIsoLiqNoRad(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """The f_matrix and j_matrix are constant, can be set in __init__()."""
        super(OneDimIsoLiqNoRad, self).__init__(settings, ref=ref, rule=rule)

        self.solution = dict(mddp=None, q_cm=None, T_s=None)

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_cm, T_s = vec_in
        res = [0 for _ in range(len(self.solution))]
        res[0] = q_cm + \
            (self.props['k_m'] / self.settings['L_t']) * \
            (self.settings['T_e'] - T_s)
        res[1] = mddp + \
            (self.props['rho_m'] * self.props['D_12'] /
             self.settings['L_t']) * \
            (self.props['m_1e'] - self.props['m_1s'])
        res[2] = mddp * self.props['h_fg'] + q_cm
        return res

    def set_solution(self, solution):
        """Docstring."""
        self.solution['mddp'] = solution[0]
        self.solution['q_cm'] = solution[1]
        self.solution['T_s'] = solution[2]


class OneDimIsoLiqBlackRad(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Docstring."""
        super(OneDimIsoLiqBlackRad, self).__init__(
            settings, ref=ref, rule=rule)

        self.unknowns = ['mddp', 'q_m', 'q_r', 'temp_s']
        self.temp_s_loc = 3

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_m, q_r, temp_s = vec_in
        res = [0 for _ in range(4)]
        res[0] = q_m + (self.k_m / self.length) * (self.temp_e - temp_s)
        res[1] = mddp + \
            (self.rho_m * self.d_12 / self.length) * (self.m_1e - self.m_1s)
        res[2] = mddp * self.h_fg + q_m + q_r
        res[3] = q_r - \
            const.SIGMA * (pow(temp_s, 4) - pow(self.temp_e, 4))
        return res

    def set_solution(self, solution):
        """Docstring."""
        self.solution = dict(mddp=solution[0], q_m=solution[1],
                             q_r=solution[2], temp_s=solution[3])

    def rad_props(self):
        """Docstring."""
        return 'eps_1: ' + str(self.eps[0]) + \
               '\neps_2: ' + str(self.eps[1]) + \
               '\neps_3: ' + str(self.eps[2])


# class OneDimIsoLiqBlackGrayRad(OneDimIsoLiqBlackRad):
#     """Docstring."""

#     def __init__(self, settings, ref='Mills', rule='mean'):
#         """Docstring."""
#         super(OneDimIsoLiqBlackGrayRad, self).__init__(settings, ref=ref,
#                                                        rule=rule)

#         self.eps = settings['eps']

#     def eval_model(self, vec_in):
#         """Docstring."""
#         mddp, q_m, q_r, temp_s = vec_in
#         res = [0 for _ in range(4)]
#         res[0] = q_m + (self.k_m / self.length) * (self.temp_e - temp_s)
#         res[1] = mddp + \
#             (self.rho_m * self.d_12 / self.length) * (self.m_1e - self.m_1s)
#         res[2] = mddp * self.h_fg + q_m + q_r

#         eb1 = const.SIGMA * pow(temp_s, 4)
#         eb2 = const.SIGMA * pow(self.temp_e, 4)
#         a1 = const.TUBE_AREA
#         a2t = (self.eps[1] * 2 * a1) / (1 - self.eps[1])

#         res[3] = q_r - eb1 + ((a1 * eb1 + a2t * eb2) / (a1 + a2t))
#         return res

#     def set_solution(self, solution):
#         """Docstring."""
#         self.solution = dict(mddp=solution[0], q_m=solution[1],
#                              q_r=solution[2], temp_s=solution[3])


# class OneDimIsoLiqGrayRad(Model):
#     """Docstring."""

#     def __init__(self, settings, eps, ref='Mills', rule='mean'):
#         """The f_matrix and j_matrix are constant, can be set in __init__()."""
#         super(OneDimIsoLiqGrayRad, self).__init__(settings, ref=ref, rule=rule)

#         self.f_matrix = [[0, 0, 0] for _ in range(3)]
#         self.set_f_matrix()
#         self.j_matrix = [[0, 0, 0] for _ in range(3)]
#         self.eps = eps
#         self.set_j_matrix()

#     def get_f12(self):
#         """Docstring."""
#         r_1 = const.TUBE_RADIUS / self.length
#         r_2 = const.TUBE_RADIUS / self.length
#         x_value = 1 + (1 + pow(r_2, 2)) / pow(r_1, 2)
#         return (x_value -
#                 pow(pow(x_value, 2) - 4 * pow(r_2 / r_1, 2), 0.5)) / 2

#     def get_f31(self):
#         """Docstring."""
#         area_1 = const.TUBE_AREA
#         area_3 = const.TUBE_CIRCUM * self.length
#         return area_1 / area_3 * self.get_f12()

#     def set_f_matrix(self):
#         """Use geometry of the tube to obtain view factor matrix."""
#         # f_matrix = [[0, 0, 0] for _ in range(3)]
#         # We know from symmetry that F_12 = F_21
#         self.f_matrix[0][1] = self.f_matrix[1][0] = self.get_f12()
#         # We also know that F_11 = F_22 = 0, which means that
#         # F_13 = F_23 = 1 - F_12
#         self.f_matrix[0][2] = self.f_matrix[1][2] = 1 - self.f_matrix[0][1]
#         # Use the G_13 = G_31 to calculate F_31
#         self.f_matrix[2][0] = self.f_matrix[2][1] = self.get_f31()
#         # Everything from 3 that doesn't hit 1 or 2 hits 3
#         self.f_matrix[2][2] = 1 - 2 * self.f_matrix[2][0]

#     def set_j_matrix(self):
#         """"Set the radiosoty matrix using view factors and emissivities."""
#         for row in range(3):
#             for col in range(3):
#                 if row == col:
#                     self.j_matrix[row][col] = 1 - \
#                         (1 - self.eps[row]) * self.f_matrix[row][col]
#                 else:
#                     self.j_matrix[row][col] = -(1 - self.eps[row]) * \
#                         self.f_matrix[row][col]

#     def solve_j_system(self):
#         """Docstring."""
#         temp = [self.temp_s, self.temp_e, (self.temp_s + self.temp_e) / 2]
#         emiss_vec = [self.eps[i] * const.SIGMA * pow(temp[i], 4)
#                      for i in range(3)]
#         return np.linalg.solve(self.j_matrix, emiss_vec)

#     def eval_model(self, vec_in):
#         """Docstring."""
#         mddp, q_m, temp_s = vec_in
#         res = [0 for _ in range(3)]
#         # First we need to solve the linear system of radiosity equations
#         j_vec = self.solve_j_system()

#         print(j_vec, res)
