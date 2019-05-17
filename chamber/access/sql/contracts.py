"""Module including data contracts for an experiment."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List


# ----------------------------------------------------------------------------
# Chamber DTOs

@dataclass(frozen=True)
class PoolSpec:
    """Chamber pool specification."""

    inner_diameter: Decimal
    outer_diameter: Decimal
    height: Decimal
    material: str
    mass: Decimal


@dataclass(frozen=True)
class SettingSpec:
    """Chamber setting specification."""

    duty: Decimal
    pressure: int
    temperature: Decimal
    time_step: Decimal


@dataclass(frozen=True)
class ExperimentSpec:
    """Chamber experiment specifications."""

    author: str
    datetime: datetime
    description: str
    pool_id: int
    setting_id: int


@dataclass(frozen=True)
class TemperatureSpec:
    """Chamber temperature specification."""

    thermocouple_num: int
    temperature: Decimal
    idx: int


@dataclass(frozen=True)
class ObservationSpec:
    """Chamber observation specification."""

    cap_man_ok: bool
    dew_point: Decimal
    idx: int
    mass: Decimal
    optidew_ok: bool
    pow_out: Decimal
    pow_ref: Decimal
    pressure: int
    temperatures: List[TemperatureSpec]


@dataclass(frozen=True)
class DataSpec:
    """Chamber data specification."""

    pool_id: int
    setting: SettingSpec
    experiment: ExperimentSpec
    observations: List[ObservationSpec]
