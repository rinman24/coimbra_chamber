"""Docstring."""
from math import cos, pi, sin

from chamber.tools import tools


class TestTools(object):
    """Unit testing of tools.py."""

    def test_meshgrid(self):
        """Check that the meshgrid is generated properly if points
        are passed to it."""
        i_points, j_points = [0, 1, 2], [0, 1]
        x_grid, y_grid = tools.meshgrid(i_points, j_points)
        assert x_grid == [[0, 0], [1, 1], [2, 2]]
        assert y_grid == [[0, 1], [0, 1], [0, 1]]

    def test_meshgrid_empty(self):
        """Check that the meshgrid is generated properly if empty
        iterables are passed to it."""
        x_grid, y_grid = tools.meshgrid([], [])
        assert not x_grid
        assert not y_grid

    def test_meshgrid_pol2cart(self):
        """Check that the polar meshgrid can be converted to Cartesian."""
        r_points, phi_points = [0, 1, 2], [pi/4, 3*pi/4, 3*pi/2]
        r_grid, phi_grid = tools.meshgrid(r_points, phi_points)
        x_grid, y_grid = tools.meshgrid_pol2cart(r_grid, phi_grid)
        assert x_grid[0] == [0, 0, 0]
        assert y_grid[0] == [0, 0, 0]
        assert x_grid[1] == [cos(pi/4), cos(3*pi/4), cos(3*pi/2)]
        assert y_grid[1] == [sin(pi/4), sin(3*pi/4), sin(3*pi/2)]
        assert x_grid[2] == [2*i for i in x_grid[1]]
        assert y_grid[2] == [2*j for j in y_grid[1]]
