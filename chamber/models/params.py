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
    get_prandtl

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
    # Get vapor properties
    D_12 = props.get_d_12(p, t, ref)
    rho = props.get_rho_m(p, t, t_dp)
    mu = props.get_mu(p, t, t_dp)

    # Calculate Schmidt number
    schmidt = mu/(rho*D_12)
    return schmidt


def get_grashof(p, t_e, t_s, t_dp):
    """Get Grashof number for vapor mixture.

    Parameters
    ----------
    p : int or float
        Pressure in Pa.
    t_e : int or float
        Dry bulb temperature in K.
    t_s : int or float
        Water surface temperature in K.
    t_dp : int or float
        Dew point temperature in K.

    Returns
    -------
    grashof : float
        The Grashof number for the vapor mixture.

    Examples
    --------
    >>> p = 101325
    >>> t_e = 290
    >>> t_s = 289
    >>> t_dp = 280
    >>> params.get_grashof(p, t_e, t_s, t_dp)
    456.280130439354

    """
    # Constants
    g = const.ACC_GRAV
    radius = RADIUS

    # Calculate water vapor parameters
    gamma_1 = props.get_gamma(p, t_e, t_dp)
    m_1s = props.get_m_1_sat(p, t_s)
    m_1e = props.get_m_1(p, t_e, t_dp)

    # Get vapor properties
    rho = props.get_rho_m(p, t_e, t_dp)
    mu = props.get_mu(p, t_e, t_dp)
    nu = mu/rho

    # Calculate Grashof number (Gr)
    grashof = g*gamma_1*rho*(m_1s-m_1e)*pow(radius, 3)/pow(nu, 2) + (t_s-t_e)/t_e
    return grashof


def get_prandtl(p, t, t_dp):
    """Get Prandtl number for vapor mixture.

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
    prandtl : float
        The Prandtl number for the vapor mixture.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> params.get_prandtl(p, t, t_dp)
    0.7146248666414813

    """
    # Get vapor properties
    alpha = props.get_alpha_m(p, t, t_dp)
    rho = props.get_rho_m(p, t, t_dp)
    mu = props.get_mu(p, t, t_dp)
    nu = mu/rho

    # Calculate Prandtl number (Pr)
    prandtl = nu/alpha
    return prandtl
