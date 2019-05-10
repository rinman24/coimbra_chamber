"""Module including data contracts for an experiment."""

from dataclasses import dataclass
from decimal import Decimal


# ----------------------------------------------------------------------------
# Example

@dataclass(frozen=True)
class PoolSpecs:
    """Experimental pool specification."""

    inner_diameter: Decimal
    outer_diameter: Decimal
    height: Decimal
    material: str
    mass: Decimal
