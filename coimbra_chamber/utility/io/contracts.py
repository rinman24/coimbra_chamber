"""Data contracts for io utility."""

from dataclasses import dataclass, field
from datetime import datetime

from typing import List


# ----------------------------------------------------------------------------
# IO utility DTOs


@dataclass(frozen=True)
class Prompt:
    """Prompt the user for input."""

    messages: List[str]  # Each string will be passed as prompt
