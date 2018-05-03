from chamber import props

"""
Thermophysical film properties of water and humid air.

This module provides a convenient wrapper around specific funtionality of the
`CoolProp package`_. Specifically, the ability to calulate approximate constant
film properties based on an e-state, s-state, and averaging rule.

Functions
---------
    use_rule

.. _CoolProp package:
   http://www.coolprop.org/
"""


def use_rule(e_value, s_value, rule):
    """The film property given a rule.

    This function returns the value of a film property given the `e_state`,
    `s_state`, and a `rule`.

    Parameters
    ----------
    e_value : int or float
        Value of the property at the e-state.
    s_value : int or float
        Value of the property at the s-state.
    rule : {'1/2', '1/3'}
        Rule for calculating the `film_prop`, see ``Notes``.

    Returns
    -------
    film_prop : float
        The film property in the same units as `e_value` and `s_value`.

    Examples
    --------
    >>> e_temp = 300
    >>> s_temp = 290
    >>> rule = '1/2'
    >>> film.use_rule(e_temp, s_temp, rule)
    295.0

    >>> rule = '1/3'
    >>> film.use_rule(e_temp, s_temp, rule)
    293.3333333333333

    Raises
    ------
    ValueError
        If `rule` is not in `{'1/2', '1/3'}`.

    Notes
    -----
    For more information regarding the choices for `rule` see [1]_.

    References
    ----------
    .. [1] Mills, A. F. and Coimbra, C. F. M., 2016
       *Mass Transfer: Third Edition*, Temporal Publishing, LLC.
    """
    if rule == '1/2':
        film_prop = (e_value+s_value)/2
        return film_prop
    elif rule == '1/3':
        film_prop = s_value + (e_value-s_value)/3
        return film_prop
    else:
        err_msg = (
            "'{0}' is not a valid rule; try '1/2' or '1/3'.".format(rule)
            )
        raise ValueError(err_msg)


def _est_c_pm(p, t, t_dp, t_s, rule):
    """The specific heat of the vapor film mixture."""
    c_pm_e = props.get_c_pm(p, t, t_dp)
    c_pm_s = props.get_c_pm_sat(p, t_s)

    c_pm_film = use_rule(c_pm_e, c_pm_s, rule)
    return c_pm_film


def _est_rho_m(p, t, t_dp, t_s, rule):
    """The specific mass of the vapor film mixture."""
    rho_m_e = props.get_rho_m(p, t, t_dp)
    rho_m_s = props.get_rho_m_sat(p, t_s)

    rho_m_film = use_rule(rho_m_e, rho_m_s, rule)
    return rho_m_film


def _est_k_m(p, t, t_dp, t_s, rule):
    """The thermal conductivity of the vapor film mixture."""
    k_m_e = props.get_k_m(p, t, t_dp)
    k_m_s = props.get_k_m_sat(p, t_s)

    k_m_film = use_rule(k_m_e, k_m_s, rule)
    return k_m_film


def _est_alpha_m(p, t, t_dp, t_s, rule):
    """The thermal diffusivity of the vapor film mixture."""
    alpha_m_e = props.get_alpha_m(p, t, t_dp)
    alpha_m_s = props.get_alpha_m_sat(p, t_s)

    alpha_m_film = use_rule(alpha_m_e, alpha_m_s, rule)
    return alpha_m_film
