from CoolProp import HumidAirProp as hap


def cpm(p, t, t_dp):
    """The specific heat of the vapor mixture.

    Parameters `p`, `t`, and `t_dp` must all be the same length.
    
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
