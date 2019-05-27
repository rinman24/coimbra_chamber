"""Unit test suite for plot utility."""

import dataclasses

import dacite
import pytest

from chamber.utility.plot.contracts import (
    Coordinates,
    Layout,
    Plot)
from chamber.utility.plot.service import PlotUtility


# ----------------------------------------------------------------------------
# Fixtures

@pytest.fixture(scope='module')
def plt_util():
    """Create a module level instance of the plotting utility."""
    return PlotUtility()


@pytest.fixture(scope='function')
def time():
    """Create a common time axis."""
    data = dict(
        values=list(range(10)),
        sigma=[0]*10,
        axis='time',
        label='')
    return dacite.from_dict(Coordinates, data)


@pytest.fixture(scope='function')
def position_1():
    """Create a position of car 1."""
    data = dict(
        values=list(range(10)),
        sigma=[0]*10,
        axis='position',
        label='car 1')
    return dacite.from_dict(Coordinates, data)


@pytest.fixture(scope='function')
def one_car_position_plot(time, position_1):
    """Create a one car position in time plot."""
    data = dict(
        abscissae=time,
        ordinates=position_1,
        title='Position with time',
        axis=0)
    return dacite.from_dict(Plot, data)


# ----------------------------------------------------------------------------
# Acceptance tests


@pytest.mark.parametrize('style', ['seaborn-darkgrid', '', 'dark_background'])
def test_can_set_global_style(style, plt_util, one_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(
        rows=1, columns=1, plots=[one_car_position_plot],
        style=style)
    layout = dacite.from_dict(Layout, data)

    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_can_plot_ordinate_errorbars(
        plt_util, position_1, one_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Adjust the uncertainty on the ordindate
    changes = dict(sigma=[5]*10)
    ordinates = dataclasses.replace(position_1, **changes)
    changes = dict(ordinates=ordinates)
    plot = dataclasses.replace(one_car_position_plot, **changes)

    # Create the layout
    data = dict(rows=1, columns=1, plots=[plot])
    layout = dacite.from_dict(Layout, data)
    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_can_plot_abscissa_errorbars(
        plt_util, time, one_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Adjust the uncertainty on the abscissa
    changes = dict(sigma=[1]*10)
    abscissae = dataclasses.replace(time, **changes)
    changes = dict(abscissae=abscissae)
    plot = dataclasses.replace(one_car_position_plot, **changes)

    # Create the layout
    data = dict(rows=1, columns=1, plots=[plot])
    layout = dacite.from_dict(Layout, data)
    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_can_plot_abscissa_and_ordinate_errorbars(
        plt_util, time, position_1, one_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Adjust the uncertainty on the abscissa and the ordindate
    changes = dict(sigma=[1]*10)
    abscissae = dataclasses.replace(time, **changes)

    changes = dict(sigma=[5]*10)
    ordinates = dataclasses.replace(position_1, **changes)

    changes = dict(abscissae=abscissae, ordinates=ordinates)
    plot = dataclasses.replace(one_car_position_plot, **changes)

    # Create the layout
    data = dict(rows=1, columns=1, plots=[plot])
    layout = dacite.from_dict(Layout, data)

    # Act --------------------------------------------------------------------
    plt_util.plot(layout)
