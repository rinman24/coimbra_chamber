"""Docstring."""

from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI

import scipy.optimize as opt

import chamber.const as const

def get_ref_state(e_state, s_state, rule):
    """Use e_state, s_state, and a rule to calculate the reference state.

    Parameters
    ----------
    e_state : float
        Temperature or mole fraction at the e-state
    s_state : float
        Temperature or mole fraction at the s-state
    rule : string
        A string used to select the rule to use. It can be either 'mean' or 'one-third'

    Returns
    -------
    ref_state : float
        Referance temperature or mole fraction at the reference state according to the rule
    """
    return {'mean': lambda e, s: (e + s)/2,
            'one-third': lambda e, s: s + (e - s)/3
           }[rule](e_state, s_state)

def get_bin_diff_coeff(ref_temp, pressure, ref):
    """Use the ref_temp and pressure to return the binary diffusion coefficient of water in air.

    Parameters
    ----------
    ref_temp : float
        Referance temperature, [K]
    pressure : int (or float)
        Pressure, [Pa]
    ref : string
        A string used to select the reference to use. It can be either 'Mills' or 'Marrero'
        See Table A.17a in `Mass Transfer` by Mills and Coimbra for details

    Returns
    -------
    bin_diff_coeff : float
        Binary diffusion coefficient of water vapor in air, [m^2/s]
    """
    return {'Mills': lambda t, p: 1.97e-5*(1/p)*pow(t/256, 1.685),
            'Marrero': lambda t, p: 1.87e-10*pow(t, 2.072)/p
           }[ref](ref_temp, pressure/101325)

def get_tp_props(model_vars):
    """Use the model_vars dictionary to calculate therophysical properties.

    Parameters
    ----------
    model_vars : dict
        Dictionary of model variables, see chamber.models for more detail on keys

    Returns
    -------
    model_vars : dict
        Dictionary of model variables with updated thermophysical properties
    """
    x_1e = HAPropsSI('Y',
                     'T', model_vars['temp_e'],
                     'T_dp', model_vars['temp_dp'],
                     'P', model_vars['pressure'])

    x_1s = HAPropsSI('Y',
                     'T', model_vars['temp_s'],
                     'RH', 1,
                     'P', model_vars['pressure'])

    ref_x = get_ref_state(x_1e, x_1s, model_vars['rule'])
    ref_temp = get_ref_state(model_vars['temp_e'], model_vars['temp_s'], model_vars['rule'])

    model_vars['d_12'] = get_bin_diff_coeff(ref_temp, model_vars['pressure'], model_vars['ref'])
    model_vars['h_fg'] = PropsSI('H', 'T', model_vars['temp_s'], 'Q', 1, 'water') - \
                         PropsSI('H', 'T', model_vars['temp_s'], 'Q', 0, 'water')
    model_vars['k_m'] = HAPropsSI('k', 'T', ref_temp, 'Y', ref_x, 'P', model_vars['pressure'])
    model_vars['m_1e'] = (x_1e*const.M1)/(x_1e*const.M1 + (1-x_1e)*const.M2)
    model_vars['m_1s'] = (x_1s*const.M1)/(x_1s*const.M1 + (1-x_1s)*const.M2)
    model_vars['rho_m'] = 1/HAPropsSI('Vha', 'T', ref_temp, 'Y', ref_x, 'P', model_vars['pressure'])

    return model_vars
