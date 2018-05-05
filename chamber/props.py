"""
Thermophysical properties of water and humid air.

This module provides a convenient wrapper around specific funtionality of the
`CoolProp package`_. Specifically, the ability to calulate properties at a
given state. A state in this case is defined as the combination of pressure `p`
in Pa, dry bulb temperature `t` in K, and dew point `t_dp` in K.

Attributes
----------
    M1 : float
        Molecular weight of H:math:`_2`O (species-1) in kg/kmol.
    M2 : float
        Molecular weight of dry-air (species-2) in kg/kmol.

Functions
---------
    get_c_pm
    get_c_pm_sat
    get_rho_m
    get_rho_m_sat
    get_k_m
    get_k_m_sat
    get_alpha_m
    get_alpha_m_sat
    get_d_12
    get_x_1
    get_x_1_sat
    get_m_1
    get_m_1_sat
    get_h_fg
    get_rh
    x1_2_m1

.. _CoolProp package:
   http://www.coolprop.org/
"""

from CoolProp import HumidAirProp as hap
from CoolProp import CoolProp as cp

M1 = 18.015
M2 = 28.964


def get_c_pm(p, t, t_dp):
    """The specific heat of the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.

    Returns
    -------
    c_pm : float
        The specific heat of the vapor mixture in J/kg K.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.get_c_pm(p, t, t_dp)
    1017.641910841458
    """
    c_pm = hap.HAPropsSI('cp_ha', 'P', p, 'T', t, 'Tdp', t_dp)
    return c_pm


def get_c_pm_sat(p, t_s):
    """The specific heat of the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    c_pm_sat : float
        The specific heat of the saturated vapor mixture in J/kg K.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> props.get_c_pm_sat(p, t_s)
    1022.2835902558337
    """
    c_pm_sat = hap.HAPropsSI('cp_ha', 'P', p, 'T', t_s, 'RH', 1.0)
    return c_pm_sat


def get_rho_m(p, t, t_dp):
    """The specific mass of the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.

    Returns
    -------
    rho_m : float
        The specific mass of the vapor mixture in kg/m:math:`^3`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.get_rho_m(p, t, t_dp)
    1.213231099568598
    """
    v_ha = hap.HAPropsSI('Vha', 'P', p, 'T', t, 'Tdp', t_dp)
    rho_m = 1/v_ha
    return rho_m


def get_rho_m_sat(p, t_s):
    """The specific mass of the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    rho_m_sat : float
        The specific mass of the saturated vapor mixture in kg/m:math:`^3`.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> props.get_rho_m_sat(p, t_s)
    1.2327562216963954
    """
    v_ha_sat = hap.HAPropsSI('Vha', 'P', p, 'T', t_s, 'RH', 1.0)
    rho_m_sat = 1/v_ha_sat
    return rho_m_sat


def get_k_m(p, t, t_dp):
    """The thermal conductivity of the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.

    Returns
    -------
    k_m : float
        The thermal conductivity of the vapor mixture in W/m K.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.get_k_m(p, t, t_dp)
    0.02563350730647246
    """
    k_m = hap.HAPropsSI('k', 'P', p, 'T', t, 'Tdp', t_dp)
    return k_m


def get_k_m_sat(p, t_s):
    """The thermal conductivity of the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    k_m_sat : float
        The thermal conductivity of the saturated vapor mixture in W/m K.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> props.get_k_m_sat(p, t_s)
    0.025260388108991345
    """
    k_m_sat = hap.HAPropsSI('k', 'P', p, 'T', t_s, 'RH', 1.0)
    return k_m_sat


def get_alpha_m(p, t, t_dp):
    """The thermal diffusivity of the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.

    Returns
    -------
    alpha_m : float
        The thermal diffusivity of the vapor mixture in m:math:`^2`/s.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.get_alpha_m(p, t, t_dp)
    2.076201562300882e-05
    """
    # Get properties needed to calculate alpha_m
    c_pm = get_c_pm(p, t, t_dp)
    k_m = get_k_m(p, t, t_dp)
    rho_m = get_rho_m(p, t, t_dp)

    # Calculate alpha_m
    alpha_m = k_m/(c_pm*rho_m)
    return alpha_m


def get_alpha_m_sat(p, t_s):
    """The thermal diffusivity of the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    alpha_m_sat : float
        The thermal diffusivity of the saturated vapor mixture in
        m:math:`^2`/s.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> props.get_alpha_m_sat(p, t_s)
    2.0044324561030463e-05
    """
    # Get properties needed to calculate alpha_m
    c_pm_sat = get_c_pm_sat(p, t_s)
    k_m_sat = get_k_m_sat(p, t_s)
    rho_m_sat = get_rho_m_sat(p, t_s)

    # Calculate alpha_m
    alpha_m_sat = k_m_sat/(c_pm_sat*rho_m_sat)
    return alpha_m_sat


def get_d_12(p, t, ref):
    """The binary species diffusivity of the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    ref : {'Mills', 'Marrero'}
        Reference for binary species diffusiity, see ``Notes``.

    Returns
    -------
    alpha_m : float
        The thermal diffusivity of the vapor mixture in m:math:`^2`/s.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> ref = 'Mills'
    >>> props.get_d_12(p, t, ref)
    2.4306504684558495e-05

    >>> ref = 'Marrero'
    >>> props.get_d_12(p, t, ref)
    2.365539793302829e-05

    Raises
    ------
    ValueError
        If `ref` is not in `{'Mills', 'Marrero'}`.

    Notes
    -----
    For more information regarding the choices for `ref` see Appendix of [1]_.

    References
    ----------
    .. [1] Mills, A. F. and Coimbra, C. F. M., 2016
       *Mass Transfer: Third Edition*, Temporal Publishing, LLC.
    """
    p_norm = p/101325
    if ref == 'Mills':
        d_12 = 1.97e-5*(1/p_norm)*pow(t/256, 1.685)
        return d_12
    elif ref == 'Marrero':
        d_12 = 1.87e-10*pow(t, 2.072)/p_norm
        return d_12
    else:
        err_msg = (
            "'{0}' is not a valid ref; try 'Mills' or 'Marrero'.".format(ref)
            )
        raise ValueError(err_msg)


def get_x_1(p, t, t_dp):
    """The mole fraction of water vapor in the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.

    Returns
    -------
    x_1 : float
        The mole fraction of water vapor in the vapor mixture in [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.get_x_1(p, t, t_dp)
    0.00982822815586041
    """
    x_1 = hap.HAPropsSI('Y', 'P', p, 'T', t, 'Tdp', t_dp)
    return x_1


def get_x_1_sat(p, t_s):
    """The mole fraction of water vapor in the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    x_1_sat : float
        The mole fraction of water vapor in the saturated vapor mixture in
        [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> props.get_x_1_sat(p, t_s)
    0.01376427605764327
    """
    x_1_sat = hap.HAPropsSI('Y', 'P', p, 'T', t_s, 'RH', 1.0)
    return x_1_sat


def get_m_1(p, t, t_dp):
    """Mass fraction of water vapor in the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.

    Returns
    -------
    m_1 : float
        Mass fraction of water vapor in the vapor mixture in [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.get_m_1(p, t, t_dp)
    0.0061357476021502095
    """
    x_1 = get_x_1(p, t, t_dp)
    m_1 = x1_2_m1(x_1)
    return m_1


def get_m_1_sat(p, t_s):
    """Mass fraction of water vapor in the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    m_1_sat : float
        Mass fraction of water vapor in the saturated vapor mixture in [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> props.get_m_1_sat(p, t_s)
    0.008605868703401028
    """
    x_1_sat = get_x_1_sat(p, t_s)
    m_1_sat = x1_2_m1(x_1_sat)
    return m_1_sat


def get_h_fg_sat(t_s):
    """Specific enthalpy of vaporization for pure water.

    Parameters
    ----------
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    h_fg_sat : float
        Specific enthalpy of vaporization for pure water in J/kg.

    Examples
    --------
    >>> t_s = 285
    >>> props.get_h_fg_sat(t_s)
    2472806.6902607535
    """
    h_g = cp.PropsSI('H', 'T', t_s, 'Q', 1, 'water')
    h_f = cp.PropsSI('H', 'T', t_s, 'Q', 0, 'water')
    h_fg = h_g - h_f
    return h_fg


def get_rh(p, t, t_dp):
    """RH based on p, t and t_dp.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.

    Returns
    -------
    rh : float
        Relative humidity in [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.get_rh(p, t, t_dp)
    0.5165573311068835
    """
    rh = hap.HAPropsSI('RH', 'P', p, 'T', t, 'Tdp', t_dp)
    return rh


def x1_2_m1(x_1):
    """Convert the mole fraction to mass fraction.

    Parameters
    ----------
    x_1 : float
        Mole fraction of water vapor in [0, 1].

    Returns
    -------
    m_1 : float
        Relative humidity in [0, 1].

    Examples
    --------
    >>> x_1 = 0.01
    >>> props.x1_2_m1(x_1)
    0.006243391414375084
    """
    numerator = x_1*M1
    denominator = x_1*M1 + (1-x_1)*M2
    m_1 = numerator/denominator
    return m_1
