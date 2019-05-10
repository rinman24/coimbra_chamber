"""Module including data contracts for an experiment."""

from dataclasses import dataclass
from decimal import Decimal


# ----------------------------------------------------------------------------
# Experimental DTOs

@dataclass(frozen=True)
class PoolSpec:
    """Experimental pool specification."""

    inner_diameter: Decimal
    outer_diameter: Decimal
    height: Decimal
    material: str
    mass: Decimal


@dataclass(frozen=True)
class SettingSpec:
    """Experimental settings specification."""

    duty: Decimal
    pressure: int
    temperature: Decimal
    time_step: Decimal
