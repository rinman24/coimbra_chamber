"""Data contracts for plot utility."""

from dataclasses import dataclass
from datetime import datetime

from typing import List


# ----------------------------------------------------------------------------
# Plot utility DTOs


@dataclass(frozen=True)
class DataSeries:
    """DataSeries to plot on a single axis."""

    values: List  # List of observation values
    sigma: List  # Error bars not plotted if sum == 0
    label: str = ''  # Should be an empty string for abscissae


@dataclass(frozen=True)
class Plot:
    """Two dimensional plot."""

    abscissae: List[DataSeries]  # Independent data series
    ordinates: List[DataSeries]  # Dependent data series
    title: str  # Title for the plot
    x_label: str  # x-label for the plot
    y_label: str  # y-label for the plot


@dataclass(frozen=True)
class Layout:
    """Layout of a figure."""

    plots: List[Plot]  # List of plots to display (each on its own axis)
    style: str = ''  # valid pyplot.style
