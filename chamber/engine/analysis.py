"""Analysis engine module."""

import math
import re

import dask.dataframe as dd
from dask.multiprocessing import get
import CoolProp.HumidAirProp as hap
import matplotlib.pyplot as plt
import nptdms
import numpy as np
import pandas as pd
from scipy import signal
import uncertainties as un
from uncertainties import unumpy as unp

import chamber.utility.uncert as un_util


# ----------------------------------------------------------------------------
# Internal logic (adding experiment)


def _tdms_2_dict_of_df(filepath):
    """
    Convert tdms file to a dictionary of pandas DataFrames.

    Parameters
    ----------
    filepath : str
        filepath to the tdms file.

    Returns
    -------
    dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, and `test`.

    Examples
    --------
    >>> dataframes = _tdms_2_dict_of_df('path')

    """
    tdms_file = nptdms.TdmsFile(filepath)

    settings_df = tdms_file.object('Settings').as_dataframe()
    settings_df = settings_df.rename(columns={'DutyCycle': 'Duty'})

    data_df = tdms_file.object('Data').as_dataframe()

    test_df = pd.DataFrame(
        data=dict(
            Author=tdms_file.object().properties['author'],
            DateTime=tdms_file.object().properties['DateTime'],
            Description=tdms_file.object().properties['description']
            ),
        index=[0]
        )

    dataframes = dict(setting=settings_df, data=data_df, test=test_df)

    return dataframes


def _build_setting_df(dataframes):
    """
    Add `Temperature` and `Pressure` keys to `setting` dataframe.

    Calculate averave experimental values of temperature and pressure using
    all observations. Average temperature and pressure are then rounded to the
    nearest 5 K and 5000 Pa, respectively.

    If `Duty` is zero in settings, `PowOut` and `PowRef` columns are
    dropped from `data` dataframe.

    If `IsMass` is truthy in settings, TC0-3 are dropped from `data`
    dataframe. Else, `Mass` is dropped from `data` dataframe.

    Parameters
    ----------
    dataframes : dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, and `test`.

    Returns
    -------
    dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, and `test`.

    Examples
    --------
    >>> dataframes = _tdms_2_dict_of_df('path')
    >>> dataframes = _build_setting_df(dataframes)

    """
    if not dataframes['setting'].loc[0, 'Duty']:
        dataframes['data'].drop(columns=['PowOut', 'PowRef'], inplace=True)

    if dataframes['setting'].loc[0, 'IsMass']:  # TCs 0-3 not connected.
            initial_tc = 4
            dataframes['data'].drop(
                columns=['TC{}'.format(tc_bad) for tc_bad in range(0, 4)],
                inplace=True
                )
    else:
        initial_tc = 0
        dataframes['data'].drop(columns=['Mass'], inplace=True)

    tc_cols = ['TC{}'.format(num) for num in range(initial_tc, 14)]
    avg_temp = dataframes['data'].loc[:, tc_cols].mean().mean()
    avg_pressure = dataframes['data'].loc[:, 'Pressure'].mean()

    dataframes['setting'].loc[0, 'Pressure'] = _round(avg_pressure, 5000)
    dataframes['setting'].loc[0, 'Temperature'] = _round(avg_temp, 5)

    return dataframes


def _build_observation_df(dataframes):
    """
    Convert `data` dataframe into `observation` dataframe.

    Columns are 'popped' off of `data` an inserted into `observation` one at a
    time to avoid creating a full copy.

    Parameters
    ----------
    dataframes : dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, and `test`.

    Returns
    -------
    dict of {str: pandas.DataFrame}
        Keys same as input plus `observation`.

    Examples
    --------
    >>> dataframes = _tdms_2_dict_of_df(filepath)
    >>> dataframes = _build_setting_df(dataframes)
    >>> dataframes = _build_observation_df(dataframes)

    """
    columns_to_keep = ['CapManOk', 'DewPoint', 'Idx', 'OptidewOk', 'Pressure']

    if dataframes['setting'].loc[0, 'IsMass']:
        columns_to_keep.append('Mass')

    if dataframes['setting'].loc[0, 'Duty']:
        columns_to_keep += ['PowOut', 'PowRef']

    dataframes['observation'] = pd.DataFrame()
    for col in columns_to_keep:
        dataframes['observation'].loc[:, col] = dataframes['data'].pop(col)

    return dataframes


def _build_temp_observation_df(dataframes):
    """
    Pivot remaining tc columns in `data` to the format required by database.

    Columns are 'popped' off of `data` an inserted into `temp_observation` one
    at a time to avoid creating a full copy.

    Parameters
    ----------
    dataframes : dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, `test`, and `observation`.

    Returns
    -------
    dict of {str: pandas.DataFrame}
        Keys same as input plus `temp_observation`.

     Examples
    --------
    >>> dataframes = _tdms_2_dict_of_df(filepath)
    >>> dataframes = _build_setting_df(dataframes)
    >>> dataframes = _build_observation_df(dataframes)
    >>> dataframes = _build_temp_observation_df(dataframes)

    """
    tc_num, temp, idx = [], [], []
    elements = len(dataframes['data'].index)
    if dataframes['setting'].loc[0, 'IsMass']:
        initial_tc = 4
    else:
        initial_tc = 0

    for tc in range(initial_tc, 14):
        tc_num += [tc]*elements
        col = 'TC{}'.format(tc)
        temp += list(dataframes['data'].pop(col))
        idx += list(dataframes['observation'].loc[:, 'Idx'])

    dataframes['temp_observation'] = pd.DataFrame(
        dict(
            ThermocoupleNum=tc_num,
            Temperature=temp,
            Idx=idx
            )
        )

    return dataframes


# ----------------------------------------------------------------------------
# Internal logic (processing data)


def _calc_avg_te(temp_data):
    """Calculate average temperature."""
    # Manager is responsible for pivoting the table before calling.
    mean = temp_data.mean(axis=1)
    std = temp_data.std(axis=1)

    avg_te = pd.DataFrame(
        unp.uarray(mean, std), columns=['AvgTe'], index=temp_data.index
        )

    return avg_te


def _filter_observations(obs_data):
    """
    Apply Savitzky-Golay filter to observation data.

    Notes
    -----
    No uncertainty yet as no calculations have been done. Conversion to
    `ufloat` at this stage would be a poor use of resources. Unlike
    `_calc_avg_temp` where we would like to propigate the error associated
    with the calculation that was performed.

    """
    filt_obs = obs_data.copy()

    filt_obs.DewPoint = signal.savgol_filter(filt_obs.DewPoint, 1801, 2)
    filt_obs.Mass = signal.savgol_filter(filt_obs.Mass, 301, 2)
    filt_obs.Pressure = signal.savgol_filter(filt_obs.Pressure, 3601, 1)

    return filt_obs


def _preprocess_observations(obs_data, temp_data):
    """Preprocess and ask user to proceed."""
    avg_te = _calc_avg_te(temp_data)
    nominal_temps = np.array(
        [avg_te.loc[i, 'AvgTe'].nominal_value for i in avg_te.index]
        )
    temp_std = np.array(
        [avg_te.loc[i, 'AvgTe'].std_dev for i in avg_te.index]
        )

    filt_obs = _filter_observations(obs_data)

    fig = plt.figure(figsize=(10, 8))

    # Temperature ------------------------------------------------------------
    ax = fig.add_subplot(2, 2, 1)
    ax.plot(avg_te.index, nominal_temps, label='Nominal $T_e$')
    ax.fill_between(
        avg_te.index, nominal_temps-temp_std, nominal_temps+temp_std,
        color='gray', alpha=0.2
        )
    ax.legend()
    ax.set_xlabel('$t$/s')
    ax.set_ylabel('$T_e$/K')
    ax.grid()

    # DewPoint ---------------------------------------------------------------
    ax = fig.add_subplot(2, 2, 2)
    obs_data.DewPoint.plot(ax=ax, label='Observed')
    filt_obs.DewPoint.plot(ax=ax, label='Filtered')
    ax.fill_between(
        filt_obs.index,
        filt_obs.DewPoint - un_util.del_tdp,
        filt_obs.DewPoint + un_util.del_tdp,
        color='gray', alpha=0.2
        )
    ax.legend()
    ax.set_xlabel('$t$/s')
    ax.set_ylabel('$T_{DP}}$/K')
    ax.grid()

    # Mass -------------------------------------------------------------------
    ax = fig.add_subplot(2, 2, 3)
    obs_data.Mass.plot(ax=ax, label='Observed')
    filt_obs.Mass.plot(ax=ax, label='Filtered')
    ax.fill_between(
        filt_obs.index,
        filt_obs.Mass - un_util.del_m,
        filt_obs.Mass + un_util.del_m,
        color='gray', alpha=0.2
        )
    ax.legend()
    ax.set_xlabel('$t$/s')
    ax.set_ylabel('$m$/kg')
    ax.grid()

    # Pressure ---------------------------------------------------------------
    ax = fig.add_subplot(2, 2, 4)
    p_err = [p * un_util.pct_p for p in obs_data.Pressure]
    obs_data.Pressure.plot(ax=ax, label='Observed')
    filt_obs.Pressure.plot(ax=ax, label='Filtered')
    ax.fill_between(
        filt_obs.index,
        filt_obs.Pressure - p_err, filt_obs.Pressure + p_err,
        color='gray', alpha=0.2
        )
    ax.legend()
    ax.set_xlabel('$t$/s')
    ax.set_ylabel('$P$/Pa')
    ax.grid()

    plt.show()

    response = input('Proceed ([y]/n)? ').lower()

    if (not response) or ('y' in response):  # pragma: no cover
        return obs_data.join(avg_te)
    elif 'n' in response:
        return 'Analysis canceled.'
    else:
        return 'Unrecognized response.'


# ----------------------------------------------------------------------------
# Internal logic (locating target indexes)

def _calc_single_phi(row):
    t, del_t = row.AvgTe.nominal_value, row.AvgTe.std_dev

    phi = hap.HAPropsSI('RH', 'P', row.Pressure, 'T', t, 'Tdp', row.DewPoint)

    del_p = hap.HAPropsSI(
        'RH',
        'P', un_util.pct_p * row.Pressure,
        'T', t,
        'Tdp', row.DewPoint) - phi
    del_t = hap.HAPropsSI(
        'RH',
        'P', row.Pressure,
        'T', t + del_t,
        'Tdp', row.DewPoint) - phi
    del_tdp = hap.HAPropsSI(
        'RH',
        'P', row.Pressure,
        'T', t,
        'Tdp', row.DewPoint + un_util.del_tdp) - phi

    phi_std = math.sqrt(del_p**2 + del_t**2 + del_tdp**2)

    return (phi, phi_std)


def _calc_multi_phi(data):  # pragma: no cover
    ddata = dd.from_pandas(data, npartitions=8)

    res = ddata.map_partitions(
        lambda df: df.apply((lambda row: _calc_single_phi(row)), axis=1),
        meta=('float', 'float')
        ).compute(get=get)

    data['phi'] = res.apply(lambda x: un.ufloat(x[0], x[1]))

    return data


# ----------------------------------------------------------------------------
# Public functions


def read_tdms(filepath):
    """
    Convert tdms file to several pandas dataframes.

    Dataframes mirror the database schema and are ready to be sent to sql.

    Parameters
    ----------
    filepath : str
        filepath to the tdms file.

    Returns
    -------
    dataframes : dict of {str: pandas.DataFrame}
        Keys include `setting`, `test`, `observation` and `temp_observation`.

    Examples
    --------
    >>> dataframes = read_tdms('path')

    """
    dataframes = _tdms_2_dict_of_df(filepath)
    dataframes = _build_setting_df(dataframes)
    dataframes = _build_observation_df(dataframes)
    dataframes = _build_temp_observation_df(dataframes)
    del dataframes['data']
    return dataframes


# ----------------------------------------------------------------------------
# helpers


def _round(number, nearest):
    return nearest*round(number/nearest)
