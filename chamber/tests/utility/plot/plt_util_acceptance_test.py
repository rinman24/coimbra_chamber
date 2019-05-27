"""Unit test suite for plot utility."""

import dataclasses

import dacite
import pytest

from chamber.utility.plot.contracts import (
    Layout,
    Observations,
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
    data = dict(values=list(range(10)), sigma=[0]*10)
    return dacite.from_dict(Observations, data)


@pytest.fixture(scope='function')
def position_1():
    """Create position of car 1."""
    data = dict(
        values=[x**2 for x in range(10)],
        sigma=[0]*10,
        label='car 1')
    return dacite.from_dict(Observations, data)


@pytest.fixture(scope='function')
def position_2():
    """Create position of car 2."""
    data = dict(
        values=[x**2.1 for x in range(10)],
        sigma=[0]*10,
        label='car 2')
    return dacite.from_dict(Observations, data)


@pytest.fixture(scope='function')
def one_car_position_plot(time, position_1):
    """Create a one car position in time plot."""
    data = dict(
        abscissae=[time],
        ordinates=[position_1],
        title='Position with time of car 1.',
        x_label='time',
        y_label='position',
        axis=0)
    return dacite.from_dict(Plot, data)


@pytest.fixture(scope='function')
def two_car_position_plot(time, position_1, position_2):
    """Create a two car position in time plot."""
    data = dict(
        abscissae=[time, time],
        ordinates=[position_1, position_2],
        title='Position with time of car 1 and 2.',
        x_label='time',
        y_label='position',
        axis=0)
    return dacite.from_dict(Plot, data)


@pytest.fixture(scope='function')
def velocity_1():
    """Create velocity of car 1."""
    data = dict(
        values=[2 * x for x in range(10)],
        sigma=[5]*10,
        label='car 1')
    return dacite.from_dict(Observations, data)


@pytest.fixture(scope='function')
def velocity_2():
    """Create velocity of car 1."""
    data = dict(
        values=[2.1 * x for x in range(10)],
        sigma=[5]*10,
        label='car 2')
    return dacite.from_dict(Observations, data)


@pytest.fixture(scope='function')
def two_car_velocity_plot(time, velocity_1, velocity_2):
    """Create a two car velocity in time plot."""
    data = dict(
        abscissae=[time, time],
        ordinates=[velocity_1, velocity_2],
        title='Velocity with time of car 1 and 2.',
        x_label='time',
        y_label='velocity',
        axis=0)
    return dacite.from_dict(Plot, data)


# ----------------------------------------------------------------------------
# Acceptance tests


@pytest.mark.parametrize('style', ['seaborn-darkgrid', '', 'dark_background'])
def test_can_set_global_style(style, plt_util, one_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(plots=[one_car_position_plot], style=style)
    layout = dacite.from_dict(Layout, data)

    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_can_plot_ordinate_errorbars(
        plt_util, position_1, one_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Adjust the uncertainty on the ordindate
    changes = dict(sigma=[5]*10)
    ordinates = dataclasses.replace(position_1, **changes)
    changes = dict(ordinates=[ordinates])
    plot = dataclasses.replace(one_car_position_plot, **changes)

    # Create the layout
    data = dict(plots=[plot])
    layout = dacite.from_dict(Layout, data)
    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_can_plot_abscissa_errorbars(
        plt_util, time, one_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Adjust the uncertainty on the abscissa
    changes = dict(sigma=[0.5]*10)
    abscissae = dataclasses.replace(time, **changes)
    changes = dict(abscissae=[abscissae])
    plot = dataclasses.replace(one_car_position_plot, **changes)

    # Create the layout
    data = dict(plots=[plot])
    layout = dacite.from_dict(Layout, data)
    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_can_plot_abscissa_and_ordinate_errorbars(
        plt_util, time, position_1, one_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # Adjust the uncertainty on the abscissa and the ordindate
    changes = dict(sigma=[0.5]*10)
    abscissae = dataclasses.replace(time, **changes)

    changes = dict(sigma=[5]*10)
    ordinates = dataclasses.replace(position_1, **changes)

    changes = dict(abscissae=[abscissae], ordinates=[ordinates])
    plot = dataclasses.replace(one_car_position_plot, **changes)

    # Create the layout
    data = dict(plots=[plot])
    layout = dacite.from_dict(Layout, data)

    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_can_plot_multiple_plots_on_one_axis(plt_util, two_car_position_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(plots=[two_car_position_plot])
    layout = dacite.from_dict(Layout, data)

    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_layout_length_2(
        plt_util, two_car_position_plot, two_car_velocity_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(
        plots=[two_car_position_plot, two_car_velocity_plot],
        style='seaborn-darkgrid')
    layout = dacite.from_dict(Layout, data)

    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_layout_length_3(
        plt_util, two_car_position_plot, two_car_velocity_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(
        plots=[two_car_position_plot, two_car_velocity_plot,
               two_car_position_plot],
        style='seaborn-deep')
    layout = dacite.from_dict(Layout, data)

    # Act --------------------------------------------------------------------
    plt_util.plot(layout)


def test_layout_length_4(
    plt_util, two_car_position_plot, two_car_velocity_plot):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(
        plots=[two_car_position_plot, two_car_velocity_plot,
               two_car_position_plot, two_car_velocity_plot],
        style='grayscale')
    layout = dacite.from_dict(Layout, data)

    # Act --------------------------------------------------------------------
    plt_util.plot(layout)
