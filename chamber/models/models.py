"""Docstring."""
import pandas as pd

from chamber.models import film
from chamber.models import props


class Spalding:
    """Init."""
    def __init__(self, p, t_e, t_dp, ref, rule):
        # Surface temperature guess defaults to `None`.
        self._t_s_guess = None

        # Keep a 'guide' of how to calculate film props.
        self._film_guide = pd.Series(dict(ref=ref, rule=rule))

        # Set the _exp_state, which should not be confused with the
        # environmental or `e`-state with attributes such as m_1e and h_e.
        self._exp_state = pd.Series(dict(p=p, t_e=t_e, t_dp=t_dp))

    @property
    def t_s_guess(self):
        """Guess at the surface temperature in K."""
        return self._t_s_guess
