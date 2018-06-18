"""
Nondimensional parameters.

Attributes
----------
    RADIUS : float
        Inside radius of Stefan tube used in experiments

Functions
---------
    get_schmidt
    get_grashof
"""

from chamber.models import props
from chamber import const

RADIUS = 0.015

def get_schmidt(p, t, t_dp, ref):
    """Get Schmidt number for vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.
    ref : {'Mills', 'Marrero'}
        Reference for binary species diffusiity, see ``Notes``.

    Returns
    -------
    schmidt : float
        The schmidt number for the vapor mixture.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> params.get_schmidt(p, t, t_dp, 'Mills')
    0.6104149007992397

    Notes
    -----
    For more information regarding the choices for `ref` see Appendix of [1]_.

    References
    ----------
    .. [1] Mills, A. F. and Coimbra, C. F. M., 2016
       *Mass Transfer: Third Edition*, Temporal Publishing, LLC.

    """
    D_12 = props.get_d_12(p, t, ref)
    rho = props.get_rho_m(p, t, t_dp)
    mu = props.get_mu(p, t, t_dp)

    # Calculate Schmidt number
    schmidt = mu/(rho*D_12)
    return schmidt


def get_grashof(p, t, t_dp):
    """Get Grashof number for vapor mixture.

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
    grashof : float
        The Grashof number for the vapor mixture.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> params.get_grashof(p, t, t_dp)
    231.5493976780182

    """
    # Constants
    g = const.ACC_GRAV
    radius = RADIUS

    # Calculate water vapor parameters
    gamma_1 = props.get_gamma(p, t, t_dp)
    m_1s = props.get_m_1_sat(p, t)
    m_1e = props.get_m_1(p, t, t_dp)

    # Get vapor properties
    rho = props.get_rho_m(p, t, t_dp)
    mu = props.get_mu(p, t, t_dp)
    nu = mu/rho

    # Calculate Schmidt number (Sh)
    grashof = g*gamma_1*rho*(m_1s-m_1e)*pow(radius, 3)/pow(nu, 2)
    return grashof
