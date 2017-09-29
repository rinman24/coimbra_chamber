"""Docstring."""
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI

import chamber.const as const

import numpy as np

import scipy.optimize as opt


class Model(object):
    """Object to hold the state of a heat and mass transfer model."""

    learning_rate = 0.05

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Constructor."""
        self.length = settings['length']
        self.pressure = settings['pressure']
        self.temp_dp = settings['temp_dp']
        self.temp_e = settings['temp_e']
        self.temp_s = (self.temp_e + self.temp_dp) / 2
        self.ref = ref
        self.rule = rule

        # Properties
        self.alpha_m = None
        self.beta_m = None
        self.beta_star_m = None
        self.cp_m = None
        self.d_12 = None
        self.h_fg = None
        self.k_m = None
        self.m_1e = None
        self.m_1s = None
        self.mu_m = None
        self.nu_m = None
        self.rho_m = None
        self.solution = None

        # Dimensionless Groups
        self.Ra_number = None

        self.eval_props()

    def __repr__(self):
        """print(repr(<MODEL>))"""
        pt1 = "settings = dict(length={}, pressure={}, temp_dp={}, temp_e={})"\
            .format(self.length, self.pressure, self.temp_dp, self.temp_e)

        pt2 = "\nModel(settings, ref='{}', rule='{}')"\
            .format(self.ref, self.rule)

        return pt1 + pt2

    def __str__(self):
        """print(str(<MODEL>))"""
        return ('--------- Settings ---------\n'
                'Length:\t\t{:.6g}\n' +
                'Pressure:\t{:.6g}\n' +
                'Reference:\t{}\n' +
                'Rule:\t\t{}\n' +
                'Temp_DP:\t{:.6g}\n' +
                'Temp_e:\t\t{:.6g}\n' +
                'Temp_s:\t\t{:.6g}\n' +
                '-------- Properties --------\n' +
                'D_12:\t\t{:.6g}\n' +
                'h_fg:\t\t{:.6g}\n' +
                'm_1e:\t\t{:.6g}\n' +
                'm_1s:\t\t{:.6g}\n' +
                'rho_m:\t\t{:.6g}'
                ).format(self.length, self.pressure, self.ref, self.rule,
                         self.temp_dp, self.temp_e, self.temp_s, self.d_12,
                         self.h_fg, self.m_1e, self.m_1s, self.rho_m)

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
        """Use CoolProp and attributes to evaluate thermo-physical properties.
        """
        x_1e = HAPropsSI('Y', 'T', self.temp_e, 'T_dp', self.temp_dp,
                         'P', self.pressure)

        x_1s = HAPropsSI('Y', 'T', self.temp_s, 'RH', 1, 'P', self.pressure)

        ref_x = self.get_ref_state(x_1e, x_1s, self.rule)

        ref_m = (ref_x * const.M1) /\
            (ref_x * const.M1 + (1 - ref_x) * const.M2)

        ref_temp = self.get_ref_state(self.temp_e, self.temp_s, self.rule)

        self.mu_m = HAPropsSI('mu', 'T', ref_temp, 'Y', ref_x,
                              'P', self.pressure)

        self.cp_m = HAPropsSI('cp', 'T', ref_temp, 'Y', ref_x,
                              'P', self.pressure)

        self.d_12 = self.get_bin_diff_coeff(ref_temp, self.pressure, self.ref)

        self.h_fg = PropsSI('H', 'T', self.temp_s, 'Q', 1, 'water') - \
            PropsSI('H', 'T', self.temp_s, 'Q', 0, 'water')

        self.k_m = HAPropsSI('k', 'T', ref_temp, 'Y', ref_x,
                             'P', self.pressure)

        self.m_1e = (x_1e * const.M1) /\
            (x_1e * const.M1 + (1 - x_1e) * const.M2)

        self.m_1s = (x_1s * const.M1) /\
            (x_1s * const.M1 + (1 - x_1s) * const.M2)

        self.rho_m = 1 / HAPropsSI('Vha', 'T', ref_temp, 'Y', ref_x,
                                   'P', self.pressure)

        self.nu_m = self.mu_m / self.rho_m

        self.alpha_m = self.k_m / (self.cp_m * self.rho_m)

        self.beta_m = 1 / ref_temp

        self.beta_star_m = (const.M2 - const.M1) /\
            (ref_m * (const.M2 - const.M1) + const.M1)

        delta_t = self.temp_s - self.temp_e

        delta_m = self.m_1s - self.m_1e

        beta_term = (self.beta_m * (delta_t) + self.beta_star_m * (delta_m))

        self.Ra_number = const.ACC_GRAV * beta_term * pow(self.length, 3) /\
            (self.alpha_m * self.nu_m)

    def solve_iteratively(self):
        """Docstring."""
        delta, count = 1, 0
        guess = [1 for _ in range(len(self.unknowns))]
        while abs(delta) > 1e-9:
            sol = opt.fsolve(self.eval_model, guess)
            delta = sol[self.temp_s_loc] - self.temp_s
            self.temp_s += self.learning_rate * delta
            self.eval_props()
            count += 1
        self.set_solution(sol)
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

        self.unknowns = ['mddp', 'q_m', 'temp_s']
        self.temp_s_loc = 2

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_m, temp_s = vec_in
        res = [0 for _ in range(3)]
        res[0] = q_m + (self.k_m / self.length) * (self.temp_e - temp_s)
        res[1] = mddp + \
            (self.rho_m * self.d_12 / self.length) * (self.m_1e - self.m_1s)
        res[2] = mddp * self.h_fg + q_m
        return res

    def set_solution(self, solution):
        """Docstring."""
        self.solution = dict(mddp=solution[0], q_m=solution[1], temp_s=solution[2])


class OneDimIsoLiqBlackRad(Model):
    """Docstring."""

    def __init__(self, settings, ref='Mills', rule='mean'):
        """The f_matrix and j_matrix are constant, can be set in __init__()."""
        super(OneDimIsoLiqBlackRad, self).__init__(settings, ref=ref, rule=rule)

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
        res[3] = q_r - 5.67e-8 * (pow(self.temp_s, 4) - pow(self.temp_e, 4))
        return res

    def set_solution(self, solution):
        """Docstring."""
        self.solution = dict(mddp=solution[0], q_m=solution[1], q_r=solution[2], temp_s=solution[3])


class OneDimIsoLiqGrayRad(Model):
    """Docstring."""

    def __init__(self, settings, eps, ref='Mills', rule='mean'):
        """The f_matrix and j_matrix are constant, can be set in __init__()."""
        super(OneDimIsoLiqGrayRad, self).__init__(settings, ref=ref, rule=rule)

        self.f_matrix = [[0, 0, 0] for _ in range(3)]
        self.set_f_matrix()
        self.j_matrix = [[0, 0, 0] for _ in range(3)]
        self.eps = eps
        self.set_j_matrix()

    def get_f12(self):
        """Docstring."""
        r_1 = const.TUBE_RADIUS / self.length
        r_2 = const.TUBE_RADIUS / self.length
        x_value = 1 + (1 + pow(r_2, 2)) / pow(r_1, 2)
        return (x_value -
                pow(pow(x_value, 2) - 4 * pow(r_2 / r_1, 2), 0.5)) / 2

    def get_f31(self):
        """Docstring."""
        area_1 = const.TUBE_AREA
        area_3 = const.TUBE_CIRCUM * self.length
        return area_1 / area_3 * self.get_f12()

    def set_f_matrix(self):
        """Use geometry of the tube to obtain view factor matrix."""
        # f_matrix = [[0, 0, 0] for _ in range(3)]
        # We know from symmetry that F_12 = F_21
        self.f_matrix[0][1] = self.f_matrix[1][0] = self.get_f12()
        # We also know that F_11 = F_22 = 0, which means that
        # F_13 = F_23 = 1 - F_12
        self.f_matrix[0][2] = self.f_matrix[1][2] = 1 - self.f_matrix[0][1]
        # Use the G_13 = G_31 to calculate F_31
        self.f_matrix[2][0] = self.f_matrix[2][1] = self.get_f31()
        # Everything from 3 that doesn't hit 1 or 2 hits 3
        self.f_matrix[2][2] = 1 - 2 * self.f_matrix[2][0]

    def set_j_matrix(self):
        """"Set the radiosoty matrix using view factors and emissivities."""
        for row in range(3):
            for col in range(3):
                if row == col:
                    self.j_matrix[row][col] = 1 - \
                        (1 - self.eps[row]) * self.f_matrix[row][col]
                else:
                    self.j_matrix[row][col] = -(1 - self.eps[row]) * \
                        self.f_matrix[row][col]

    def solve_j_system(self):
        """Docstring."""
        temp = [self.temp_s, self.temp_e, (self.temp_s + self.temp_e) / 2]
        emiss_vec = [self.eps[i] * const.SIGMA * pow(temp[i], 4)
                     for i in range(3)]
        return np.linalg.solve(self.j_matrix, emiss_vec)

    def eval_model(self, vec_in):
        """Docstring."""
        mddp, q_m, temp_s = vec_in
        res = [0 for _ in range(3)]
        # First we need to solve the linear system of radiosity equations
        j_vec = self.solve_j_system()

        print(j_vec, res)
