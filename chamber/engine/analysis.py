"""Analysis engine module."""

import nptdms
import pandas as pd


def _get_tdms_objs_as_df(filepath):
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
    >>> dataframes = tdms_2_dict_of_df('path')

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

    Use `data` dataframe to calculate averave values of temperature and
    pressure over the course of the experiment. Average temperature and
    pressure are then rounded to the nearest 5 K and 5000 Pa, respectively.

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
    >>> dataframes = _get_tdms_objs_as_df(filepath)
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
    Add columns to observation and drop columns from data.

    In order to manage resources, when a columns is moved to
    `dataframes['observation'] is is immediately dropped from
    `databases['data']`.

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
    >>> dataframes = _get_tdms_objs_as_df(filepath)
    >>> dataframes = _build_setting_df(dataframes)
    >>> dataframes = _build_observation_df(dataframes)

    """
    columns_to_move = ['CapManOk', 'DewPoint', 'OptidewOk', 'Pressure']

    if dataframes['setting'].loc[0, 'IsMass']:
        columns_to_move.append('Mass')
    else:
        dataframes['data'].drop(columns=['Mass'], inplace=True)

    if dataframes['setting'].loc[0, 'Duty']:
        columns_to_move += ['PowRef', 'PowOut']
    else:
        dataframes['data'].drop(columns=['PowOut', 'PowRef'], inplace=True)

    dataframes['observation'] = dataframes['data'][columns_to_move].copy()
    dataframes['data'].drop(columns=columns_to_move, inplace=True)

    return dataframes


def _build_temp_observation_df(dataframes):
    """
    Reformat data table to temp observation format.

    Pivot remaining tc columns in `data` to the format required by database.

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
    >>> dataframes = _get_tdms_objs_as_df(filepath)
    >>> dataframes = _build_setting_df(dataframes)
    >>> dataframes = _build_observation_df(dataframes)
    >>> dataframes = _build_temp_observation_df(dataframes)

    """
    tc_num, temp, idx = [], [], []
    elements = len(dataframes['data'].index)

    initial_tc = 0

    if dataframes['setting'].loc[0, 'IsMass']:
        initial_tc = 4

    for tc in range(initial_tc, 14):
        tc_num += [tc]*elements

        col = 'TC{}'.format(tc)
        temp += list(dataframes['data'].loc[:, col])
        dataframes['data'].drop(columns=[col], inplace=True)

        idx += list(dataframes['data'].loc[:, 'Idx'])

    dataframes['observation'].loc[:, 'Idx'] = dataframes['data'].loc[:, 'Idx']
    dataframes['data'].drop(columns=['Idx'], inplace=True)

    dataframes['temp_observation'] = pd.DataFrame(
        dict(
            ThermocoupleNum=tc_num,
            Temperature=temp,
            Idx=idx
            )
        )

    return dataframes


def read_tdms(filepath):
    dataframes = _get_tdms_objs_as_df(filepath)
    dataframes = _build_setting_df(dataframes)
    # dataframes = _build_observation_df(dataframes)
    # dataframes = _build_temp_observation_df(dataframes)
    return dataframes


# ----------------------------------------------------------------------------
# helpers


def _round(number, nearest):
    return nearest*round(number/nearest)
