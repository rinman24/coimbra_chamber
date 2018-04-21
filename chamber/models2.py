"""
This module contains several classes required for modeling simultaneous
heat and mass transfer problems from a Stefan tube.

Classes:
    ExperimentalState: Custom read-only datastore for experimental state.
    FilmProperties: Thermophysical properties as a function of reference state.
    ReferenceFilm: Relevant properties based on a guess at the surface
        temperature.
"""

import CoolProp.HumidAirProp as hap
import scipy.optimize as opt

RULES = ['one-half', 'one-third']
REFERENCES = ['Mills', 'Marrero']


class ExperimentalState:
    """
    Use `p`, `tch`, `tdp`, and `tm` store experimental state.

    A custom read-only data store for experimental state. An experimental
    state is completely defined by a pressure `p` in Pa, a chamber wall
    temperature `tch` in K, a dew point temperature `tdp` in K, and a vapor
    mixture temperature `tm` in K.

    An experimental state is required when calling the `ExperimentalState`
    constructor. All instance variable are read-only. However, a non-public
    method `_change_state` is provided for insistent users who would like to
    change the experimental state. However, this is not recommended.

    Instance Variables:
        p (`float` or `int`): Experimental chamber pressure, [Pa].
        tch (`float` or `int`): Experimental chamber wall temperature, [K].
        tdp (`float` or `int`): Experimental dew point temperature, [K].
        tm (`float` or `int`): Experimental vapor mixture temperature, [K].
    """
    def __init__(self, p, tch, tdp, tm):
        """
        Return a new instance of `ExperimentalState` with corresponding
        instance variables (state).

        Args:
            p (`float` or `int`): Experimental chamber pressure, [Pa].
            tch (`float` or `int`): Experimental chamber wall temperature, [K].
            tdp (`float` or `int`): Experimental dew point temperature, [K].
            tm (`float` or `int`): Experimental vapor mixture temperature, [K].

        Example:
            It is often convenient to pass a dictionary to the constructor:

            >>> exp_state_dict = dict(p=100e3, tch=290, tdp=280, tm=290)
            >>> exp_state = models2.ExperimentalState(**exp_state_dict)
        """
        self._p = p
        self._tch = tch
        self._tdp = tdp
        self._tm = tm

    # ----------------------------------------------------------------------- #
    # Instance Variables
    # ----------------------------------------------------------------------- #
    @property
    def p(self):
        """Experimental chamber pressure, [Pa]."""
        return self._p

    @property
    def tch(self):
        """Experimental chamber wall temperature, [K]."""
        return self._tch

    @property
    def tdp(self):
        """Experimental dew point temperature, [K]."""
        return self._tdp

    @property
    def tm(self):
        """Experimental vapor mixture temperature, [K]."""
        return self._tm

    # ----------------------------------------------------------------------- #
    # Internal Methods
    # ----------------------------------------------------------------------- #
    def _change_state(self, p, tch, tdp, tm):
        """
        Use `p`, `tch`, `tdp`, and `tm` to update the experimental state.

        Args:
            p (`float` or `int`): Experimental chamber pressure, [Pa].
            tch (`float` or `int`): Experimental chamber wall temperature, [K].
            tdp (`float` or `int`): Experimental dew point temperature, [K].
            tm (`float` or `int`): Experimental vapor mixture temperature, [K].

        Returns:
            True if successful, False otherwise.

        Example:
            It is often convenient to pass a dictionary this method:

            >>> # Create an instance
            >>> ...
            >>> exp_state_dict = dict(p=100e3, tch=290, tdp=280, tm=290)
            >>> exp_state = models2.ExperimentalState(**exp_state_dict)
            >>> # Update the experimental state
            >>> ...
            >>> exp_state_dict['p'] = 80000
            >>> exp_state.update(**exp_state_dict)
        """
        try:
            self._p = p
            self._tch = tch
            self._tdp = tdp
            self._tm = tm
            return True
        except:
            return False


class FilmProperties:
    """
    Logic and data store for thermophysical film properties.

    When `FilmProperties` constructor is called all instance variables are set
    to `None` except `ref` which defaults to 'Mills'. Film properties are
    evaluated (and updated) using the `eval` method. The instance variable
    `ref` is updated using the `update_ref` method.

    Note: Film properties are divided into two types: primary and secondary.
        Primary properties typically cannot be decomposed into subsequent
        primary properties. Secondary properties, on the other hand are
        composed of primary properties. For example, thermal conductivity `k`,
        specific heat at constant pressure per kg humid air `cp`, and specific
        mass `rho` would be considered primary properties. On the other hand,
        the mixture thermal diffusivity `alpha` = `k` / (`rho`*`cp`) would be
        considered a secondary property since it is composed or three primary
        properties.

    Public Methods:
        eval: Evaluate thermophysical properties based on `p`, `t`, and `x`.
        change_ref: Change reference used to calculate binary species
            diffusivity, `d12`.

    Instance Variables:
        alpha (`float`): Thermal diffusivity of the humid air, [m^2/s].
        cp (`float`): Specific heat at constant pressure per unit humid
            air, [J/kg K].
        d12 (`float`): Binary pecies diffusivity for water vapor and dry
            air, [m^2/s].
        k (`float`): Thermal conductivity of the humid air, [W/m K].
        rho (`float`): Specific mass of the humid air, [kg humid air/m^3].
    """

    def __init__(self, ref='Mills'):
        """
        Return a new instance of `FilmProperties` with all attributes set to
        `None`.
        """
        self._ref = ref

        self._cp = None
        self._k = None
        self._rho = None

        self._alpha = None
        self._d12 = None

    # ----------------------------------------------------------------------- #
    # Public Methods
    # ----------------------------------------------------------------------- #
    def change_ref(self, ref):
        """
        Change `self.ref` which is used to calculate the binary species
        diffusivity `d12`.

        Args:
            ref (`str`): Rule used to calculate `d12`.

        Returns:
            True if successful, raises error otherwise.

        Raises:
            ValueError: If `ref` is ``<class 'str'>`` but not valid ref.
            TypeError: If `ref` is not ``<class 'str'>``.
        """
        if ref in REFERENCES:
            self._ref = ref
            return True
        elif isinstance(ref, str):
            raise ValueError('`ref` must be in {0}.'.format(REFERENCES))
        else:
            raise TypeError(
                "`ref` must be <class 'str'> not {0}.".format(type(ref))
                )

    def eval(self, p, t, x):
        """
        Use `p`, `t`, and `x` to evaluate thermophysical properties.

        Uses reference pressure `p`, reference temperature `t`, and reference
        mole fraction `x` to update all of the thermophysical properties.

        Args:
            p (`float` or `int`): Reference pressure in Pa.
            t (`float` or `int`): Reference temperature in K.
            x (`float`): Reference water vapor mole fraction with no units.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self._eval_rho(p, t, x)
            self._eval_k(p, t, x)
            self._eval_cp(p, t, x)

            self._eval_alpha()
            self._eval_d12(p, t)
            return True
        except:
            return False

    # ----------------------------------------------------------------------- #
    # Instance Variables
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
    def ref(self):
        """Rule for calculating the binary species diffusivity."""
        return self._ref

    @property
    def rho(self):
        """Specific mass of the humid air, [kg humid air/m^3]."""
        return self._rho

    # ----------------------------------------------------------------------- #
    # Internal Methods
    # ----------------------------------------------------------------------- #
    def _eval_alpha(self):
        self._alpha = self._k / (self._rho*self._cp)

    def _eval_cp(self, p, t, x):
        self._cp = hap.HAPropsSI('cp_ha', 'P', p, 'T', t, 'Y', x)

    def _eval_d12(self, p, t):
        self._d12 = {
            'Mills': lambda t, p: 1.97e-5 * (1/p) * pow(t/256, 1.685),
            'Marrero': lambda t, p: 1.87e-10 * pow(t, 2.072) / p
            }[self.ref](t, p/101325)

    def _eval_k(self, p, t, x):
        self._k = hap.HAPropsSI('k', 'P', p, 'T', t, 'Y', x)

    def _eval_rho(self, p, t, x):
        spec_vol_ha = hap.HAPropsSI('Vha', 'P', p, 'T', t, 'Y', x)
        self._rho = 1/spec_vol_ha


class ReferenceFilm:
    """
    Logic and data store for thermophysical film properties based on a guess
    at the surface temperature `ts`.

    Each instance of `ReferenceFilm` is composed of two other objects: an
    instance of `ExperimentalState` and an instance of `FilmProperties`.
    Each instance of `ReferenceFilm` also contains a `film_rule` attribute,
    which defaults to 'one-third'.

    When the `ReferenceFilm` constructor is called all instance variables are
    set to `None`. In order to populate `ts_guess` and other instance
    variables a call to the `update_film` method is required.

    Public Methods:
        change_film_rule: Update the film rule used to calculated the
            reference state.
        update_film: Update the guess at the surface temperature and related
            film properties.

    Instance Variables:
        alpha (`float`): Film thermal diffusivity, [m^2/s].
        cp ('float'): Film specific heat at constant pressure per unit humid
            air, [J/kg K].
        d12 (`float`): Film binary pecies diffusivity for water vapor and dry
            air, [m^2/s].
        film_rule (`str`): Rule for calculating the reference state.
        k (`float`): Film thermal conductivity of the humid air, [W/m K].
        p (`float` or `int`): Film pressure, [Pa].
        rho (`float`): Film specific mass of the humid air, [kg humid air/m^3].
        t (`float` or `int`): Reference film temperature, [K].
        ts_guess (`float` or `int`): Guess at surface temperature, [K].
        x (`float`): Film reference film mole fraction of water vapor with no
            units.
    """
    def __init__(self, exp_state, film_rule='one-third', ref='Mills'):
        self._ts_guess = None
        self._ExpState = ExperimentalState(**exp_state)
        self._FilmProps = FilmProperties(ref=ref)
        self._film_rule = film_rule

        self._t = None
        self._x = None
        self._xe = None
        self._xs = None

    # ----------------------------------------------------------------------- #
    # Public Methods
    # ----------------------------------------------------------------------- #
    def change_film_rule(self, film_rule):
        """
        Update film rule used to calculate reference state attributes.

        Args:
            film_rule (`str`): Film rule. Should be either 'one-third' or
                'one-half'.

        Returns:
            True if successful, raises error otherwise.

        Raises:
            ValueError: If `film_rule` is ``<class 'str'>`` but not valid
                film_rule.
            TypeError: If `film_rule` is not ``<class 'str'>``.
        """
        if film_rule in RULES:
            self._film_rule = film_rule
            return True
        elif isinstance(film_rule, str):
            err_msg = "'{0}' is not a valid `film_rule`."
            raise ValueError(err_msg.format(film_rule))
        else:
            err_msg = "`film_rule` must be <class 'str'> not {0}."
            raise TypeError(err_msg.format(type(film_rule)))

    def update_film(self, ts_guess):
        """
        Update the guess at the surface temperature in [K].

        Args:
            ts_guess (`int` or `float`): New guess at the surface temperature
                in [K].

        Returns:
            True if successful, raises error otherwise.

        Raises:
            TypeError: if `ts_guess` is not ``<class 'int'>`` or
            ``<class 'float'>``.
        """
        if isinstance(ts_guess, int) or isinstance(ts_guess, float):
            self._ts_guess = ts_guess  # Update guess
            self._eval_state()  # Eval new film temp and mole frac
            self._FilmProps.eval(  # Eval props
                p=self.p, t=self.t, x=self.x
                )
            return True
        else:
            raise TypeError(
                "`ts_guess` must be numeric not {0}.".format(type(ts_guess))
                )

    # ----------------------------------------------------------------------- #
    # Instance Variables
    # ----------------------------------------------------------------------- #
    @property
    def alpha(self):
        """Film thermal diffusivity, [m^2/s]."""
        return self._FilmProps.alpha

    @property
    def cp(self):
        """
        Film specific heat at constant pressure per unit humid air, [J/kg K].
        """
        return self._FilmProps.cp

    @property
    def d12(self):
        """
        Film binary pecies diffusivity for water vapor and dry air, [m^2/s].
        """
        return self._FilmProps.d12

    @property
    def film_rule(self):
        """Rule for calculating the reference state."""
        return self._film_rule

    @property
    def k(self):
        """Film thermal conductivity of the humid air, [W/m K]."""
        return self._FilmProps.k

    @property
    def p(self):
        """Film pressure, [Pa]."""
        if self._ts_guess:
            return self._ExpState.p
        else:
            return None

    @property
    def ref(self):
        """Rule for calculating the binary species diffusivity."""
        return self._FilmProps.ref

    @property
    def rho(self):
        """Film specific mass of the humid air, [kg humid air/m^3]."""
        return self._FilmProps.rho

    @property
    def t(self):
        """Reference film temperature, [K]."""
        return self._t

    @property
    def ts_guess(self):
        """Guess at surface temperature, [K]."""
        return self._ts_guess

    @property
    def x(self):
        """Film reference film mole fraction of water vapor with no units."""
        return self._x

    # ----------------------------------------------------------------------- #
    # Internal Methods
    # ----------------------------------------------------------------------- #
    def _eval_state(self):
        self._p = self._ExpState.p
        self._t = self._use_film_rule(self._ExpState.tm, self.ts_guess)
        self._eval_xe()
        self._eval_xs()
        self._x = self._use_film_rule(self._xe, self._xs)

    def _eval_xe(self):
        self._xe = hap.HAPropsSI('Y',
                                 'T', self.t,
                                 'P', self.p,
                                 'Tdp', self._ExpState.tdp)

    def _eval_xs(self):
        self._xs = hap.HAPropsSI('Y',
                                 'T', self.ts_guess,
                                 'P', self.p,
                                 'RH', 1.0)

    def _use_film_rule(self, e_state, s_state):
        return {
            'one-half': lambda e, s: (e + s) / 2,
            'one-third': lambda e, s: s + (e - s) / 3
            }[self.film_rule](e_state, s_state)


class Model:
    """Model base class."""

    def __init__(self, exp_state, film_rule='one-third', ref='Mills'):
        """Return """

        self._RefFilm = ReferenceFilm(
            exp_state, ref=ref, film_rule=film_rule
            )
