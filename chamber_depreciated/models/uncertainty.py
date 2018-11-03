"""Module for error propagation."""
import itertools
import math
import operator

import numpy as np

from chamber.models import film
from chamber.models import props


def prop_uncertainty(func, param_1, param_2=None, param_3=None,
                     param_4=None, param_5=None, param_6=None):
    """
    Calculate the uncertainty associated with a function from `props` module.

    Leverage itertools and operators to call all possible uncertainty addition
    and subtraction combinations to determine the greatest uncertainty.

    Parameters
    ----------
    func: function
        Function from `props` module.
    param_1: tuple
        A `tuple` of `floats` or `ints` representing a measurement and its
        uncertainty, eg. (290.00, 0.02).
    param_2: tuple
        A `tuple` of `floats` or `ints` representing a measurement and its
        uncertainty, eg. (290.00, 0.02). Defaults to `None`
    param_3: tuple
        A `tuple` of `floats` or `ints` representing a measurement and its
        uncertainty, eg. (290.00, 0.02). Defaults to `None`
    param_4: tuple or str
        A `tuple` of `floats` or `ints` representing a measurement and its
        uncertainty, eg. (290.00, 0.02). Or a string reference eg. 'Mills'.
        Defaults to `None`
    param_5: str
        The rule used to calculate `film` properties.
    param_6: str
        The ref used to calculate `film` properties.

    Returns
    -------
    tuple
        The desired function's output and associated error.

    Examples
    --------
    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> ref = 'Mills'
    >>> prop_uncertainty(get_d_12, p, t, t_dp, ref)
    (2.4306504684558495e-05, 1.4163719437180477e-07)

    >>> p = (101325, 1)
    >>> t_s = (285, 1)
    >>> prop_uncertainty(get_k_m_sat, p, t_s)
    (0.025260388108991345, 7.454320267070297e-05)

    """
    prop = 0
    val = []
    # Creates all possible lists of length 'repeat' made of combinations
    # of the two operators
    op_list = list(itertools.product(
            [operator.add, operator.sub],
            repeat=4 if type(param_4) is tuple
            else 3 if param_3
            else 2 if param_2
            else 1
        )
    )
    # Loop through list of operator combinations
    for op in op_list:
        if param_6:
            # Populate the value of prop on first iteration
            if not val:
                prop = func(
                    param_1[0], param_2[0], param_3[0],
                    param_4[0], param_5, param_6
                )
            val.append(
                func(
                    op[0](param_1[0], param_1[1]),
                    op[1](param_2[0], param_2[1]),
                    op[2](param_3[0], param_3[1]),
                    op[3](param_4[0], param_4[1]),
                    param_5,
                    param_6
                )
            )
        elif param_5:
            # Populate the value of prop on first iteration
            if not val:
                prop = func(
                    param_1[0], param_2[0], param_3[0], param_4[0], param_5
                )
            val.append(
                func(
                    op[0](param_1[0], param_1[1]),
                    op[1](param_2[0], param_2[1]),
                    op[2](param_3[0], param_3[1]),
                    op[3](param_4[0], param_4[1]),
                    param_5
                )
            )
        elif type(param_4) is tuple:
            if not val:
                prop = func(
                    param_1[0], param_2[0], param_3[0], param_4[0]
                )
            val.append(
                func(
                    op[0](param_1[0], param_1[1]),
                    op[1](param_2[0], param_2[1]),
                    op[2](param_3[0], param_3[1]),
                    op[3](param_4[0], param_4[1])
                )
            )
        elif param_4:
            if not val:
                prop = func(param_1[0], param_2[0], param_3[0], param_4)
            val.append(
                func(
                    op[0](param_1[0], param_1[1]),
                    op[1](param_2[0], param_2[1]),
                    op[2](param_3[0], param_3[1]),
                    param_4
                )
            )
        elif param_3:
            if not val:
                prop = func(param_1[0], param_2[0], param_3[0])
            val.append(
                func(
                    op[0](param_1[0], param_1[1]),
                    op[1](param_2[0], param_2[1]),
                    op[2](param_3[0], param_3[1])
                )
            )
        elif param_2:
            if not val:
                prop = func(param_1[0], param_2[0])
            val.append(
                func(
                    op[0](param_1[0], param_1[1]),
                    op[1](param_2[0], param_2[1])
                )
            )
        else:
            if not val:
                prop = func(param_1[0])
            val.append(
                func(
                    op[0](param_1[0], param_1[1]),
                )
            )
    # Get the largest in magnitude difference in function results
    prop_err = abs(np.array(val) - prop).max()
    return (prop, prop_err)


def liq_length(m_tl):
    """
    Calculate the height [m] with uncertainty of the liquid in the tube.

    Calucalte the height of the liquid in the tube in meters. Uncertainty
    is reported as the second argument of the returned tuple.

    Parameters
    ----------
    m_tl : (float, float)
        The mass of the tube with liquid in it and error in the measurement.

    Returns
    -------
    (float, float)
        The liquid height and associated uncertainty as (height, uncertainty).

    """
    r_t = (0.015, 1e-4)  # m
    rho_w = 997  # kg / m^3
    m_t = (0.0873832, 1e-6)  # kg
    l_t = (0.06, 1e-4)
    # Calculate the mass of the liquid
    m_l = (
        m_tl[0] - m_t[0], math.sqrt(math.pow(m_tl[1], 2) + math.pow(m_t[1], 2))
    )
    # Calculate uncertainty of water level
    l_unc = math.sqrt(
        math.pow(m_l[1] / (rho_w * np.pi * math.pow(r_t[0], 2)), 2) +
        math.pow(
            2 * m_l[0] * r_t[1] / (rho_w * np.pi * math.pow(r_t[0], 3)), 2
        )
    )
    # Calculate water level
    l_s = m_l[0] / (rho_w * np.pi * math.pow(r_t[0], 2))

    l_e = (l_t[0] - l_s,
           math.sqrt(math.pow(l_t[1], 2) + math.pow(l_unc, 2)))

    return l_e


def mdpp_unc(mdpp, spald):
    """Docstring."""
    p = (spald.exp_state['p'], 0.0015 * spald.exp_state['p'])
    t_e = (spald.exp_state['t_e'], 0.2)
    t_dp = (spald.exp_state['t_dp'], 0.2)
    t_s = (spald.t_s_guess, 0)
    m_l = (spald.exp_state['m_l'], 4e-8)
    rule = spald.film_guide['rule']
    ref = spald.film_guide['ref']

    rho_m = prop_uncertainty(film.est_rho_m, p, t_e, t_dp, t_s, rule)
    d_12 = prop_uncertainty(film.est_d_12, p, t_e, t_dp, t_s, rule, ref)
    l_s = liq_length(m_l)
    m_1s = prop_uncertainty(props.get_m_1_sat, p, t_s)
    m_1e = prop_uncertainty(props.get_m_1, p, t_e, t_dp)

    mdpp_unc = (
        mdpp * math.sqrt(
            math.pow(rho_m[1] / rho_m[0], 2) +
            math.pow(d_12[1] / d_12[0], 2) +
            math.pow(l_s[1] / l_s[0], 2) +
            math.pow(math.sqrt(math.pow(m_1s[1], 2) + math.pow(m_1e[1], 2)) /
                     (m_1s[0] - m_1e[0]), 2) +
            math.pow(m_1s[1] / m_1s[0], 2)
        )
    )
    return (mdpp, mdpp_unc)
