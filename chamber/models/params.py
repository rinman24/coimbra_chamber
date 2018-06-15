"""
Nondimensional parameters.

Functions
---------
    get_schmidt
    get_grashof
"""

from chamber.models import props
from chamber import const


def get_schmidt(p, t, t_dp, ref):
	"""The Schmidt number for the vapor mixture.

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
	d_12 = props.get_d_12(p, t, ref)
	rho = props.get_rho_m(p, t, t_dp)
	mu = props.get_mu(p, t, t_dp)

	# Calculate Schmidt number
	schmidt = mu/(rho*d_12)
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
    157.31009268101118

    """
    g = const.ACC_GRAV
    R = const.R_IN_TUBE
    gamma = props.get_gamma(p, t, t_dp)
    mu = props.get_mu(p, t, t_dp)
    m_s = props.get_m_1_sat(p, t)
    m_1 = props.get_m_1(p, t, t_dp)
    rho = props.get_rho_m(p, t, t_dp)

    # Calculate Schmidt number
    grashof = rho*g*gamma*(m_s-m_1)*(R**3)/(mu/rho)**2
    return grashof
