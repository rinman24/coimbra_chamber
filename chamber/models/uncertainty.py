"""Module for error propagation."""
import itertools
import operator

import numpy as np

from chamber.models.props import *


def prop_uncertainty(func, param_1, param_2=None, param_3=None, param_4=None):
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
    param_2: tuple
        A `tuple` of `floats` or `ints` representing a measurement and its
        uncertainty, eg. (290.00, 0.02). Defaults to `None`
    param_2: tuple or str
        A `tuple` of `floats` or `ints` representing a measurement and its
        uncertainty, eg. (290.00, 0.02). Or a string reference eg. 'Mills'.
        Defaults to `None`

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
        if type(param_4) is tuple:
            # Populate the value of prop on first iteration
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
