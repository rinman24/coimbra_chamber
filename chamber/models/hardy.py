import math

G_COEFF = (-2.8365744e3, -6.028076559e3, 1.954263612e1, -2.737830188e-2,
           1.6261698e-5, 7.0229056e-10, -1.8680009e-13, 2.7150305)

K_COEFF = (-5.8666426e3, 2.232870244e1, 1.39387003e-2, -3.4262402e-5,
           2.7040955e-8, 6.7063522e-1)

A_COEFF_WATER = (-1.6302041e-1, 1.8071570e-3, -6.7703064e-6, 8.5813609e-9)

B_COEFF_WATER = (-5.9890467e1, 3.4378043e-1, -7.7326396e-4, 6.3405286e-7)

A_COEFF_ICE = (-7.1044201e-2, 8.6786223e-4, -3.5912529e-6, 5.0194210e-9)

B_COEFF_ICE = (-8.2308868e1, 5.6519110e-1, -1.5304505e-3, 1.5395086e-6)


def get_p_sat(p_in, t_in):
    enh_fact, p_sat_ideal = _get_enh_fact(p_in, t_in, retrun_p=True)
    p_sat = enh_fact*p_sat_ideal
    return p_sat 


def _get_p_sat_water_ideal(t_in):
    """
    Valid from 0 C to 100 C, extrapolated to -100 to 200 in literature.
    """
    sum_ = sum(G_COEFF[i] * pow(t_in, i-2) for i in range(7))
    last_term = G_COEFF[7] * math.log(t_in)
    p_sat_water = math.exp(sum_ + last_term)
    return p_sat_water


def _get_p_sat_ice_ideal(t_in):
    """Valid from -100 C to 0 C."""
    sum_ = sum(K_COEFF[i] * pow(t_in, i-1) for i in range(5))
    last_term = K_COEFF[5] * math.log(t_in)
    p_sat_ice = math.exp(sum_ + last_term)
    return p_sat_ice


def _get_enh_alpha(t_in):
    if t_in >= 223.15 and t_in < 273.15:
        # Ice
        alpha = sum(A_COEFF_ICE[i] * pow(t_in, i) for i in range(4))
        return alpha
    elif t_in >= 273.15 and t_in < 373.15:
        # Water
        alpha = sum(A_COEFF_WATER[i] * pow(t_in, i) for i in range(4))
        return alpha
    else:
        err_msg = (
            "`t_in` must be between 223.15 K and 373.15 K."
            )
        raise ValueError(err_msg)


def _get_enh_beta(t_in):
    if t_in >= 223.15 and t_in < 273.15:
        # Ice
        sum_ = sum(B_COEFF_ICE[i] * pow(t_in, i) for i in range(4))
        beta = math.exp(sum_)
        return beta
    elif t_in >= 273.15 and t_in < 373.15:
        # Water
        sum_ = sum(B_COEFF_WATER[i] * pow(t_in, i) for i in range(4))
        beta = math.exp(sum_)
        return beta
    else:
        err_msg = (
            "`t_in` must be between 223.15 K and 373.15 K."
            )
        raise ValueError(err_msg)


def _get_enh_fact(p_in, t_in, retrun_p=False):
    if t_in >= 223.15 and t_in < 273.15:
        # Ice
        p_sat_ideal = _get_p_sat_ice_ideal(t_in)
    elif t_in >= 273.15 and t_in < 373.15:
        # Water
        p_sat_ideal = _get_p_sat_water_ideal(t_in)
    else:
        err_msg = (
            "`t_in` must be between 223.15 K and 373.15 K."
            )
        raise ValueError(err_msg)
    alpha = _get_enh_alpha(t_in)
    beta = _get_enh_beta(t_in)

    left_term = alpha * (1 - (p_sat_ideal/p_in))
    right_term = beta * ((p_in/p_sat_ideal)-1)
    enh_fact = math.exp(right_term + left_term)
    if retrun_p:
        return enh_fact, p_sat_ideal
    else:
        return enh_fact
