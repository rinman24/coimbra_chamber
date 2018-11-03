"""Docstring."""
import numpy as np
from math import cos, sin
import sys

from matplotlib.legend_handler import HandlerLine2D
import matplotlib.pyplot as plt
from scipy import stats
from tabulate import tabulate

from chamber.data import sqldb


def meshgrid(i_points, j_points):
    """Use two iterables to make a grid, similar to numpy.meshgrid.

    Description: Given two iterables, return two lists of lists where i_grid
    has rows of i_points and j_grid has columns of j_points. The coordinate
    system doesn't matter here, which is why i and j were used rather than
    x and y. This could just as well be a polar grid in r and phi.

    Positional arguments:
    i_points -- iterable of i points
    j_points -- iterable of j points
    """
    rows, cols = len(i_points), len(j_points)
    i_grid = [[i]*cols for i in i_points]
    j_grid = [j_points[:] for __ in range(rows)]
    return i_grid, j_grid


def meshgrid_pol2cart(r_grid, phi_grid):
    """Convert r_grid and phi_grid to x_grid and y_grid.

    Description: Given two iterables of iterables (grids or matrices)
    representing polar coordinates, convert them to x_grid and y_grid for
    plotting functions that require Cartesian coordinates as inputs; e.g.
    matplotlib.pyplot.plot_surface.

    Positional arguments:
    r_grid -- iterable of iterables for r points
    phi_grid -- iterable of iterables for phi points
    """
    r_points = [col[0] for col in r_grid]
    phi_points = phi_grid[0][:]
    for i, r in enumerate(r_points):
        for j, phi in enumerate(phi_points):
            r_grid[i][j] = r*cos(phi)
            phi_grid[i][j] = r*sin(phi)
    return r_grid, phi_grid
