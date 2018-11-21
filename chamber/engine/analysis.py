"""Analysis engine module."""

import re

import nptdms
import pandas as pd


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
# helpers


def _round(number, nearest):
    return nearest*round(number/nearest)
