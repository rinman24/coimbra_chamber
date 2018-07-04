"""
Thermophysical film properties of humid air.

This module provides a convenient wrapper around specific funtionality of the
`CoolProp package`_. Specifically, the ability to calulate approximate constant
film properties based on an e-state, s-state, and averaging rule.

Functions
---------
    use_rule
    est_mix_props
    est_liq_props

.. _CoolProp package:
   http://www.coolprop.org/

"""

from chamber.models import props


def use_rule(e_value, s_value, rule):
    """
    Calculate film state by applying the given rule.

    This function returns the value of a film property given the `e_value`,
    `s_value`, and a `rule`.

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
    float
        The film property in the same units as `e_value` and `s_value`.

    Examples
    --------
    >>> e_temp = 300
    >>> s_temp = 290
    >>> rule = '1/2'
    >>> use_rule(e_temp, s_temp, rule)
    295.0

    >>> rule = '1/3'
    >>> use_rule(e_temp, s_temp, rule)
    293.3333333333333

    Raises
    ------
    ValueError
        If `rule` is not in `{'1/2', '1/3'}`.

    Notes
    -----
    For more information regarding the choices for `rule` see [5]_.

    References
    ----------
    .. [5] Mills, A. F. and Coimbra, C. F. M., 2016
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


def est_mix_props(p, t_e, t_dp, t_s, ref, rule):
    """
    Estimates of film properties.

    This function calculates estimations of constant film properties based on
    input parameters. Properties are returned in a `dict` with the follwoing
    keys:
    * 'c_pm': Specific heat of vapor mixture film in J/kg K
    * 'rho_m': Specific mass of vapor mixture film in kg/m:math:`^3`
    * 'k_m': Thermal conductivity of the vapor mixture film in W/m K.
    * 'alpha_m': Thermal diffusivity of the vapor mixture film in
    m:math:`^2`/s.
    * 'd_12': Binary species diffusivity of the vapor mixture film in
    m:math:`^2`/s

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_e : int or float
        Dry bulb temperature of the environment in K.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.
    t_dp : int or float
        Dew point temperature in K.
    ref : {'Mills', 'Marrero', 'constant'}
        Reference for binary species diffusiity, see ``Notes``.
    rule : {'1/2', '1/3'}
        Rule for calculating the `film_prop`, see ``Notes``.

    Returns
    -------
    dict(float)
        The film properties in the same units as inputs.

    Examples
    --------
    Let's get the film props as `p` = 101325, `t` = 290, `t_dp` = 280,
    `t_s` = 285, `ref` = 'Mills' and `rule` = '1/2'

    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> t_s = 285
    >>> ref = 'Mills'
    >>> rule = '1/2'
    >>> film_props = est_mix_props(p, t, t_dp, t_s, ref, rule)
    >>> film_props['c_pm']
    1019.9627505486458
    >>> film_props['rho_m']
    1.2229936606324967
    >>> film_props['k_m']
    0.025446947707731902
    >>> film_props['alpha_m']
    2.040317009201964e-05
    >>> film_props['d_12']
    2.3955520502741308e-05

    Change `rule` to '1/3'

    >>> rule = '1/3'
    >>> film_props = est_mix_props(p, t, t_dp, t_s, ref, rule)
    >>> film_props['c_pm']
    1020.7363637843752
    >>> film_props['rho_m']
    1.2262478476537964
    >>> film_props['k_m']
    0.025384761174818384
    >>> film_props['alpha_m']
    2.028355491502325e-05
    >>> film_props['d_12']
    2.3838525775468913e-05

    Change `ref` to 'Marrero'. Only `film_props['d_12']` will update

    >>> ref = 'Marrero'
    >>> film_props = est_mix_props(p, t, t_dp, t_s, ref, rule)
    >>> film_props['d_12']
    2.3097223037856368e-05

    Raises
    ------
    ValueError
        If `rule` is not in `{'1/2', '1/3'}`.
    ValueError
        If `ref` is not in `{'Mills', 'Marrero'}`

    Notes
    -----
    For more information regarding the choices for `ref` and `rule` see [1]_.

    References
    ----------
    .. [1] Mills, A. F. and Coimbra, C. F. M., 2016
       *Mass Transfer: Third Edition*, Temporal Publishing, LLC.

    """
    c_pm = _est_c_pm(p, t_e, t_dp, t_s, rule)
    rho_m = _est_rho_m(p, t_e, t_dp, t_s, rule)
    k_m = _est_k_m(p, t_e, t_dp, t_s, rule)
    alpha_m = _est_alpha_m(p, t_e, t_dp, t_s, rule)
    d_12 = _est_d_12(p, t_e, t_dp, t_s, ref, rule)
    film_props = dict(
        c_pm=c_pm, rho_m=rho_m, k_m=k_m, alpha_m=alpha_m, d_12=d_12
    )
    return film_props


def est_liq_props(t_s, t_t, rule):
    """
    Estimates of liquid properties.

    This function calculates estimations of constant liquid properties.
    Properties are returned in a `dict` with the follwoing
    keys:
    * 'c_pl': Specific heat of vapor mixture film in J/kg K

    Parameters
    ----------
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.
    t_t : int or float
        Temperature of the liquid water (condensed phase) in K.
    rule : {'1/2', '1/3'}
        Rule for calculating the `film_prop`, see ``Notes``.

    Returns
    -------
    dict(float)
        The film properties in the same units as inputs.

    Examples
    --------
    Let's get the liquid props for `t_s` = 285, `t_t` = 290, `rule` = '1/2'

    >>> t_s = 285
    >>> t_t = 290
    >>> rule = '1/2'
    >>> liq_props = est_liq_props(t_s, t_t, rule)
    >>> liq_props['c_pl']
    4189.82872258844

    Change `rule` to '1/3'

    >>> rule = '1/3'
    >>> liq_props = est_liq_props(t_s, t_t, rule)
    >>> liq_props['c_pl']
    4190.7955800723075

    Raises
    ------
    ValueError
        If `rule` is not in `{'1/2', '1/3'}`.

    """
    c_pl = _est_c_pl(t_s, t_t, rule)
    liq_props = dict(c_pl=c_pl)
    return liq_props


def _est_c_pm(p, t_e, t_dp, t_s, rule):
    """Estimate specific heat of the vapor mixture film."""
    c_pme = props.get_c_pm(p, t_e, t_dp)
    c_pms = props.get_c_pm_sat(p, t_s)

    c_pm_film = use_rule(c_pme, c_pms, rule)
    return c_pm_film


def _est_rho_m(p, t_e, t_dp, t_s, rule):
    """Estimate specific mass of the vapor mixture film."""
    rho_me = props.get_rho_m(p, t_e, t_dp)
    rho_ms = props.get_rho_m_sat(p, t_s)

    rho_m_film = use_rule(rho_me, rho_ms, rule)
    return rho_m_film


def _est_k_m(p, t_e, t_dp, t_s, rule):
    """Estimate thermal conductivity of the vapor mixture film."""
    k_me = props.get_k_m(p, t_e, t_dp)
    k_ms = props.get_k_m_sat(p, t_s)

    k_m_film = use_rule(k_me, k_ms, rule)
    return k_m_film


def _est_alpha_m(p, t_e, t_dp, t_s, rule):
    """Estimate thermal diffusivity of the vapor mixture film."""
    alpha_me = props.get_alpha_m(p, t_e, t_dp)
    alpha_ms = props.get_alpha_m_sat(p, t_s)

    alpha_m_film = use_rule(alpha_me, alpha_ms, rule)
    return alpha_m_film


def _est_d_12(p, t_e, t_dp, t_s, ref, rule):
    """Estimate binary species diffusivity of the vapor mixture film."""
    d_12e = props.get_d_12(p, t_e, t_dp, ref)
    d_12s = props.get_d_12(p, t_s, t_s, ref)

    d_12_film = use_rule(d_12e, d_12s, rule)
    return d_12_film


def _est_c_pl(t_s, t_t, rule):
    """Estimate specific heat of pure liquid water at the film temperature."""
    c_pls = props.get_c_pl(t_s)
    c_plt = props.get_c_pl(t_t)

    c_pl_film = use_rule(c_plt, c_pls, rule)
    return c_pl_film
