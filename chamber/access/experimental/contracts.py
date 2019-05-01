"""Module including data contracts for an experiment."""

from dataclasses import dataclass
from numbers import Real
from typing import List


# ----------------------------------------------------------------------------
# Example

@dataclass(frozen=True)
class MyDataClass:
    """Description of my dataclass."""

    attr_1: str
    attr_2: float
    attr_3: List[str]
    attr_4: int
