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

from chamber.models import uncertainty as unc

M1 = 18.015
M2 = 28.964


# --------------------------------------------------------------------------- #
# Vapor Mixture Properties
# --------------------------------------------------------------------------- #

def get_c_pm(p, t, t_dp):
    """
    Get the specific heat of th evapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        The specific heat of the vapor mixture in J/kg K.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_c_pm(p, t, t_dp)
    1017.641910841458

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_c_pm(p, t, t_dp)
    (1017.641910841458, 0.8642246765946311)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_c_pm, p, t, t_dp)
    c_pm = hap.HAPropsSI('cp_ha', 'P', p, 'T', t, 'Tdp', t_dp)
    return c_pm


def get_c_pm_sat(p, t_s):
    """
    Get the specific heat of the saturated vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t_s : int, float, or tuple
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float or tuple
        The specific heat of the saturated vapor mixture in J/kg K.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_c_pm_sat(p, t_s)
    1022.2835902558337

    >>> p = (101325, 1)
    >>> t_s = (285, 1)
    >>> get_c_pm_sat(p, t_s)
    (1022.2835902558337, 1.163174765231247)

    """
    if type(p) is tuple and type(t_s) is tuple:
        return unc.prop_uncertainty(get_c_pm_sat, p, t_s)
    c_pm_sat = hap.HAPropsSI('cp_ha', 'P', p, 'T', t_s, 'RH', 1.0)
    return c_pm_sat


def get_rho_m(p, t, t_dp):
    r"""
    Get the specific mass of the vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        The specific mass of the vapor mixture in kg/m\ :sup:`3`.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_rho_m(p, t, t_dp)
    1.213231099568598

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_tho_m(p, t, t_dp)
    (1.213231099568598, 0.00452319762615927)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_rho_m, p, t, t_dp)
    v_ha = hap.HAPropsSI('Vha', 'P', p, 'T', t, 'Tdp', t_dp)
    rho_m = 1/v_ha
    return rho_m


def get_rho_m_sat(p, t_s):
    r"""
    Get the specific mass of the saturated vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t_s : int, float, or tuple
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float or tuple
        The specific mass of the saturated vapor mixture in kg/m\ :sup:`3`.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_rho_m_sat(p, t_s)
    1.2327562216963954

    >>> p = (101325, 1)
    >>> t_s = (285, 1)
    >>> get_rho_m_sat(p, t_s)
    (1.2327562216963954,  0.004778162710130651)

    """
    if type(p) is tuple and type(t_s) is tuple:
        return unc.prop_uncertainty(get_rho_m_sat, p, t_s)
    v_ha_sat = hap.HAPropsSI('Vha', 'P', p, 'T', t_s, 'RH', 1.0)
    rho_m_sat = 1/v_ha_sat
    return rho_m_sat


def get_k_m(p, t, t_dp):
    """
    Get the thermal conductivity of the vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        The thermal conductivity of the vapor mixture in W/m K.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_k_m(p, t, t_dp)
    0.02563350730647246

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_k_m(p, t, t_dp)
    (0.02563350730647246, 7.465143177219635e-05)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_k_m, p, t, t_dp)
    k_m = hap.HAPropsSI('k', 'P', p, 'T', t, 'Tdp', t_dp)
    return k_m


def get_k_m_sat(p, t_s):
    """
    Get the thermal conductivity of the saturated vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t_s : int, float, or tuple
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float or tuple
        The thermal conductivity of the saturated vapor mixture in W/m K.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_k_m_sat(p, t_s)
    0.025260388108991345

    >>> p = (101325, 1)
    >>> t_s = (285, 1)
    >>> get_k_m_sat(p, t_s)
    (0.025260388108991345, 7.454320267070297e-05)

    """
    if type(p) is tuple and type(t_s) is tuple:
        return unc.prop_uncertainty(get_k_m_sat, p, t_s)
    k_m_sat = hap.HAPropsSI('k', 'P', p, 'T', t_s, 'RH', 1.0)
    return k_m_sat


def get_alpha_m(p, t, t_dp):
    r"""
    Get the thermal diffusivity of the vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        The thermal diffusivity of the vapor mixture in m\ :sup:`2`\ /s.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_alpha_m(p, t, t_dp)
    2.076201562300882e-05

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_alpha_m(p, t, t_dp)
    (2.076201562300882e-05, 1.432817367533441e-07)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_alpha_m, p, t, t_dp)

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

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t_s : int, float, or tuple
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float or tuple
        The thermal diffusivity of the saturated vapor mixture in
        m\ :sup:`2`\ /s.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_alpha_m_sat(p, t_s)
    2.0044324561030463e-05

    >>> p = (101325, 1)
    >>> t_s = (285, 1)
    >>> get_alpha_m_sat(p, t_s)
    (2.0044324561030463e-05, 1.1495765792420251e-07)

    """
    if type(p) is tuple and type(t_s) is tuple:
        return unc.prop_uncertainty(get_alpha_m_sat, p, t_s)

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

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.
    ref : {'Mills', 'Marrero', 'constant'}
        Reference for binary species diffusiity, see ``Notes``.

    Returns
    -------
    float or tuple
        The thermal diffusivity of the vapor mixture in m\ :sup:`2`\ /s.
        Uncertainty is reported as the second item in the `tuple`.

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

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> ref = 'Mills'
    >>> get_d_12(p, t, t_dp, ref)
    (2.4306504684558495e-05, 1.4163719437180477e-07)

    >>> ref = 'Marrero'
    >>> get_d_12(p, t, t_dp, ref)
    (2.365539793302829e-05, 1.695612836276839e-07)

    >>> ref = 'constant'
    >>> get_d_12(p, t, t_dp, ref)
    (2.416458085635347e-05, 1.5030027598073996e-07)

    Raises
    ------
    ValueError
        If `ref` is not in `{'Mills', 'Marrero', 'constant'}`.

    Notes
    -----
    For more information regarding the choices for `ref` see Appendix of [1]_.

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_d_12, p, t, t_dp, ref)

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

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        The mole fraction of water vapor in the vapor mixture in [0, 1].
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_x_1(p, t, t_dp)
    0.00982822815586041

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_x_1(p, t, t_dp)
    (0.00982822815586041, 0.0006963488001588882)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_x_1, p, t, t_dp)
    x_1 = hap.HAPropsSI('Y', 'P', p, 'T', t, 'Tdp', t_dp)
    return x_1


def get_x_1_sat(p, t_s):
    """
    Get the mole fraction of water vapor in the saturated mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t_s : int, float, or tuple
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float or tuple
        The mole fraction of water vapor in the saturated vapor mixture in
        [0, 1].
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_x_1_sat(p, t_s)
    0.01376427605764327

    >>> p = (101325, 1)
    >>> t_s = (285, 1)
    >>> get_x_1_sat(p, t_s)
    (0.01376427605764327, 0.0009358863844873)

    """
    if type(p) is tuple and type(t_s) is tuple:
        return unc.prop_uncertainty(get_x_1_sat, p, t_s)
    x_1_sat = hap.HAPropsSI('Y', 'P', p, 'T', t_s, 'RH', 1.0)
    return x_1_sat


def get_m_1(p, t, t_dp):
    """
    Get the mass fraction of water vapor in the vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        Mass fraction of water vapor in the vapor mixture in [0, 1].
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_m_1(p, t, t_dp)
    0.0061357476021502095

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_m_1(p, t, t_dp)
    (0.0061357476021502095, 0.0004364659611057649)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_m_1, p, t, t_dp)
    x_1 = get_x_1(p, t, t_dp)
    m_1 = x1_2_m1(x_1)
    return m_1


def get_m_1_sat(p, t_s):
    """
    Get the mass fraction of water vapor in the saturated vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t_s : int, float, or tuple
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float or tuple
        Mass fraction of water vapor in the saturated vapor mixture in [0, 1].
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t_s = 285
    >>> get_m_1_sat(p, t_s)
    0.008605868703401028

    >>> p = (101325, 1)
    >>> t_s = (285, 1)
    >>> get_m_1_sat(p, t_s)
    (0.008605868703401028, 0.0005884161208112876)

    """
    if type(p) is tuple and type(t_s) is tuple:
        return unc.prop_uncertainty(get_m_1_sat, p, t_s)
    x_1_sat = get_x_1_sat(p, t_s)
    m_1_sat = x1_2_m1(x_1_sat)
    return m_1_sat


def get_h_fg_sat(t_s):
    """
    Get the specific enthalpy of vaporization for pure water.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    t_s : int, float, or tuple
        Dry bulb temperature of saturated vapor mixture in K.

    Returns
    -------
    float or tuple
        Specific enthalpy of vaporization for pure water in J/kg.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> t_s = 285
    >>> get_h_fg_sat(t_s)
    2472806.6902607535

    >>> t_s = (285, 1)
    >>> get_h_fg_sat(t_s)
    (2472806.6902607535, 2367.4987125825137)

    """
    if type(t_s) is tuple:
        return unc.prop_uncertainty(get_h_fg_sat, t_s)
    h_g = cp.PropsSI('H', 'T', t_s, 'Q', 1, 'water')
    h_f = cp.PropsSI('H', 'T', t_s, 'Q', 0, 'water')
    h_fg = h_g - h_f
    return h_fg


def x1_2_m1(x_1):
    """
    Convert the mole fraction to mass fraction.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    x_1 : float or tuple
        Mole fraction of water vapor in [0, 1].

    Returns
    -------
    float or tuple
        Relative humidity in [0, 1].
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> x_1 = 0.01
    >>> x1_2_m1(x_1)
    0.006243391414375084

    >>> x_1 = (0.01, 0.001)
    >>> x1_2_m1(x_1)
    (0.006243391414375084, 0.0006269461282050444)

    """
    if type(x_1) is tuple:
        return unc.prop_uncertainty(x1_2_m1, x_1)
    numerator = x_1*M1
    denominator = x_1*M1 + (1-x_1)*M2
    m_1 = numerator/denominator
    return m_1


def get_mu(p, t, t_dp):
    """
    Get the dynamic viscocity of the vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        The viscocity of the vapor mixture in Pa*s.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_mu(p, t, t_dp)
    1.800077369582236e-05

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_mu(p, t, t_dp)
    (1.800077369582236e-5, 5.197108679739007e-08)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_mu, p, t, t_dp)
    mu = hap.HAPropsSI('mu', 'P', p, 'T', t, 'Tdp', t_dp)
    return mu


# --------------------------------------------------------------------------- #
# Liquid Properties
# --------------------------------------------------------------------------- #

def get_c_pl(t):
    """
    Get the specific heat of pure liquid water.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    t : int, float, or tuple
        Temperature of the liquid water (condensed phase) in K.

    Returns
    -------
    float or tuple
        Specific heat of pure liquid water in J/kg K.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> t = 285
    >>> get_c_pl(t)
    4192.729295040042

    >>> t = (285, 1)
    >>> get_c_pl(t)
    (4192.729295040042, 1.4683242561413863)

    """
    if type(t) is tuple:
        return unc.prop_uncertainty(get_c_pl, t)
    c_pl = cp.PropsSI('Cpmass', 'T', t, 'Q', 0, 'water')
    return c_pl


# --------------------------------------------------------------------------- #
# Water Vapor Content
# --------------------------------------------------------------------------- #

def get_rh(p, t, t_dp):
    """
    Get the relative humidity of the vapor liquid mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        Relative humidity in [0, 1].
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_rh(p, t, t_dp)
    0.5165573311068835

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_rh(p, t, t_dp)
    (0.5165573311068835, 0.07299917217578145)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_rh, p, t, t_dp)
    rh = hap.HAPropsSI('RH', 'P', p, 'T', t, 'Tdp', t_dp)
    return rh


def get_tdp(p, t, rh):
    """
    Get the dew point temperature of the vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    rh : float ro tuple
        Relative humidity fraction between 0 and 1.

    Returns
    -------
    float or tuple
        The dew point temperature of the vapor mixture in K.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> rh = 0.5
    >>> get_tdp(p, t, rh)
    279.5268317988297

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> rh = (0.5, 0.01)
    >>> get_tdp(p, t, rh)
    (279.5268317988297, 1.2109280624741814)

    """
    if type(p) is tuple and type(t) is tuple and type(rh) is tuple:
        return unc.prop_uncertainty(get_tdp, p, t, rh)
    t_dp = hap.HAPropsSI('Tdp', 'P', p, 'T', t, 'R', rh)
    return t_dp


def get_mol_wgt(p, t, t_dp):
    """
    Get the molar mass of the vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuole
        The total molar mass of the vapor mixture in kg/mol.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_mol_wgt(p, t, t_dp)
    28.856390729921483

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_mol_wgt(p, t, t_dp)
    (28.856390729921483, 0.0076243230129406925)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_mol_wgt, p, t, t_dp)
    x_1 = get_x_1(p, t, t_dp)
    M = x_1*M1 + (1 - x_1)*M2
    return M


def get_gamma(p, t, t_dp):
    """
    Get the coefficient of volumetric expansion of the vapor mixture.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.

    Returns
    -------
    float or tuple
        The coefficient of volumetric expansion of the vapor mixture.
        in m:math:`^-3`
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_gamma(p, t, t_dp)
    0.49602914637400736

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> get_gamma(p, t, t_dp)
    (0.49602914637400736, 0.0019386355678004952)

    """
    if type(p) is tuple and type(t) is tuple and type(t_dp) is tuple:
        return unc.prop_uncertainty(get_gamma, p, t, t_dp)
    # Suffix `-r` is used to denote the reference state
    rho_r = get_rho_m(p, t, t_dp)
    mol_wgt_r = get_mol_wgt(p, t, t_dp)
    gamma = (1/rho_r)*(mol_wgt_r/M1 - 1)
    return gamma


def get_beta_m1(p, t, t_dp, t_s):
    """
    Get the mass transfer rate coefficient of the stefan tube system.

    Use all `tuple` arguments to report and calculate uncertainty. If only
    some values have an uncertainty use zeros to report values without
    uncertainty. eg. a = (123, 1), b = (456, 0).

    Parameters
    ----------
    p : int, float, or tuple
        Pressure in Pa.
    t : int, float, or tuple
        Dry bulb temperature in K.
    t_dp : int, float, or tuple
        Dew point temperature in K.
    t_s : int, float, or tuple
        Saturated liquid surface temperature in K.

    Returns
    -------
    float or tuple
        The mass transfer rate coefficient.
        Uncertainty is reported as the second item in the `tuple`.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> t_s = 285
    >>> get_beta_m1(p, t, t_dp, t_s)
    0.002491563166729926

    >>> p = (101325, 1)
    >>> t = (290, 1)
    >>> t_dp = (280, 1)
    >>> t_s = (285, 1)
    >>> get_beta_m1(p, t, t_dp, t_s)
    (0.002491563166729926, 0.0010096089583837994)

    """
    if (type(p) is tuple and type(t) is tuple and
            type(t_dp) is tuple and type(t_s) is tuple):
        return unc.prop_uncertainty(get_beta_m1, p, t, t_dp, t_s)
    m_1s = get_m_1_sat(p, t_s)
    m_1e = get_m_1(p, t, t_dp)
    beta_m1 = (m_1s - m_1e)/(1 - m_1s)
    return beta_m1
