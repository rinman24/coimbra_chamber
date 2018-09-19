"""
Analysis of test results.

Description to come, see:
http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

Notes
-----
This could actually be a class that extends DataFrame. In this case,
the module level functions would become methods of the class. But for now,
the following implementation will allow futher development.

Functions
---------
- `mass_transfer` -- perform analysis on the experimental data.
- `preprocess` -- ready a `DataFrame` for analysis.
- `results_from_csv` -- get analysis results from a .csv file.

"""
from itertools import repeat
import math
import multiprocessing as multi

from CoolProp.HumidAirProp import HAPropsSI
import pandas as pd
import numpy as np
import scipy.signal as signal
from tqdm import tqdm

from chamber.analysis import chi2
from chamber.models import models
from chamber.models import uncertainty as unc

TC_LIST = ['TC{0}'.format(i) for i in range(4, 14)]
TC_SET = set(TC_LIST)

FILTER_LENGTH = 3601
RH_STEP_PCT = 5

R_TUBE = 1.5e-2
A_TUBE = math.pi * pow(R_TUBE, 2)

CPU_COUNT = multi.cpu_count()


# --------------------------------------------------------------------------- #
# Public Functions
# --------------------------------------------------------------------------- #
def preprocess(
        dataframe,
        param_list=['PressureSmooth', 'TeSmooth', 'DewPointSmooth'],
        purge=False
        ):
    """
    Readies a `DataFrame` for further analysis.

    This function takes in a `DataFrame` and calls all of the module helper
    functions to produce a `DataFrame` that is ready for analysis.

    The following steps are included in 'preprocess':
        '_zero_time'
        '_format_temp'
        '_format_dew_point'
        '_format_pressure'
        '_add_avg_te'
        '_add_smooth_avg_te'
        '_add_smooth_dew_point'
        '_add_smooth_pressure'
        '_add_rh'

        See respective docstrings for more details.

    Parameters
    ----------
    dataframe: DataFrame
        A `DataFrame` of experimental data to be preprocessed.
    param_list: list(str)
        List of parameters to use to calculate the relative humidity using the
        CoolProp API, see `_get_coolprop_rh` docstring for more detail.
        Defaults to: `['PressureSmooth', 'TeSmooth', 'DewPointSmooth']`.
    purge: bool
        If `True` the original raw data is removed from the
        returned `DataFrame`. If `False` the raw data remains in the
        'DataFrame'. Defaults to `False`.

    Returns
    -------
    DataFrame
        The preprocessed data.

    Examples
    --------
    .. todo:: Examples.

    """
    dataframe = _zero_time(dataframe)

    dataframe = _format_temp(dataframe)
    dataframe = _format_dew_point(dataframe)
    dataframe = _format_pressure(dataframe)

    dataframe = _add_avg_te(dataframe, purge=purge)

    dataframe = _add_smooth_avg_te(dataframe, purge=purge)
    dataframe = _add_smooth_dew_point(dataframe, purge=purge)
    dataframe = _add_smooth_pressure(dataframe, purge=purge)

    dataframe = _add_rh(dataframe, param_list=param_list, purge=purge)

    return dataframe


def mass_transfer(dataframe, sigma=4e-8, steps=100, plot=False):
    """
    Perform analysis of experiment.

    Use the dataframe and uncertainty to perform an opening window analysis.
    This function finds all valid relative humidity targets for a given
    `DataFrame`. For each of these targets, the function determines where the
    RH occurs, generates windows up to `max_half_length`, performs analysis
    on each window, and returns the results.

    Parameters
    ----------
    dataframe:  DataFrame
        Processed experimental data.
    sigma: float
        Standard deviation of mass measurement. Defaults to 4e-8 accoriding to
        the spec sheet.
    steps: int
        Steps to increase the `half_length`.

    Returns
    -------
    DataFrame
        Results of the analysis of the test. Attributes include:
        - `a`: y-intercept
        - `sig_a`: standard deviation of `a`
        - `b`: slope (mass-transfer)
        - `b_sig`: standard deviation of `b`
        - `chi_2`: chi-square metric
        - `Q`: goodness of fit score (survival function)
        - `nu`: degrees of freedom
        - `RH`: target relative humidity
        - `SigRH`: target relative humidity
        - `spalding_mdpp`: mass flux determinded by Spalding Model

    Examples
    --------
    .. todo:: Examples.

    """
    print('Starting analysis...')
    rh_targets = _get_valid_rh_targets(dataframe)
    res = []
    pool = multi.Pool(CPU_COUNT)
    no_format_list = pool.starmap(
        _multi_analysis,
        zip(
            repeat(dataframe), repeat(sigma), repeat(steps),
            repeat(plot), rh_targets
        )
    )
    for col in no_format_list:
        res += col
    pool.close()
    pool.join()
    print('Analysis complete.')
    res_df = pd.DataFrame(
        res, columns=['a', 'sig_a', 'b', 'sig_b', 'chi2', 'Q', 'nu',
                      'RH', 'SigRH', 'p', 't_e', 't_dp', 'spald_mdpp',
                      'spald_mdpp_unc', 'spald_t_s']
        )
    return res_df


def _multi_analysis(dataframe, sigma, steps, plot, rh):
    """Extract values from dataframe and build the analyzed rows as lists."""
    idx = _get_target_idx(dataframe, rh)
    m_l = dataframe['Mass'].iloc[idx]
    p = dataframe['PressureSmooth'].iloc[idx]
    t_e = dataframe['TeSmooth'].iloc[idx]
    t_dp = dataframe['DewPointSmooth'].iloc[idx]
    ref = 'constant'
    rule = '1/2'
    spald = models.Spalding(m_l, p, t_e, t_dp, ref, rule)
    sol = spald.solve_system(2e-7, 0.01, 0.1, 0.01)
    mdpp = unc.mdpp_unc(sol.mdpp, spald)
    t_s = sol.t_s
    stats = []
    for _len in _half_len_gen(dataframe, idx, steps=steps):
        stats.append(_add_mass(dataframe, rh, _len, idx, steps,
                     sigma, mdpp[0], mdpp[1], t_s, plot))
    return stats


def _add_mass(dataframe, rh, len_, idx, steps, sigma,
              mdpp, mdpp_unc, t_s, plot):
    """Calculate the Chi2 statistics for a single row of data."""
    time, mass = _get_stat_group(dataframe, idx, len_)
    stats = chi2.chi2(time, mass, sigma, plot=plot)
    stats.append(rh)
    stats.append(
        dataframe.loc[dataframe['Idx'] == idx]['SigRH'].iloc[0])
    stats.append(
        dataframe.loc[dataframe['Idx'] == idx]['PressureSmooth'].iloc[0]
    )
    stats.append(
        dataframe.loc[dataframe['Idx'] == idx]['TeSmooth'].iloc[0]
    )
    stats.append(
        dataframe.loc[dataframe['Idx'] == idx]['DewPointSmooth'].iloc[0]
    )
    stats.append(mdpp)
    stats.append(mdpp_unc)
    stats.append(t_s)
    return stats


# --------------------------------------------------------------------------- #
# Internal Use Functions (Weakly Enforced)
# --------------------------------------------------------------------------- #
def _zero_time(dataframe):
    """Remove offset from `Idx` attribute of `DataFrame` in place."""
    dataframe.Idx = dataframe.Idx - min(dataframe.Idx)
    return dataframe


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def _format_temp(dataframe):
    """
    Format observed temperature.

    Round thermocouple attributes of the `DataFrame` to one decimal place.
    Operation is performed in place.

    thermocouple attributes:
        `TC4`, `TC5`, `TC6`, `TC7`, `TC8`, `TC9`, `TC10`, `TC11`, `TC12`,
        `TC13`
    """
    dataframe.loc[:, TC_LIST] = dataframe.loc[:, TC_LIST].round(1)
    return dataframe


def _format_dew_point(dataframe):
    """
    Format dew point observation.

    Round `DewPoint` attribute of the `DataFrame` to one decimal place.
    Operation is performed in place.
    """
    dataframe.DewPoint = dataframe.DewPoint.round(1)
    return dataframe


def _format_pressure(dataframe):
    """
    Format pressure observation.

    Convert `Pressure` attribute of the `DataFrame` to an integer.
    Operation is performed in place.

    """
    dataframe.Pressure = dataframe.Pressure.round(0).astype(int)
    return dataframe


# --------------------------------------------------------------------------- #
# Averaging
# --------------------------------------------------------------------------- #
def _add_avg_te(dataframe, purge=False):
    """
    Add average temperature to the `DataFrame`.

    Add `Te` attribute to the `DataFrame` that is an average of all other
    thermocouple attributes. Operation is performed in place.

    thermocouple attributes
    -----------------------
        `TC4`, `TC5`, `TC6`, `TC7`, `TC8`, `TC9`, `TC10`, `TC11`, `TC12`,
        `TC13`

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data containing TC4-TC13 attributes.
    purge: bool
        If `True` delete TC4-TC13 attributes from `DataFrame` in place.
        Defaults to `False`.

    Returns
    -------
    DataFrame:
        Tansformed `DataFrame` containing a new `Te` attribute.
        If `purge == True` then TC4-TC13 will have been dropped.

    """
    pool = multi.Pool(CPU_COUNT)
    df_stack = np.array_split(dataframe, CPU_COUNT)
    dataframe['Te'] = pd.concat(pool.map(_multi_te, df_stack))
    pool.close()
    pool.join()
    if purge:
        dataframe.drop(columns=TC_LIST, inplace=True)
    return dataframe


def _multi_te(dataframe):
    """Add average temperature to the `DataFrame`."""
    df_te = dataframe.loc[:, TC_LIST].apply(np.mean, axis=1).round(1)
    return df_te


# --------------------------------------------------------------------------- #
# Smoothing
# --------------------------------------------------------------------------- #
def _add_smooth_avg_te(dataframe, purge=False):
    """
    Add smoothed temperature.

    Add `TeSmooth` attribute to the `DataFrame`. Operation is performed
    in place.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data containing `Te` attribute.
    purge: bool
        If `True` delete `Te` attributes from `DataFrame` in place.
        Defaults to `False`.

    Returns
    -------
    DataFrame
        Transformed `DataFrame` containing a new `TeSmooth` attribute.
        If `purge == True` then `Te` attribute was dropped.

    """
    dataframe['TeSmooth'] = signal.savgol_filter(
        dataframe.Te, FILTER_LENGTH, 1
        )
    dataframe.TeSmooth = dataframe.TeSmooth.round(1)
    if purge:
        dataframe.drop(columns='Te', inplace=True)
    return dataframe


def _add_smooth_dew_point(dataframe, purge=False):
    """
    Add smoothed dew point.

    Add `DewPointSmooth` attribute to the `DataFrame`. Operation is performed
    in place.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data containing `DewPoint` attribute.
    purge: bool
        If `True` delete `DewPoint` attributes from `DataFrame` in place.
        Defaults to `False`.

    Returns
    -------
    DataFrame
        Transformed `DataFrame` containing a new `DewPointSmooth` attribute.
        If `purge == True` then `DewPoint`attribute was dropped.

    """
    dataframe['DewPointSmooth'] = signal.savgol_filter(
        dataframe.DewPoint, FILTER_LENGTH, 1
    )
    dataframe.DewPointSmooth = dataframe.DewPointSmooth.round(1)
    if purge:
        dataframe.drop(columns='DewPoint', inplace=True)
    return dataframe


def _add_smooth_pressure(dataframe, purge=False):
    """
    Add smoothed pressure.

    Add `PressureSmooth` attribute to the `DataFrame`. Operation is performed
    in place.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data containing `Pressure` attribute.
    purge: bool
        If `True` delete `Pressure` attributes from `DataFrame` in place.
        Defaults to `False`.

    Returns
    -------
    DataFrame
        Transformed `DataFrame` containing a new `DewPointSmooth` attribute.
        If `purge == True` then `DewPoint` attribute was dropped.

    """
    dataframe['PressureSmooth'] = signal.savgol_filter(
        dataframe.Pressure, FILTER_LENGTH, 1
    )
    dataframe.Pressure = dataframe.Pressure.round(0).astype(int)
    if purge:
        dataframe.drop(columns='Pressure', inplace=True)
    return dataframe


# --------------------------------------------------------------------------- #
# Relative Humidity
# --------------------------------------------------------------------------- #
def _get_coolprop_rh(params):
    """
    Get relative humidity.

    This is a wrapper for the CoolProp.HumidAirProp.HAPropsSI API in Python.
    It accepts a list of pressure (Pa), temperature (K), and dew-point (K)
    and converts it to the required API.

    This allows the use of pandas.DataFrame.apply(_get_rh, axis=1) which is
    more readable.

    Parameters
    ----------
    params: list(float)
        A list of at least three elements where the first, second, and third
        elements are the values of pressure (Pa), temperature (K),
        and dew-point (K) respectively.

    Returns
    -------
    float
        Dimensionless relative humidity as specified by the `param` input list.

    """
    pressure = params[0]
    temp = params[1]
    dew_point = params[2]
    return HAPropsSI('RH', 'P', pressure, 'T', temp, 'Tdp', dew_point)


def _get_coolprop_rh_err(params):
    """
    Get relative humidity error.

    This is a wrapper for the CoolProp.HumidAirProp.HAPropsSI API in Python.
    It accepts a list of pressure (Pa), temperature (K), and dew-point (K)
    and converts it to the required API.

    This allows the use of pandas.DataFrame.apply(_get_rh, axis=1) which is
    more readable.

    Parameters
    ----------
    params: list(float)
        A list of at least three elements where the first, second, and third
        elements are the values of pressure (Pa), temperature (K),
        and dew-point (K) respectively.

    Returns
    -------
    float
        Dimensionless relative humidity error as specified by the `param` input
        list.

    """
    pressure = params[0]
    temp = params[1]
    dew_point = params[2]
    high_rh = HAPropsSI('RH', 'P', pressure, 'T', temp, 'Tdp', dew_point + 0.2)
    low_rh = HAPropsSI('RH', 'P', pressure, 'T', temp, 'Tdp', dew_point - 0.2)
    rh = HAPropsSI('RH', 'P', pressure, 'T', temp, 'Tdp', dew_point)
    upper_err = abs(high_rh - rh)
    lower_err = abs(rh - low_rh)
    if upper_err > lower_err:
        return upper_err
    else:
        return lower_err


def _add_rh(
        dataframe,
        param_list=['PressureSmooth', 'TeSmooth', 'DewPointSmooth'],
        purge=False
        ):
    """
    Add relative humidity to the `DataFrame`.

    Add `RH` attribute to the `DataFrame`. Operation is performed in place and
    uses the `_get_coolprop_rh` wrapper for the CoolProp.HumidAirProp.HAPropsSI
    API in Python.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data containing (by default) `PressureSmooth`, `TeSmooth`,
        and `DewPointSmooth` attributes. This behavior can be modified using
        the optional `param_list` parameter, see below.
    param_list: list(str)
        List of parameters to use to calculate the relative humidity using the
        CoolProp API, see `_get_coolprop_rh` docstring for more detail.
    purge: bool
        If `True` delete the third element from the `param_list`. This third
        element (index = 2) represents the dew-point. It could be `DewPoint`,
        `DewPointSmooth`, etc. Defaults to `False`.

    Returns
    -------
    DataFrame
        Transformed `DataFrame` containing a new `RH` attribute.
        If `purge == True` then the attribute representing the dew-point
        was dropped.

    """
    pool = multi.Pool(CPU_COUNT)
    df_stack = np.array_split(dataframe, CPU_COUNT)
    dataframe['RH'] = pd.concat(
        pool.starmap(_multi_rh, zip(df_stack, repeat(param_list)))
        )
    dataframe['SigRH'] = pd.concat(
        pool.starmap(_multi_rh_err, zip(df_stack, repeat(param_list)))
        )
    pool.close()
    pool.join()
    if purge:
        dataframe.drop(columns=param_list[2], inplace=True)
    return dataframe


def _multi_rh(dataframe, param_list):
    """Apply `_get_coolprop_rh` to the argument dataframe."""
    df = dataframe.loc[:, param_list].apply(_get_coolprop_rh, axis=1)
    return df


def _multi_rh_err(dataframe, param_list):
    """Apply `_get_coolprop_rh_err` to the argument dataframe."""
    df = dataframe.loc[:, param_list].apply(_get_coolprop_rh_err, axis=1)
    return df


# --------------------------------------------------------------------------- #
# Selecting Data For Fits
# --------------------------------------------------------------------------- #
def _get_max_half_len(dataframe, target_idx, max_=10000):
    """
    Get maximum window half length.

    Return the maximum half-length of datapoints before hitting either the
    first element (left) or the last element (right). The half-length is used
    to extract a sample of 2*half-length + 1 data points centered at the
    target index.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data. The DataFrame is only used to determine the number
        of elements it contains. The dataframe is input rather than its length
        explicitly to increase readability and code consistancy. Other much
        more substantial bottlenecks exist in this module; for example,
        the adding relative humidity.
    target_idx: int
        Index in the dataframe that corresponds to the relative humidity.
        When the time-step is one second, the `Idx` attribute and the
        DataFrame.index will be the same, however, this is not always the case.
        Because the sampling rate may change, the decision is made to make the
        DataFrame.index the standard, unless regression analysis is being
        performed.

    Returns
    -------
    int
        Maximum half window length.

    Raises
    ------
    IndexError
        If calculated `max_half_length is zero or negative. This occurs when
        the `target_idx` is negative, zero, >= len(DataFrame).

    """
    to_the_right = (len(dataframe)-1) - target_idx
    to_the_left = target_idx
    max_half_len = min(to_the_left, to_the_right)

    if max_half_len > max_:
        max_half_len = max_

    if max_half_len > 0:
        return max_half_len
    else:
        raise IndexError(
            "no 'half length' available for the target index: "
            "target must have at least one element to right or left"
            )


def _get_target_idx(dataframe, target_rh):
    """
    Get target index.

    Get the target_idx from the `DataFrame` given a target dimensionless
    relative humidity. As noted in the `_get_max_half_len()` docstring,
    the target_idx refers to the DataFrame.index rather than the attribute
    `Idx`, which was specific to data acquisition.

    It should be noted that the implementation selects the first occurance
    of the closest realtive humidity, approacing from the bottom. In other
    words, the `target_rh` - `DataFrame.RH` will be positive when the
    observed RH is less than the target. As a result, the function looks
    for a minimum positive value.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data containing `RH` attribute.
    target_rh: float
        Dimensionless relative humidity, typically between zero and one.

    Returns
    -------
    int
        The DataFrame.index coresponding to the earliert time the
        observed dimensionless relative humidity obtained the value
        before it exceeded or equaled the target.

    """
    rh = dataframe.RH.copy()
    rh = target_rh - rh
    target_idx = rh[rh > 0].idxmin()
    return target_idx


def _get_stat_group(dataframe, target_idx, half_len):
    """
    Get statistics group.

    Use the `target_idx` and `half_length` to return a group of observations
    on which to perform perform statistial analysis. Note, this function
    returns a copy of the data for statistical analysis so that there is no
    risk of contamination durring analysis.

    Notes
    -----
        This method employs pandas.DataFrame.loc[], which is inclusive
        unline python's list indexing.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data containing `Idx` and `Mass` attributes.
    target_idx: int
        Index in the dataframe that corresponds to the relative humidity.
        When the time-step is one second, the `Idx` attribute and the
        DataFrame.index will be the same, however, this is not always the case.
        Because the sampling rate may change, the decision is made to make the
        DataFrame.index the standard, unless regression analysis is being
        performed.
    half_len: int
        The number of elements to select on either side of the target index.

    Returns
    -------
    list
        List of length 2. The first element (index 0) is a copy of
        the `Idx` attribute of the `DataFrame` for analysis. The second
        element (index 1) is a copy of the `Mass` attribute of the `DataFrame`
        for analysis.

    """
    start = target_idx - half_len
    stop = target_idx + half_len

    return [dataframe.loc[start:stop, 'Idx'].copy(),
            dataframe.loc[start:stop, 'Mass'].copy()]


def _get_valid_rh_targets(dataframe, rh_step_pct=5):
    """
    Use the dataframe to return a list of valid RH values for analysis.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data containing `RH` attribute.
    rh_ste_pct: int
        Size of RH steps in percent. Defaults to 5.

    Returns
    -------
    list
        List of all the valid relative humidity targets for the given
        `DataFrame`.

    """
    # Multipy by 100 to get into percent
    rh_min = dataframe.RH.min() * 100
    rh_max = dataframe.RH.max() * 100

    rh_min_valid = int(math.ceil(rh_min/rh_step_pct)) * rh_step_pct
    rh_max_valid = int(math.floor(rh_max/rh_step_pct)) * rh_step_pct

    # Devide by 100 to get back to dimensionless RH
    my_map = map(
        lambda x: x/100,
        range(rh_min_valid, rh_max_valid + 5, rh_step_pct)
    )

    return list(my_map)


def _half_len_gen(dataframe, target_idx, steps=100):
    """
    Generate window half length.

    Progressively increase the the `half_length` until you exceed the maximum
    half length as specified by `_get_max_half_len()`.

    Parameters
    ----------
    dataframe: DataFrame
        Experimental data required for `_get_max_half_length()`.

    Yeilds
    -------
    int
        The next `half_lenth` to be used to grab data.

    """
    max_half_len = _get_max_half_len(dataframe, target_idx)

    half_len = steps
    while half_len <= max_half_len:
        yield half_len
        half_len += steps


def _get_df_row(res_df):
    """
    Get the `DataFrame` row with the index of the last occurence of Q >= 0.49.

    Get the row of data from a `DataFrame` corresponding to the index found by
    stepping through the 'Results' data backwards and selecting the index of
    the first occurence  of Q >= 0.49 from the reversed data. This is assuming
    that a Chi2 fit is appropreate for the data and that the Q values drop fro
    1, through 0.5, to 0.

    Parameters
    ----------
    res_df: DataFrame
        `DataFrame` object with a 'Q' value column.

    Returns
    -------
    DataFrame
        The one row `DataFrame` with the specified index.

    Examples
    --------
    >>> df_dict = dict(A=[0, 1, 2, 3, 4],
                       B=[a, b, c, d, e]
                       Q=[1, 0.6, 0.51, 0.1, 0])
    >>> df = pd.DataFrame(df_dict)
    >>> _get_df_row(df)
        A    B    Q
    3   3    d    0.51

    """
    q = 0
    for i in range(len(res_df)-1, -1, -1):
        if q < res_df.iloc[i].Q:
            q = res_df.iloc[i].Q
        if q >= 0.49:
            df_row = res_df[res_df.index == i]
            return df_row
