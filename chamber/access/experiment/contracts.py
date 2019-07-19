"""Data contracts for experiment access."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List


# ----------------------------------------------------------------------------
# Experiment access DTOs

@dataclass(frozen=True)
class TubeSpec:
    """Tube specification."""

    inner_diameter: Decimal
    outer_diameter: Decimal
    height: Decimal
    material: str
    mass: Decimal


@dataclass(frozen=True)
class SettingSpec:
    """Setting specification."""

    duty: Decimal
    pressure: int
    temperature: Decimal
    time_step: Decimal


@dataclass(frozen=True)
class ExperimentSpec:
    """Experiment specification."""

    author: str
    datetime: datetime
    description: str
    tube_id: int


@dataclass(frozen=True)
class TemperatureSpec:
    """Temperature specification."""

    thermocouple_num: int
    temperature: Decimal
    idx: int


@dataclass(frozen=True)
class ObservationSpec:
    """Observation specification."""

    cap_man_ok: bool
    dew_point: Decimal
    idx: int
    mass: Decimal
    optidew_ok: bool
    pow_out: Decimal
    pow_ref: Decimal
    pressure: int
    temperatures: List[TemperatureSpec]
    surface_temp: Decimal
    ic_temp: Decimal


@dataclass(frozen=True)
class DataSpec:
    """Data specification."""

    setting: SettingSpec
    experiment: ExperimentSpec
    observations: List[ObservationSpec]


@dataclass(frozen=True)
class FitSpec:
    """Regression fit results."""

    a: float
    sig_a: float
    b: float
    sig_b: float
    r2: float
    q: float
    chi2: float
    nu_chi: int
    exp_id: int
    idx: int
    mddp: float
    x1s: float
    x1e: float
    x1: float
    m1s: float
    m1e: float
    m1: float
    rhos: float
    rhoe: float
    rho: float
    Bm1: float
    T: float
    D12: float
    hfg: float
    hu: float
    hs: float
    cpv: float
    he: float
    cpl: float
    hT: float
    qcu: float
    Ebe: float
    Ebs: float
    qrs: float
    kv: float
    alpha: float
    Bh: float
    M: float
    gamma1: float
    beta: float
    Deltam: float
    DeltaT: float
    mu: float
    nu: float
