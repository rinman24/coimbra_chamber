"""Docstring."""

def meshgrid(x_points, y_points):
    """Use two iterables to make a mesh grid, similar to numpy.meshgrid.

    Description: Given two iterables, return two lists of lists where x_grid has rows of x_points
    and y_grid has columns of y_points.

    Positional arguments:
    x_points -- iterable of x points
    y_points -- iterable of y points
    """
    rows, cols = len(x_points), len(y_points)
    x_grid = [x_points for __ in range(cols)]
    y_grid = [[y]*rows for y in y_points]
    return x_grid, y_grid
