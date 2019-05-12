"""Module including data contracts for an experiment."""

from dataclasses import dataclass
from datetime import datetime
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
    """Experimental setting specification."""

    duty: Decimal
    pressure: int
    temperature: Decimal
    time_step: Decimal


@dataclass(frozen=True)
class ExperimentSpec:
    """Experimental experiment specifications."""

    author: str
    datetime: datetime
    description: str
    pool_id: int
    setting_id: int
