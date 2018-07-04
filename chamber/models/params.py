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
    get_sherwood

"""

from math import log

from chamber.models import props
from chamber import const

RADIUS = 0.015


def get_schmidt(p, t, t_dp, ref):
    """
    Get Schmidt number for vapor mixture.

    This function uses the humid air property getter functions in props.py to
    calculate the Schmidt number, the ratio of momentum diffusivity and
    mass diffusivity, of the vapor liquid mixture.

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
        The schmidt number for the vapor mixture.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_schmidt(p, t, t_dp, 'Mills')
    0.6104149007992397

    Notes
    -----
    For more information regarding the choices for `ref` see Appendix of [4]_.

    References
    ----------
    .. [4] Mills, A. F. and Coimbra, C. F. M., 2016
       *Mass Transfer: Third Edition*, Temporal Publishing, LLC.

    """
    # Get vapor properties
    d_12 = props.get_d_12(p, t, t_dp, ref)
    rho = props.get_rho_m(p, t, t_dp)
    mu = props.get_mu(p, t, t_dp)
    nu = mu/rho

    # Calculate Schmidt number
    schmidt = nu/d_12
    return schmidt


def get_grashof(p, t, t_dp, t_s):
    """
    Get Grashof number for vapor mixture.

    This function uses the humid air property getter functions in props.py to
    calculate the Grashof number, the ratio of the buoyant force and
    the viscous force, of the vapor liquid mixture.

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
        The Grashof number for the vapor mixture.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> t_s = 289.5
    >>> get_grashof(p, t, t_dp, t_s)
    230.11072973650792

    """
    # Constants
    g = const.ACC_GRAV
    radius = RADIUS

    # Calculate water vapor parameters
    gamma_1 = props.get_gamma(p, t, t_dp)
    m_1s = props.get_m_1_sat(p, t_s)
    m_1e = props.get_m_1(p, t, t_dp)

    # Get vapor properties
    rho = props.get_rho_m(p, t, t_dp)
    mu = props.get_mu(p, t, t_dp)
    nu = mu/rho
    beta = 1/t

    # Calculate Grashof number (Gr)
    grashof = (g
               * (gamma_1*rho*(m_1s - m_1e) + beta*(t_s - t))
               * pow(radius, 3)
               / pow(nu, 2))

    if grashof < 0:
        return 0
    else:
        return grashof


def get_prandtl(p, t, t_dp):
    """
    Get Prandtl number for vapor mixture.

    This function uses the humid air property getter functions in props.py to
    calculate the Prandtl number, the ratio of momentum diffusivity and
    thermal diffusivity, of the vapor liquid mixture.

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
        The Prandtl number for the vapor mixture.

    Examples
    --------
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> get_prandtl(p, t, t_dp)
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


def get_sherwood(l, m_dot_pp, p, t, t_dp, t_s, ref):
    """
    Get Sherwood number for vapor mixture.

    This function uses the humid air property getter functions in props.py to
    calculate the Sherwood number, the ratio of convective mass transfer and
    diffusive mass transport, of the vapor liquid mixture.

    Parameters
    ----------
    l : int or float
        The length of the stefan tube from the water surface in m.
    m_dot_pp : int or float
        The evaporation flux in kg/s/m\\ :sup:`3`.
    p : int or float
        Pressure in Pa.
    t : int or float
        Dry bulb temperature in K.
    t_dp : int or float
        Dew point temperature in K.
    t_s : int or float
        Saturated liquid surface temperature in K.
    ref : {'Mills', 'Marrero', 'constant'}
        Reference for binary species diffusiity, see ``Notes``.


    Returns
    -------
    float
        The Sherwood number for the vapor mixture.

    Examples
    --------
    >>> l = 0.044
    >>> m_dot_pp = 1.2e-6
    >>> p = 101325
    >>> t = 290
    >>> t_dp = 280
    >>> t_s = 289
    >>> ref = 'constant'
    >>> get_sherwood(l, m_dot_pp, p, t, t_dp, t_s, ref)
    0.3540373651492251

    Notes
    -----
    For more information regarding the choices for `ref` see Appendix of [2]_.

    References
    ----------
    .. [2] Mills, A. F. and Coimbra, C. F. M., 2016
       *Mass Transfer: Third Edition*, Temporal Publishing, LLC.

    """
    # Get vapor properties
    beta_m1 = props.get_beta_m1(p, t, t_dp, t_s)
    d_12 = props.get_d_12(p, t, t_dp, ref)
    rho = props.get_rho_m(p, t, t_dp)

    # Calculate Sherwood number (Sh)
    sherwood = m_dot_pp*l/(rho*d_12*log(1+beta_m1))
    return sherwood
