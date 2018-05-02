from CoolProp import HumidAirProp as hap


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
    """RH based on `p`, `t` and `t_dp`.

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
