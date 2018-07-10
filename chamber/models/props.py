"""
Thermophysical properties of water and humid air.

This module provides a convenient wrapper around specific funtionality of the
`CoolProp package`_. Specifically, the ability to calulate properties at a
given state. A state in this case is defined as the combination of pressure `p`
in Pa, dry bulb temperature `t` in K, and dew point `t_dp` in K.

Attributes
----------
    M1 : float
        Molecular weight of H\\ :sub:`2`\\ O (species-1) in kg/kmol.
    M2 : float
        Molecular weight of dry-air (species-2) in kg/kmol.

Functions
---------
- `get_alpha_m` -- get the thermal diffusivity of the vapor mixture.
- `get_alpha_m_sat` -- get the thermal diffusivity of the saturated vapor \
    mixture.
- `get_beta_m1` -- get the mass transfer rate coefficient of the stefan tube \
    system.
- `get_c_pl` -- get the specific heat of pure liquid water.
- `get_c_pm` -- get the specific heat of the vapor mixture.
- `get_c_pm_sat` -- get the specific heat of the saturated vapor mixture.
- `get_d_12` -- get the binary species diffusivity of the vapor mixture.
- `get_gamma` -- get the coefficient of volumetric expansion of the vapor \
    mixture.
- `get_h_fg_sat` -- get the specific enthalpy of vaporization for pure water.
- `get_k_m` -- get the thermal conductivity of the vapor mixture.
- `get_k_m_sat` -- get the thermal conductivity of the saturated vapor mixture.
- `get_m_1` -- get the mass fraction of water vapor in the vapor mixture.
- `get_m_1_sat` -- get the mass fraction of water vapor in the saturated \
    vapor mixture.
- `get_mol_wgt` -- get the molar mass of the vapor mixture.
- `get_mu` -- get the dynamic viscocity of the vapor mixture.
- `get_rh` -- get the relative humidity of the vapor liquid mixture.
- `get_rho_m` -- get the specific mass of the vapor mixture.
- `get_rho_m_sat` -- get the specific mass of the saturated vapor mixture.
- `get_tdp` -- get the dew point temperature of the vapor mixture.
- `get_x_1` -- get the mole fraction of water vapor in mixture.
- `get_x_1_sat` -- get the mole fraction of water vapor in the saturated \
    mixture.
- `x1_2_m1` -- convert the mole fraction to mass fraction.

.. _CoolProp package:
   http://www.coolprop.org/

"""

from CoolProp import HumidAirProp as hap
from CoolProp import CoolProp as cp

M1 = 18.015
M2 = 28.964


# --------------------------------------------------------------------------- #
# Vapor Mixture Properties
# --------------------------------------------------------------------------- #

def get_c_pm(p, t, t_dp):
    """
    Get the specific heat of th evapor mixture.

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
    float
        The specific heat of the vapor mixture in J/kg K.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_c_pm(p, t, t_dp)
    1017.641910841458

    """
    c_pm = hap.HAPropsSI('cp_ha', 'P', p, 'T', t, 'Tdp', t_dp)
    return c_pm


def get_c_pm_sat(p, t_s):
    """
    Get the specific heat of the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float
        The specific heat of the saturated vapor mixture in J/kg K.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_c_pm_sat(p, t_s)
    1022.2835902558337

    """
    c_pm_sat = hap.HAPropsSI('cp_ha', 'P', p, 'T', t_s, 'RH', 1.0)
    return c_pm_sat


def get_rho_m(p, t, t_dp):
    r"""
    Get the specific mass of the vapor mixture.

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
    float
        The specific mass of the vapor mixture in kg/m\ :sup:`3`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_rho_m(p, t, t_dp)
    1.213231099568598

    """
    v_ha = hap.HAPropsSI('Vha', 'P', p, 'T', t, 'Tdp', t_dp)
    rho_m = 1/v_ha
    return rho_m


def get_rho_m_sat(p, t_s):
    r"""
    Get the specific mass of the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float
        The specific mass of the saturated vapor mixture in kg/m\ :sup:`3`.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_rho_m_sat(p, t_s)
    1.2327562216963954

    """
    v_ha_sat = hap.HAPropsSI('Vha', 'P', p, 'T', t_s, 'RH', 1.0)
    rho_m_sat = 1/v_ha_sat
    return rho_m_sat


def get_k_m(p, t, t_dp):
    """
    Get the thermal conductivity of the vapor mixture.

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
    float
        The thermal conductivity of the vapor mixture in W/m K.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_k_m(p, t, t_dp)
    0.02563350730647246

    """
    k_m = hap.HAPropsSI('k', 'P', p, 'T', t, 'Tdp', t_dp)
    return k_m


def get_k_m_sat(p, t_s):
    """
    Get the thermal conductivity of the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float
        The thermal conductivity of the saturated vapor mixture in W/m K.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_k_m_sat(p, t_s)
    0.025260388108991345

    """
    k_m_sat = hap.HAPropsSI('k', 'P', p, 'T', t_s, 'RH', 1.0)
    return k_m_sat


def get_alpha_m(p, t, t_dp):
    r"""
    Get the thermal diffusivity of the vapor mixture.

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
    float
        The thermal diffusivity of the vapor mixture in m\ :sup:`2`\ /s.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_alpha_m(p, t, t_dp)
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
    r"""
    Get the thermal diffusivity of the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float
        The thermal diffusivity of the saturated vapor mixture in
        m\ :sup:`2`\ /s.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_alpha_m_sat(p, t_s)
    2.0044324561030463e-05

    """
    # Get properties needed to calculate alpha_m
    c_pm_sat = get_c_pm_sat(p, t_s)
    k_m_sat = get_k_m_sat(p, t_s)
    rho_m_sat = get_rho_m_sat(p, t_s)

    # Calculate alpha_m
    alpha_m_sat = k_m_sat/(c_pm_sat*rho_m_sat)
    return alpha_m_sat


def get_d_12(p, t, t_dp, ref):
    r"""
    Get the binary species diffusivity of the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.
    ref : {'Mills', 'Marrero', 'constant'}
        Reference for binary species diffusiity, see ``Notes``.

    Returns
    -------
    float
        The thermal diffusivity of the vapor mixture in m\ :sup:`2`\ /s.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> ref = 'Mills'
    >>> get_d_12(p, t, t_dp, ref)
    2.4306504684558495e-05

    >>> ref = 'Marrero'
    >>> get_d_12(p, t, t_dp, ref)
    2.365539793302829e-05

    >>> ref = 'constant'
    >>> get_d_12(p, t, t_dp, ref)
    2.416458085635347e-05

    Raises
    ------
    ValueError
        If `ref` is not in `{'Mills', 'Marrero', 'constant'}`.

    Notes
    -----
    For more information regarding the choices for `ref` see Appendix of [1]_.

    """
    p_norm = p/101325
    if ref == 'Mills':
        d_12 = 1.97e-5*(1/p_norm)*pow(t/256, 1.685)
        return d_12
    elif ref == 'Marrero':
        d_12 = 1.87e-10*pow(t, 2.072)/p_norm
        return d_12
    elif ref == 'constant':
        rho = get_rho_m(p, t, t_dp)
        mu = get_mu(p, t, t_dp)
        nu = mu/rho
        schmidt = 0.614
        d_12 = nu/schmidt
        return d_12
    else:
        err_msg = (
            "'{0}' is not a valid ref; try 'Mills',"
            " 'Marrero', or 'constant'.".format(ref)
            )
        raise ValueError(err_msg)


def get_x_1(p, t, t_dp):
    """
    Get the mole fraction of water vapor in mixture.

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
    float
        The mole fraction of water vapor in the vapor mixture in [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_x_1(p, t, t_dp)
    0.00982822815586041

    """
    x_1 = hap.HAPropsSI('Y', 'P', p, 'T', t, 'Tdp', t_dp)
    return x_1


def get_x_1_sat(p, t_s):
    """
    Get the mole fraction of water vapor in the saturated mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float
        The mole fraction of water vapor in the saturated vapor mixture in
        [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_x_1_sat(p, t_s)
    0.01376427605764327

    """
    x_1_sat = hap.HAPropsSI('Y', 'P', p, 'T', t_s, 'RH', 1.0)
    return x_1_sat


def get_m_1(p, t, t_dp):
    """
    Get the mass fraction of water vapor in the vapor mixture.

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
    float
        Mass fraction of water vapor in the vapor mixture in [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_m_1(p, t, t_dp)
    0.0061357476021502095

    """
    x_1 = get_x_1(p, t, t_dp)
    m_1 = x1_2_m1(x_1)
    return m_1


def get_m_1_sat(p, t_s):
    """
    Get the mass fraction of water vapor in the saturated vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float
        Mass fraction of water vapor in the saturated vapor mixture in [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_m_1_sat(p, t_s)
    0.008605868703401028

    """
    x_1_sat = get_x_1_sat(p, t_s)
    m_1_sat = x1_2_m1(x_1_sat)
    return m_1_sat


def get_h_fg_sat(t_s):
    """
    Get the specific enthalpy of vaporization for pure water.

    Parameters
    ----------
    t_s : int or float
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float
        Specific enthalpy of vaporization for pure water in J/kg.

    Examples
    --------
    >>> t_s = 285
    >>> get_h_fg_sat(t_s)
    2472806.6902607535

    """
    h_g = cp.PropsSI('H', 'T', t_s, 'Q', 1, 'water')
    h_f = cp.PropsSI('H', 'T', t_s, 'Q', 0, 'water')
    h_fg = h_g - h_f
    return h_fg


def x1_2_m1(x_1):
    """
    Convert the mole fraction to mass fraction.

    Parameters
    ----------
    x_1 : float
        Mole fraction of water vapor in [0, 1].

    Returns
    -------
    float
        Relative humidity in [0, 1].

    Examples
    --------
    >>> x_1 = 0.01
    >>> x1_2_m1(x_1)
    0.006243391414375084

    """
    numerator = x_1*M1
    denominator = x_1*M1 + (1-x_1)*M2
    m_1 = numerator/denominator
    return m_1


def get_mu(p, t, t_dp):
    """
    Get the dynamic viscocity of the vapor mixture.

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
    float
        The viscocity of the vapor mixture in Pa*s.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_mu(p, t, t_dp)
    1.800077369582236e-05

    """
    mu = hap.HAPropsSI('mu', 'P', p, 'T', t, 'Tdp', t_dp)
    return mu


# --------------------------------------------------------------------------- #
# Liquid Properties
# --------------------------------------------------------------------------- #

def get_c_pl(t):
    """
    Get the specific heat of pure liquid water.

    Parameters
    ----------
    t : int or float
        Temperature of the liquid water (condensed phase) in K.

    Returns
    -------
    float
        Specific heat of pure liquid water in J/kg K.

    Examples
    --------
    >>> t = 285
    >>> get_c_pl(t)
    4192.729295040042

    """
    c_pl = cp.PropsSI('Cpmass', 'T', t, 'Q', 0, 'water')
    return c_pl


# --------------------------------------------------------------------------- #
# Water Vapor Content
# --------------------------------------------------------------------------- #

def get_rh(p, t, t_dp):
    """
    Get the relative humidity of the vapor liquid mixture.

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
    float
        Relative humidity in [0, 1].

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_rh(p, t, t_dp)
    0.5165573311068835

    """
    rh = hap.HAPropsSI('RH', 'P', p, 'T', t, 'Tdp', t_dp)
    return rh


def get_tdp(p, t, rh):
    """
    Get the dew point temperature of the vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    rh : float.
        Relative humidity fraction between 0 and 1.

    Returns
    -------
    float
        The dew point temperature of the vapor mixture in K.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> rh = 0.5
    >>> get_tdp(p, t, rh)
    279.5268317988297

    """
    t_dp = hap.HAPropsSI('Tdp', 'P', p, 'T', t, 'R', rh)
    return t_dp


def get_mol_wgt(p, t, t_dp):
    """
    Get the molar mass of the vapor mixture.

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
    float
        The total molar mass of the vapor mixture in kg/mol.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_mol_wgt(p, t, t_dp)
    28.856390729921483

    """
    x_1 = get_x_1(p, t, t_dp)
    M = x_1*M1 + (1 - x_1)*M2
    return M


def get_gamma(p, t, t_dp):
    """
    Get the coefficient of volumetric expansion of the vapor mixture.

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
    float
        The coefficient of volumetric expansion of the vapor mixture.
        in m:math:`^-3`

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_gamma(p, t, t_dp)
    0.49602914637400736

    """
    # Suffix `-r` is used to denote the reference state
    rho_r = get_rho_m(p, t, t_dp)
    mol_wgt_r = get_mol_wgt(p, t, t_dp)
    gamma = (1/rho_r)*(mol_wgt_r/M1 - 1)
    return gamma


def get_beta_m1(p, t, t_dp, t_s):
    """
    Get the mass transfer rate coefficient of the stefan tube system.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.
    t_s : int or float
        Saturated liquid surface temperature in K.

    Returns
    -------
    float
        The mass transfer rate coefficient.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> t_s = 285
    >>> get_beta_m1(p, t, t_dp, t_s)
    0.002491563166729926

    """
    m_1s = get_m_1_sat(p, t_s)
    m_1e = get_m_1(p, t, t_dp)
    beta_m1 = (m_1s - m_1e)/(1-m_1s)
    return beta_m1
