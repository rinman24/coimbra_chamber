"""Docstring."""
from math import exp, log

import chamber.const as const


def p_sat_liq(temp_k):
    """Use Hardy (1998) to return P_sat(T_K) in Pa.
    
    This function uses Hardy (1998), "ITS-90 Formulations for Vapor Pressure, Frostpoint
    Temperature, Dewpoint Temperature, and Enhancement Factors in the Range -100 to +100 C," to
    calculate the saturation vapor pressure over liquid water in the range 0 to 100 C.
    
    Parameters
    ----------
    temp_k : float
    	Temperature in Kelvin.
    
    Returns
    -------
    p_sat : float
    	Saturation vapor pressure over liquid water in Pa.
    """
    p_sat = sum([const.G_COEF[i] * pow(temp_k, i-2) for i in range(7)]) + const.G_COEF[7]*log(temp_k)
    p_sat = exp(p_sat)
    return p_sat

def enh_fact_liq(temp_k, p_pa, p_sat):
    """Use Hardy (1998) to return f_e.

    This function uses Hardy (1998), "ITS-90 Formulations for Vapor Pressure, Frostpoint
    Temperature, Dewpoint Temperature, and Enhancement Factors in the Range -100 to +100 C," to
    calculate the enhancement factor over liquid water in the range 0 to 100 C.

    Parameters
    ----------
    temp_k : float
    	Temperature in Kelvin.
    p_pa : float
    	Total pressure in Pa.
    p_sat : float
    	Saturation vapor pressure of water over liquid water in Pa.
    
    Returns
    -------
    f_e : float
    	Enhancement factor over liquid water.
    """
    alpha = 0
    beta = 0
    for i in range(4):
        alpha += const.A_COEF[i] * pow(temp_k, i)
        beta += const.B_COEF[i] * pow(temp_k, i)
    beta = exp(beta)
    f_e = exp(alpha*(1 - p_sat/p_pa) + beta*(p_pa/p_sat - 1))
    return f_e

def eff_p_sat_liq(temp_k, p_pa):
    """Use p_sat_liq and enh_fact_liq to return effective saturation pressure.

    This function uses Hardy (1998), "ITS-90 Formulations for Vapor Pressure, Frostpoint
    Temperature, Dewpoint Temperature, and Enhancement Factors in the Range -100 to +100 C," to
    calculate the effective saturation vapor pressure over liquid water in the range 0 to 100 C.

    Parameters
    ----------
    temp_k : float
    	Temperature in Kelvin.
    p_pa : float
    	Total pressure in Pa.
    
    Returns
    -------
    eff_p : float
    	Effective saturation vapor pressure over liquid water.
    """
    p_sat = p_sat_liq(temp_k)
    enh_fact = enh_fact_liq(temp_k, p_pa, p_sat)
    return enh_fact*p_sat

def rel_humidity(temp_k, temp_dew, p_pa, eff = True):
	"""Use eff_p_sat_liq, or p_sat_liq to calculate relative humidity.

    This function uses eff_p_sat_liq if eff is True or no argument is given,
    or p_sat_liq if eff is False to calculate the relative humidity of
    liquid water in the range 0 to 100 C.

    Parameters
    ----------
    temp_k : float
    	Temperature in Kelvin.
    temp_dew : float
    	Dew Point Temperature in Kelvin.
    p_pa : float
    	Total pressure in Pa.
    
    Returns
    -------
    rel_hum : float
    	Relative Humidity percentage in decimal form.
    """
	if eff == False:
		rel_hum = p_sat_liq(temp_dew)/p_sat_liq(temp_k)
	if eff == True:
		rel_hum = eff_p_sat_liq(temp_dew, p_pa)/eff_p_sat_liq(temp_k, p_pa)
	return rel_hum
