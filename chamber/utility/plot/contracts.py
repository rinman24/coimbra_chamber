"""Data contracts for plot utility."""

from dataclasses import dataclass
from datetime import datetime

from typing import List


# ----------------------------------------------------------------------------
# Plot utility DTOs


@dataclass(frozen=True)
class Coordinates:
    """Coordinates to plot on a single axis."""

    values: List  # List of coordinate values
    sigma: List  # Error bars not plotted if sum == 0
    label: str = '' # Should be an empty string for abscissae


@dataclass(frozen=True)
class Plot:
    """Two dimensional plot."""

    abscissae: List[Coordinates]  # Independent coordinates
    ordinates: List[Coordinates]  # Dependent coordinates
    title: str  # Title for the plot
    x_label: str
    y_label: str
    axis: int  # Location of the plot


@dataclass(frozen=True)
class Layout:
    """Layout of a figure."""

    rows: int  # Number of rows for the subplots
    columns: int  # Number of columns for the subplots
    plots: List[Plot]  # List of plots to display
    style: str = ''  # valid pyplot.style
