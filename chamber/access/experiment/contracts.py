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
    sig_mddp: float
    x1s: float
    sig_x1s: float
    x1e: float
    sig_x1e: float
    x1: float
    sig_x1: float
    m1s: float
    sig_m1s: float
    m1e: float
    sig_m1e: float
    m1: float
    sig_m1: float
    rhos: float
    sig_rhos: float
    rhoe: float
    sig_rhoe: float
    rho: float
    sig_rho: float
    Bm1: float
    sig_Bm1: float
    T: float
    sig_T: float
    D12: float
    sig_D12: float
    hfg: float
    sig_hfg: float
    hu: float
    sig_hu: float
    hs: float
    sig_hs: float
    cpv: float
    sig_cpv: float
    he: float
    sig_he: float
    cpl: float
    sig_cpl: float
    hT: float
    sig_hT: float
    qcu: float
    sig_qcu: float
    Ebe: float
    sig_Ebe: float
    Ebs: float
    sig_Ebs: float
    qrs: float
    sig_qrs: float
    kv: float
    sig_kv: float
    alpha: float
    sig_alpha: float
    Bh: float
    sig_Bh: float
    M: float
    sig_M: float
    gamma1: float
    sig_gamma1: float
    beta: float
    sig_beta: float
    Delta_m: float
    sig_Delta_m: float
    Delta_T: float
    sig_Delta_T: float
    mu: float
    sig_mu: float
    nu: float
    sig_nu: float
