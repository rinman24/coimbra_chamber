"""Data contracts for plot utility."""

from dataclasses import dataclass, field
from datetime import datetime

from typing import List


# ----------------------------------------------------------------------------
# Plot utility DTOs


@dataclass(frozen=True)
class DataSeries:
    """DataSeries to plot on a single axis."""

    values: List  # List of observation values
    sigma: List = field(default_factory=list)  # Error bars not plotted if sum == 0
    label: str = ''  # Should be an empty string for abscissae


@dataclass(frozen=True)
class Axis:
    """Single axis for a two dimensional plot."""

    data: List[DataSeries]  # Data to plot on the axis
    y_label: str  # y-label for the axis
    error_type: str = ''  # {discrete, continuous}


@dataclass(frozen=True)
class Plot:
    """Two dimensional plot."""

    abscissa: DataSeries  # Independent data series
    axes: List[Axis]  # Axes for dependent data series
    x_label: str  # x-label for the plot
    legend: bool = True  # If True, show legend; else, do not


@dataclass(frozen=True)
class Layout:
    """Layout of a figure."""

    plots: List[Plot]  # List of plots to display (each on its own axis)
    style: str = ''  # valid pyplot.style
