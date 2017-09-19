"""Docstring."""
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI

import chamber.const as const

class Model(object):
    """Object to hold the state of a heat and mass transfer model."""

    # pylint: disable=too-many-instance-attributes
    # Thirteen is reasonable in this case.

    def __init__(self, settings, ref='Mills', rule='mean'):
        """Constructor."""
        self.length = settings['length']
        self.pressure = settings['pressure']
        self.temp_dp = settings['temp_dp']
        self.temp_e = settings['temp_e']
        self.ref = ref
        self.rule = rule
        self.temp_s = 300
        self.d_12 = None
        self.h_fg = None
        self.k_m = None
        self.m_1e = None
        self.m_1s = None
        self.rho_m = None

        self.eval_props()

    def __repr__(self):
        """print(repr(<MODEL>))"""
        repr_1 = "settings = dict(length={}, pressure={}, temp_dp={}, temp_e={})"\
                 .format(self.length, self.pressure, self.temp_dp, self.temp_e)

        repr_2 = "\nModel(settings, ref='{}', rule='{}')"\
                 .format(self.ref, self.rule)

        return repr_1 + repr_2

    def __str__(self):
        """print(str(<MODEL>))"""
        return ('--------- Settings ---------\n'
                'Length:\t\t{:.6g}\n' +
                'Pressure:\t{:.6g}\n' +
                'Reference:\t{}\n' +
                'Rule:\t\t{}\n' +
                'Temp_DP:\t{:.6g}\n' +
                'Temp_e:\t\t{:.6g}\n' +
                '-------- Properties --------\n' +
                'D_12:\t\t{:.6g}\n' +
                'h_fg:\t\t{:.6g}\n' +
                'm_1e:\t\t{:.6g}\n' +
                'm_1s:\t\t{:.6g}\n' +
                'rho_m:\t\t{:.6g}')\
                .format(self.length, self.pressure, self.ref, self.rule, self.temp_dp,\
                        self.temp_e, self.d_12, self.h_fg, self.m_1e, self.m_1s, self.rho_m)

    @staticmethod
    def get_ref_state(e_state, s_state, rule):
        """Calculate ref state based on rule."""
        return {'mean': lambda e, s: (e + s)/2,
                'one-third': lambda e, s: s + (e - s)/3
               }[rule](e_state, s_state)

    @staticmethod
    def get_bin_diff_coeff(ref_temp, pressure, ref):
        """Get binary diffusion coefficient based on ref."""
        # See Table A.17a in `Mass Transfer` by Mills and Coimbra for details.
        return {'Mills': lambda t, p: 1.97e-5*(1/p)*pow(t/256, 1.685),
                'Marrero': lambda t, p: 1.87e-10*pow(t, 2.072)/p
               }[ref](ref_temp, pressure/101325)

    def eval_props(self):
        """Use CoolProp and attributes to evaluate thermo-physical properties."""
        x_1e = HAPropsSI('Y', 'T', self.temp_e, 'T_dp', self.temp_dp, 'P', self.pressure)
        x_1s = HAPropsSI('Y', 'T', self.temp_s, 'RH', 1, 'P', self.pressure)

        ref_x = self.get_ref_state(x_1e, x_1s, self.rule)
        ref_temp = self.get_ref_state(self.temp_e, self.temp_s, self.rule)

        self.d_12 = self.get_bin_diff_coeff(ref_temp, self.pressure, self.ref)
        self.h_fg = PropsSI('H', 'T', self.temp_s, 'Q', 1, 'water') - \
                    PropsSI('H', 'T', self.temp_s, 'Q', 0, 'water')
        self.k_m = HAPropsSI('k', 'T', ref_temp, 'Y', ref_x, 'P', self.pressure)
        self.m_1e = (x_1e*const.M1)/(x_1e*const.M1 + (1-x_1e)*const.M2)
        self.m_1s = (x_1s*const.M1)/(x_1s*const.M1 + (1-x_1s)*const.M2)
        self.rho_m = 1/HAPropsSI('Vha', 'T', ref_temp, 'Y', ref_x, 'P', self.pressure)
