"""
Analysis of test results.

Description to come, see:
http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

Note: This could actually be a class that extends DataFrame. In this case,
the module level functions would become methods of the class. But for now,
the following implementation will allow futher development.
"""
import math

from CoolProp.HumidAirProp import HAPropsSI
import pandas as pd
import numpy as np
import scipy.signal as signal

from chamber.analysis import chi2

TC_LIST = ['TC{0}'.format(i) for i in range(4, 14)]
TC_SET = set(TC_LIST)

FILTER_LENGTH = 3601
RH_STEP_PCT = 5

R_TUBE = 1.5e-2
A_TUBE = math.pi * pow(R_TUBE, 2)


# --------------------------------------------------------------------------- #
# Public Functions
# --------------------------------------------------------------------------- #
def results_from_csv(
        filepath,
        purge=False,
        param_list=['PressureSmooth', 'TeSmooth', 'DewPointSmooth'],
        sigma=4e-8,
        steps=100,
        ):
    """
    This function opens up a csv file, preprocesses the data, performs the
    chi-square regression, and returns the data and results in separate
    `DataFrames`.
    """

    dataframe = pd.read_csv(filepath)
    dataframe = preprocess(dataframe, param_list=param_list, purge=purge)
    results = analysis(dataframe, sigma=sigma, steps=steps)

    return (dataframe, results)


def preprocess(
        dataframe,
        param_list=['PressureSmooth', 'TeSmooth', 'DewPointSmooth'],
        purge=False
        ):
    """
    Call all of the helper functions to preprocess the `DataFrame`.
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


def analysis(dataframe, sigma=4e-8, steps=100, plot=False):
    """
    Use the dataframe and uncertainty to perform an opening window analysis.
    This function finds all valid relative humidity targets for a given
    `DataFrame`. For each of these targets, the function determines where the
    RH occurs, generates windows up to `max_half_length`, performs analysis
    on each window, and returns the results.

    Args:
        dataframe (DataFrame): Processed experimental data.
        sigma (float): Standard deviation of mass measurement. Defaults to
            4e-8 accoriding to the spec sheet.
        steps (int): Steps to increase the `half_length`.

    Returns:
        DataFrame: Results of the analysis of the test. Attributes include:
            - `a`: y-intercept
            - `sig_a`: standard deviation of `a`
            - `b`: slope (mass-transfer)
            - `b_sig`: standard deviation of `b`
            - `chi_2`: chi-square metric
            - `Q`: goodness of fit score (survival function)
            - `nu`: degrees of freedom
            - `RH`: target relative humidity
    """
    rh_targets = _get_valid_rh_targets(dataframe)
    res = []
    for rh in rh_targets:
        print('target={0}'.format(rh))
        idx = _get_target_idx(dataframe, rh)
        for len_ in _half_len_gen(dataframe, idx, steps=steps):
            print('{0}: \thalf_length={1}'.format(rh, len_))
            time, mass = _get_stat_group(dataframe, idx, len_)
            stats = chi2.chi2(time, mass, sigma, plot=plot)
            stats.append(rh)
            res.append(stats)
    return pd.DataFrame(
        res, columns=['a', 'sig_a', 'b', 'sig_b', 'chi2', 'Q', 'nu', 'RH']
        )


# --------------------------------------------------------------------------- #
# Internal Use Functions (Weakly Enforced)
# --------------------------------------------------------------------------- #
def _zero_time(dataframe):
    """
    Removes any offset from the `Idx` attribute of the `DataFrame` in place.
    """
    dataframe.Idx = dataframe.Idx - min(dataframe.Idx)
    return dataframe


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def _format_temp(dataframe):
    """
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
    Round `DewPoint` attribute of the `DataFrame` to one decimal place.
    Operation is performed in place.
    """
    dataframe.DewPoint = dataframe.DewPoint.round(1)
    return dataframe


def _format_pressure(dataframe):
    """
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
    Add `Te` attribute to the `DataFrame` that is an average of all other
    thermocouple attributes. Operation is performed in place.

    thermocouple attributes:
        `TC4`, `TC5`, `TC6`, `TC7`, `TC8`, `TC9`, `TC10`, `TC11`, `TC12`,
        `TC13`

    Args:
        dataframe (DataFrame): Experimental data containing TC4-TC13
            attributes.
        purge (bool): If `True` delete TC4-TC13 attributes from
           `DataFrame` in place. Defaults to `False`.

    Returns:
        DataFrame: Transformed `DataFrame` containing a new `Te` attribute.
            If `purge == True` then TC4-TC13 will have been dropped.
    """
    dataframe['Te'] = dataframe.loc[:, TC_LIST].apply(np.mean, axis=1).round(1)
    if purge:
        dataframe.drop(columns=TC_LIST, inplace=True)
    return dataframe


# --------------------------------------------------------------------------- #
# Smoothing
# --------------------------------------------------------------------------- #
def _add_smooth_avg_te(dataframe, purge=False):
    """
    Add `TeSmooth` attribute to the `DataFrame`. Operation is performed
    in place.

    Args:
        dataframe (DataFrame): Experimental data containing `Te` attribute.
        purge (bool): If `True` delete `Te` attributes from
           `DataFrame` in place. Defaults to `False`.

    Returns:
        DataFrame: Transformed `DataFrame` containing a new `TeSmooth`
            attribute. If `purge == True` then `Te` attribute was dropped.
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
    Add `DewPointSmooth` attribute to the `DataFrame`. Operation is performed
    in place.

    Args:
        dataframe (DataFrame): Experimental data containing `DewPoint`
            attribute.
        purge (bool): If `True` delete `DewPoint` attributes from `DataFrame``
            in place. Defaults to `False`.

    Returns:
        DataFrame: Transformed `DataFrame` containing a new `DewPointSmooth`
            attribute. If `purge == True` then `DewPoint`attribute was
            dropped.
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
    Add `PressureSmooth` attribute to the `DataFrame`. Operation is performed
    in place.

    Args:
        dataframe (DataFrame): Experimental data containing `Pressure`
            attribute.
        purge (bool): If `True` delete `Pressure` attributes from `DataFrame`
            in place. Defaults to `False`.

    Returns:
        DataFrame: Transformed `DataFrame` containing a new `DewPointSmooth`
            attribute. If `purge == True` then `DewPoint` attribute was
            dropped.
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
    This is a wrapper for the CoolProp.HumidAirProp.HAPropsSI API in Python.
    It accepts a list of pressure (Pa), temperature (K), and dew-point (K)
    and converts it to the required API.

    This allows the use of pandas.DataFrame.apply(_get_rh, axis=1) which is
    more readable.

    Args:
        params (list): A list of at least three elements where the first,
            second, and third elements are the values of pressure (Pa),
            temperature (K), and dew-point (K) respectively.

    Returns:
        float: Dimensionless relative humidity as specified by the `param`
            input list.
    """
    pressure = params[0]
    temp = params[1]
    dew_point = params[2]
    return HAPropsSI('RH', 'P', pressure, 'T', temp, 'Tdp', dew_point)


def _add_rh(
        dataframe,
        param_list=['PressureSmooth', 'TeSmooth', 'DewPointSmooth'],
        purge=False
        ):
    """
    Add `RH` attribute to the `DataFrame`. Operation is performed in place and
    uses the `_get_coolprop_rh` wrapper for the CoolProp.HumidAirProp.HAPropsSI
    API in Python.

    Args:
        dataframe (DataFrame): Experimental data containing (by default)
            `PressureSmooth`, `TeSmooth`, and `DewPointSmooth` attributes.
            This behavior can be modified using the optional `param_list`
            parameter, see below.
        param_list (list): List of parameters to use to calculate the
            relative humidity using the CoolProp API, see `_get_coolprop_rh`
            docstring for more detail.
        purge (bool): If `True` delete the third element from the
            `param_list`. This third element (index = 2) represents the
            dew-point. It could be `DewPoint`, `DewPointSmooth`, etc.
            Defaults to `False`.

    Returns:
        DataFrame: Transformed `DataFrame` containing a new `RH` attribute.
            If `purge == True` then the attribute representing the dew-point
            was dropped.
    """

    dataframe['RH'] = (
        dataframe.loc[:, param_list].apply(_get_coolprop_rh, axis=1)
        )
    if purge:
        dataframe.drop(columns=param_list[2], inplace=True)
    return dataframe


# --------------------------------------------------------------------------- #
# Selecting Data For Fits
# --------------------------------------------------------------------------- #
def _get_max_half_len(dataframe, target_idx, max_=10000):
    """
    Return the maximum half-length of datapoints before hitting either the
    first element (left) or the last element (right). The half-length is used
    to extract a sample of 2*half-length + 1 data points centered at the
    target index.

    Args:
        dataframe (DataFrame): Experimental data. The DataFrame is only used
            to determine the number of elements it contains. The dataframe is
            input rather than its length explicitly to increase readability
            and code consistancy. Other much more substantial bottlenecks exist
            in this module; for example, the adding relative humidity.
        target_idx (int): Index in the dataframe that corresponds to the
            relative humidity. When the time-step is one second, the `Idx`
            attribute and the DataFrame.index will be the same, however, this
            is not always the case. Because the sampling rate may change, the
            decision is made to make the DataFrame.index the standard, unless
            regression analysis is being performed.

    Returns:
        int: maximum half window length

    Raises:
        IndexError: If calculated `max_half_length is zero or negative. This
            occurs when the `target_idx` is negative, zero, >= len(DataFrame).
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
    Get the target_idx from the `DataFrame` given a target dimensionless
    relative humidity. As noted in the `_get_max_half_len()` docstring,
    the target_idx refers to the DataFrame.index rather than the attribute
    `Idx`, which was specific to data acquisition.

    It should be noted that the implementation selects the first occurance
    of the closest realtive humidity, approacing from the bottom. In other
    words, the `target_rh` - `DataFrame.RH` will be positive when the
    observed RH is less than the target. As a result, the function looks
    for a minimum positive value.

    Args:
        dataframe (DataFrame): Experimental data containing `RH`
            attribute.
        target_rh (float): Dimensionless relative humidity, typically
            between zero and one.

    Returns:
        int: The DataFrame.index coresponding to the earliert time the
        observed dimensionless relative humidity obtained the value
        before it exceeded or equaled the target.
    """
    rh = dataframe.RH.copy()
    # performing rh manipulation in place
    # This is no longer rh
    rh = target_rh - rh
    target_idx = rh[rh > 0].idxmin()
    return target_idx


def _get_stat_group(dataframe, target_idx, half_len):
    """
    Use the `target_idx` and `half_length` to return a group of observations
    on which to perform perform statistial analysis. Note, this function
    returns a copy of the data for statistical analysis so that there is no
    risk of contamination durring analysis.

    NOTE: This method employs pandas.DataFrame.loc[], which is inclusive
        unline python's list indexing.

    Args:
        dataframe (DataFrame): Experimental data containing `Idx` and
            `Mass` attributes.
        target_idx (int): Index in the dataframe that corresponds to the
            relative humidity. When the time-step is one second, the `Idx`
            attribute and the DataFrame.index will be the same, however, this
            is not always the case. Because the sampling rate may change, the
            decision is made to make the DataFrame.index the standard, unless
            regression analysis is being performed.
        half_len (int): The number of elements to select on either side of
            the target index.

    Returns:
        list: List of length 2. The first element (index 0) is a copy of
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

    Args:
        dataframe (DataFrame): Experimental data containing `RH` attribute.
        rh_ste_pct (int): Size of RH steps in percent. Defaults to 5.

    Returns:
        list: List of all the valid relative humidity targets for the given
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
    """"
    Progressively increase the the `half_length` until you exceed the maximum
    half length as specified by `_get_max_half_len()`.

    Args:
        dataframe (DataFrame): Experimental data required for
            `_get_max_half_length()`.

    Yields:
        int: The next `half_lenth` to be used to grab data.
    """
    max_half_len = _get_max_half_len(dataframe, target_idx)

    half_len = steps
    while half_len <= max_half_len:
        yield half_len
        half_len += steps
