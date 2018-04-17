"""
This module contains several classes required for modeling simultaneous
heat and mass transfer problems from a Stefan tube.

Classes:
    Properties: Thermophysical properties as a function of reference state.
"""

import CoolProp.HumidAirProp as hap


class Properties:
    """
    Use reference state to caclulate thermophysical properties.

    Calculates thermophysical properties as a function of a given reference
    state. A reference state is specified by a pressure `p`, temperature `t`,
    and water vapor mole fraction `x`. For the sake of clarity, properties are
    divided into two types: primary and secondary. Primary properties cannot be
    decomposed into subsequent primary properties. Secondary properties are
    composed of primary properties. For example, thermal conductivity `k`,
    specific heat at constand pressure per kg humid air `cp`, and specific mass
    `rho` would be considered primary properties. On the other hand, the
    mixture thermal diffusivity `alpha` = `k` / (`rho`*`cp`) would be
    considered a secondary property since it is composed or three primary
    properties.

    Public Methods:
        eval: evaluate thermophysical properties
    Instance Variables:
        alpha: Thermal diffusivity of the humid air, [m^2/s]
        cp: Specific heat at constant pressure per unit humid air, [J/kg K]
        d12: Binary pecies diffusivity for water vapor and dry air, [m^2/s]
        k: Thermal Conductivity of the humid air, [W/m K]
        rho: Specific mass of the humid air, [kg humid air/m^3]
    """

    def __init__(self):
        """
        Return a new instance of `Properties` with all attributes set to `None`.
        """
        self._rho = None
        self._k = None
        self._cp = None

        self._alpha = None
        self._d12 = None

    # ----------------------------------------------------------------------- #
    # Read only addtibutes
    # ----------------------------------------------------------------------- #
    @property
    def alpha(self):
        """Thermal diffusivity of the humid air, [m^2/s]."""
        return self._alpha

    @property
    def cp(self):
        """Specific heat at constant pressure per unit humid air, [J/kg K]."""
        return self._cp

    @property
    def d12(self):
        """Binary pecies diffusivity for water vapor and dry air, [m^2/s]."""
        return self._d12

    @property
    def k(self):
        """Thermal Conductivity of the humid air, [W/m K]."""
        return self._k

    @property
    def rho(self):
        """Specific mass of the humid air, [kg humid air/m^3]."""
        return self._rho

    # ----------------------------------------------------------------------- #
    # Private methods for evaluation
    # ----------------------------------------------------------------------- #
    def _eval_alpha(self):
        self._alpha = self._k / (self._rho*self._cp)

    def _eval_cp(self, p, t, x):
        self._cp = hap.HAPropsSI('cp_ha', 'P', p, 'T', t, 'Y', x)

    def _eval_d12(self, p, t, ref='Mills'):
        """
        Two references are available: 'Mills' and 'Marrero'.

        See Appendix of 'Mass Transfer' by Mills and Coimbra for more info.
        """
        self._d12 = {
            'Mills': lambda t, p: 1.97e-5 * (1/p) * pow(t/256, 1.685),
            'Marrero': lambda t, p: 1.87e-10 * pow(t, 2.072) / p
            }[ref](t, p/101325)

    def _eval_k(self, p, t, x):
        self._k = hap.HAPropsSI('k', 'P', p, 'T', t, 'Y', x)

    def _eval_rho(self, p, t, x):
        spec_vol_ha = hap.HAPropsSI('Vha', 'P', p, 'T', t, 'Y', x)
        self._rho = 1/spec_vol_ha

    # ----------------------------------------------------------------------- #
    # Public methods for evaluation
    # ----------------------------------------------------------------------- #
    def eval(self, p, t, x, ref='Mills'):
        """
        Use `p`, `t`, and `x` to evaluate thermophysical properties.

        Uses reference pressure `p`, reference temperature `t`, and reference
        mole fraction `x` to update all of the thermophysical properties. A
        reference `ref` is also required when calculating `d12`, which defaults
        to 'Mills'. Try `>>> help(self._eval_d12)` for more help regarding
        options for this input.

        Args:
            p (`float` or `int`): Reference pressure in Pa.
            t (`float` or `int`): Reference temperature in K.
            x (`float`): Reference water vapor mole fraction with no units.
            ref (`str`, optional): Reference for calculating the binary species
                diffusivity. Defaults to 'Mills'.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self._eval_rho(p, t, x)
            self._eval_k(p, t, x)
            self._eval_cp(p, t, x)

            self._eval_alpha()
            self._eval_d12(p, t, ref=ref)
            return True
        except:
            return False
