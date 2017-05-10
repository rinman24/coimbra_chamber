"""Docstring."""

import chamber.tools as tools

class TestTools(object):
    """Unit testing of tools.py."""

    def test_meshgrid_custom(self):
        """Check that the meshgrid is generated properly if points are passed to it."""
        x_grid, y_grid = tools.meshgrid([10.1, 20.1, 30.1, 40.1], [8.9, 16.9])
        assert x_grid == [[10.1, 20.1, 30.1, 40.1], [10.1, 20.1, 30.1, 40.1]]
        assert y_grid == [[8.9, 8.9, 8.9, 8.9], [16.9, 16.9, 16.9, 16.9]]

    def test_meshgrid_empty(self):
        """Check that the meshgrid is generated properly if empty iterables are passed to it."""
        x_grid, y_grid = tools.meshgrid([], [])
        assert not x_grid
        assert not y_grid
