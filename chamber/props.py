from CoolProp import HumidAirProp as hap

M1 = 18.015
M2 = 28.964


def get_cp_m(p, t, t_dp):
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
    cp_m : float
        The specific heat of the vapor mixture in J/kg K.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.get_cp_m(p, t, t_dp)
    1017.641910841458
    """
    cp_m = hap.HAPropsSI('cp_ha', 'P', p, 'T', t, 'Tdp', t_dp)
    return cp_m


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
    c_pm = get_cp_m(p, t, t_dp)
    k_m = get_k_m(p, t, t_dp)
    rho_m = get_rho_m(p, t, t_dp)

    # Calculate alpha_m
    alpha_m = k_m/(c_pm*rho_m)
    return alpha_m


def tdp2rh(p, t, t_dp):
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
        Relative humidity in [0, 1]

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.tdp2rh(p, t, t_dp)
    0.5165573311068835
    """
    rh = hap.HAPropsSI('RH', 'P', p, 'T', t, 'Tdp', t_dp)
    return rh


def x12m1(x1):
    """m1 based on x1.

    Parameters
    ----------
    x1 : float
        Mole fraction of water vapor in [0, 1]

    Returns
    -------
    m1 : float
        Relative humidity in [0, 1]

    Examples
    --------
    >>> x1 = 0.01
    >>> props.tdp2rh(x1)
    0.006243391414375084
    """
    numerator = x1*M1
    denominator = x1*M1 + (1-x1)*M2
    m1 = numerator/denominator
    return m1
