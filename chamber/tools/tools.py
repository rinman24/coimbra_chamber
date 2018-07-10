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


def get_db_data(test_id):
    """
    Connect to database and gets mass and relative humidity data.

    Creates a connection to the chamber MySql database and gets the mass and
    calculated relative humidity data using CoolProp.

    Parameters
    ----------
    test_id : int
        TestID for the test to get data from.

    Returns
    -------
    list(floats)
        List of mass data pertaining to the TestID.
    list(floats)
        List of calculated relative humidity data pertaining to the TestID.
    """
    cnx = sqldb.connect_sqldb('test_chamber')
    cur = cnx.cursor()

    mass = sqldb.get_mass(cur, test_id)
    rel_hum = sqldb.get_rel_hum(cur, test_id)

    cnx.commit()
    cur.close()
    cnx.close()

    return mass, rel_hum


def get_hum_index(rel_hum):
    """
    Finds the indicies of relative humidities that are multiples of 10%.

    Searches the full list of relative humidities rel_hum and returns the
    indicies where the relative humidity is a multiple of 10%.

    Parameters
    ----------
    rel_hum : list of floats
        List of relative humidity percentages in decimal form.

    Returns
    -------
    list(int)
        List of indicies where the relative humidity is a multiple of 10% in
        rel_hum.
    """
    hum_index = []
    for hum in range(int(round(min(rel_hum)*100, -1)),
                     int(round(max(rel_hum)*100, -1)), 10):
        hum_index.append((np.abs(np.array(rel_hum) - hum/100).argmin()))
    if not hum_index:
        raise Exception('Can not resolve Relative Humidity, '
                        'insufficient Humidity variation')
    if hum_index[-1] == len(rel_hum) - 1:
        hum_index = hum_index[:-1]
    return hum_index


def lin_reg(mass, start, end, tol=0.99):
    """Calculates the slope, r^2, intercept for the argument humidity index.

    Calculaes slope, r^2, and the intercept for the linear regression that fits
    mass in the range defined by start and end, start being the center point of
    the regression and end being the width to either side which data will be
    taken. The function returns the slope, r^2 and intercept if the r^2 is
    above the argument tolerance, tol, which defaults to 0.99. Returns None if
    the r^2 value is below the tolerance.

    Parameters
    ----------
    mass : list of floats
        List of mass observatons.
    start : int
        Relative humidity index where the center of the regression is located.
    end : int
        Width to either side of start that data is included in the regression.
    tol : float
        The r^2 tolerance which dictates which slopes are retuned.
        Defaults to 0.99.

    Returns
    -------
    slope : float
        Slope of the linear regression.
    r_value : float
        r^2 value of the linear regression.
    intercept : float
        y-intercept of the linear regression.
    None : None
        if r^2 < tol
    """
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        range(len(mass))[start-end:start+end], mass[start-end:start+end])
    if r_value**2 >= tol:
        return slope, r_value**2, intercept
    else:
        return None


def get_lin(mass, hum_idx, tol=0.99, get_one=False):
    """Calculates the slope, r^2, intercept for the argument humidity index.

    Calculaes slope, r^2, and the intercept for the linear regression that fits
    mass in the range defined by start and end, start being the center point of
    the regression and end being the width to either side which data will be
    taken. The function returns the slope, r^2 and intercept if the r^2 is
    above the argument tolerance, tol, which defaults to 0.99. Returns None if
    the r^2 value is below the tolerance.

    Parameters
    ----------
    mass : list of floats
        List of mass observatons.
    hum_idx : list
        List of indicies where the relative humidity is a multiple of 10% in
        rel_hum.
    tol : float
        The r^2 tolerance which dictates which slopes are retuned.
        Defaults to 0.99.
    get_one : boolean
        Boolean that dictates weither to get and return one linear regression
        or all.

    Returns
    -------
    slope : list of floats
        List of slopes of the calculated linear regressions.
    r_squared : list of floats
        List of r^2 values of the calculated linear regressions.
    intercept : lsit of floats
        List of y-intercepts of the calculated linear regressions.
    ends : list of ints
        List of x-values for the plots of the linear regressions.
    """
    slope_r = []
    ends = []
    end = hum_idx
    if end > len(mass) / 2:
        end = len(mass) - hum_idx
    for end_idx in range(5, int(end)):
        lin = lin_reg(mass, hum_idx, end_idx, tol=tol)
        if lin:
            if get_one is True:
                return lin
            else:
                slope_r.append(lin)
                ends.append(end_idx)
    slope = [idx[0] for idx in slope_r]
    r_squared = [idx[1] for idx in slope_r]
    intercept = [idx[2] for idx in slope_r]
    return slope, r_squared, intercept, ends


def get_avg(mass, hum_idx, tol=0.99):
    """Calculates the average slope, intercept, and r^2 for a given tolerace level.

    Calculates and returns the average slope, intercept, and r_2 using all of
    the valid linear regressions under the argument r^2 tolerance level, tol.

    Parameters
    ----------
    mass : list of floats
        List of mass observatons.
    hum_idx : list
        List of indicies where the relative humidity is a multiple of 10% in
        rel_hum.
    tol : float
        The r^2 tolerance which dictates which slopes are retuned.
        Defaults to 0.99.

    Returns
    -------
    slope : float
        Avarage slope of the calculated linear regressions.
    r_squared : float
        Average r^2 value of the calculated linear regressions.
    intercept : float
        Average y-intercept of the calculated linear regressions.
    """
    slope, r_squared, intercept, end = get_lin(mass, hum_idx, tol)
    return np.average(slope), np.average(r_squared), np.average(intercept)


def get_set_width(mass, hum_idx, idx):
    """Calculates the average slope, intercept, and r^2 for a given tolerace level.

    Calculates and returns the average slope, intercept, and r_2 using all of
    the valid linear regressions under the argument r^2 tolerance level, tol.

    Parameters
    ----------
    mass : list of floats
        List of mass observatons.
    hum_idx : list
        List of indicies where the relative humidity is a multiple of 10% in
        rel_hum.
    idx : int
        The band width to one side that you wish to use to calulate the linear
        regression.

    Returns
    -------
    slope : float
        Slope of the calculated linear regression at the argument index.
    r_squared : float
        r^2 value of the calculated linear regression at the argument index.
    intercept : float
        y-intercept of the calculated linear regression at the argument index.
    """
    slope, r_squared, intercept, end = get_lin(mass, hum_idx)
    if len(slope) < idx:
        return None, None, None
    return slope[idx], r_squared[idx], intercept[idx]


def get_hum_percent(rel_hum, hum):
    """Converts the relative humidity percentage decimal into percent form (x100).

    Parameters
    ----------
    rel_hum : list of floats
        List of relative humidity percentages in decimal form.
    hum : int
        The index of the desired relative humidity percentage.

    """
    return round(rel_hum[hum]*100, -1)


def get_change(slope, step=1):
    """Calculates the percent change for each step in the inputed data, slope.

    Parameters
    ----------
    slope : list of floats
        List data for percent change calculation.
    step : int
        Step size for calculation of percent change. Defaults to 1

    Returns
    -------
    change : list of floats
        List of percent changes. Note length is one less than argument data,
        slope.
    """
    change = []
    for delta in range(1, len(slope), step):
        change.append((slope[delta] - slope[delta - 1]) / slope[delta])
    return change


def subplot_1_mass(fig, mass):
    """Adds the Evaporation Rate subplot to argument figure."""
    sub_1 = fig.add_subplot(3, 2, 1)
    sub_1.set_title('Ev-R [kg/s]')
    sub_1.plot(mass)


def subplot_2_rel_hum(fig, rel_hum):
    """Adds the Realtive humidity subplot to argument figure."""
    sub_2 = fig.add_subplot(3, 2, 2)
    sub_2.set_title('RH/t [%/s]')
    sub_2.plot(rel_hum)


def subplot_3_EvR(fig, ends, slope, hum_per_list):
    """Adds the Evaporation Rate Fits subplot to argument figure."""
    sub_3 = fig.add_subplot(3, 2, 3)
    sub_3.set_title('EvR [kg/s] / (BW/2) [s]')
    for key in hum_per_list:
        sub_3.plot(ends[key], slope[key], label="RH = {}%".format(key))


def subplot_4_change(fig, ends, slope, hum_per_list):
    """Adds the Percent Change of Fits subplot to argument figure."""
    sub_4 = fig.add_subplot(3, 2, 4)
    sub_4.set_title('% Change [%] / (BW/2) [s]')
    for key in hum_per_list:
        sub_4.plot(ends[key][1:501],
                   get_change(slope[key][:501]), label="RH = {}%".format(key))
    sub_4.legend(loc='center left', bbox_to_anchor=(1, 0.5))


def subplot_5_R(fig, ends, r_squared, hum_per_list):
    """Adds the R^2 subplot to argument figure."""
    sub_5 = fig.add_subplot(3, 2, 5)
    sub_5.set_title('R^2 / (BW/2) [s]')
    for key in hum_per_list:
        sub_5.plot(ends[key], r_squared[key], label="RH = {}%".format(key))


def subplot_6_lin(fig, mass, hum_dict, inter_99, slope_99, hum_per_list):
    """Adds the Evaporation Rate Linear Fits subplot to argument figure."""
    sub_6 = fig.add_subplot(3, 2, 6)
    sub_6.set_title('Ev-R W/ Fit R^2=0.99 [kg/s]')
    sub_6.plot(mass, color='y', label='Mass')
    for key in hum_per_list:
        sub_6.plot(range(hum_dict[key]-2000, hum_dict[key]+2000),
                   inter_99[key]+slope_99[key]*range(hum_dict[key]-2000,
                                                     hum_dict[key]+2000),
                   label="RH = {}%".format(key))
    sub_6.legend(loc='center left', bbox_to_anchor=(1, 0.5))


def generate_summary(test_id):
    """Summarises the test where test.TestID matches the argument test_id.

    Generates a graphical and tabular summary of the data for the argument test
    id's coresponing test. Neccessary values are calculated using helper
    functions. 6 subplots are produced and a tabular summary of information is
    printed to the console. The slopes using various methods of analysis,
    present in the tabular output, are returned.

    Parameters
    ----------
    test_id : int
        TestID for the test to summarize.

    Returns
    -------
    output_slopes : list of floats
        List of slopes for the relevant relative humidities calculated using
        various methods described in the tabular output.
    """
    mass, rel_hum = get_db_data(test_id)

    print(len(mass), len(rel_hum))

    hum_per_list = []
    slope, r_squared, ends, hum_dict = [{} for i in range(4)]
    slope_99, r_99, inter_99 = [{} for i in range(3)]
    slope_999, r_999, inter_999 = [{} for i in range(3)]
    avg_slope_99, avg_r_99, avg_inter_99 = [{} for i in range(3)]
    avg_slope_999, avg_r_999, avg_inter_999 = [{} for i in range(3)]
    set_slope_250, set_r_250, set_inter_250 = [{} for i in range(3)]
    set_slope_500, set_r_500, set_inter_500 = [{} for i in range(3)]
    hum_idx = get_hum_index(rel_hum)
    for hum in hum_idx:
        hum_per = get_hum_percent(rel_hum, hum)
        hum_per_list.append(hum_per)
        hum_dict[hum_per] = hum

        slope[hum_per], r_squared[hum_per], place_holder, ends[hum_per] = get_lin(mass, hum)

        slope_99[hum_per], r_99[hum_per], inter_99[hum_per] = get_lin(mass, hum, tol=0.99, get_one=True)
        slope_999[hum_per], r_999[hum_per], inter_999[hum_per] = get_lin(mass, hum, tol=0.999, get_one=True)

        avg_slope_99[hum_per], avg_r_99[hum_per], avg_inter_99[hum_per] = get_avg(mass, hum, tol=0.99)
        avg_slope_999[hum_per], avg_r_999[hum_per], avg_inter_999[hum_per] = get_avg(mass, hum, tol=0.999)

        set_slope_250[hum_per], set_r_250[hum_per], set_inter_250[hum_per] = get_set_width(mass, hum, 250)
        set_slope_500[hum_per], set_r_500[hum_per], set_inter_500[hum_per] = get_set_width(mass, hum, 500)

    hum_per_list.sort()

    fig = plt.figure(figsize=(8, 6))
    subplot_1_mass(fig, mass)
    subplot_2_rel_hum(fig, rel_hum)
    subplot_3_EvR(fig, ends, slope, hum_per_list)
    subplot_4_change(fig, ends, slope, hum_per_list)
    subplot_5_R(fig, ends, r_squared, hum_per_list)
    subplot_6_lin(fig, mass, hum_dict, inter_99, slope_99, hum_per_list)

    head = ['RH %', 'Method', 'Slope', 'Intercept', 'R^2']
    rows = []
    for key in hum_per_list:
        rows.append([key, 'R^2 Limit = 0.99',
                    slope_99[key], inter_99[key], r_99[key]])
        rows.append([key, 'R^2 Limit = 0.999', slope_999[key],
                    inter_999[key], r_999[key]])
        rows.append([key, 'Average R^2 > 0.99', avg_slope_99[key],
                    avg_inter_99[key], avg_r_99[key]])
        rows.append([key, 'Average R^2 > 0.999', avg_slope_999[key],
                    avg_inter_999[key], avg_r_999[key]])
        rows.append([key, 'Band Width = 500', set_slope_250[key],
                    set_r_250[key], set_inter_250[key]])
        rows.append([key, 'Band Width = 1000', set_slope_500[key],
                    set_r_500[key], set_inter_500[key]])
    output_slopes = []
    for idx in range(len(rows)):
        output_slopes.append(rows[idx][2])
    print(tabulate(rows, headers=head, tablefmt='orgtbl'))

    plt.tight_layout()
    plt.show()

    return output_slopes

if __name__ == "__main__":
    generate_summary(int(sys.argv[1]))
