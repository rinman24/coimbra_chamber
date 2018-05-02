from CoolProp import HumidAirProp as hap

M1 = 18.015
M2 = 28.964


def cpm(p, t, t_dp):
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
    cpm : float
        The specific heat of the vapor mixture in J/kg K.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> props.cpm(p, t, t_dp)
    1017.641910841458
    """
    cpm = hap.HAPropsSI('cp_ha', 'P', p, 'T', t, 'Tdp', t_dp)
    return cpm


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
