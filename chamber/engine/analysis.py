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
        Keys include `settings`, `data`, and `test`.

    Examples
    --------
    >>> dataframes = tdms_2_dict_of_df('path')

    """
    tdms_file = nptdms.TdmsFile(filepath)
    settings_df = tdms_file.object('Settings').as_dataframe()
    settings_df.rename(columns={'DutyCycle': 'Duty'})
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


def _build_setting_df(setting_df, data_df):
    """
    Add `Temperature` and `Pressure` keys to `setting_df`.

    Use `data_df` to calculate averave values of temperature and pressure
    over the course of the experiment. Average temperature and pressure
    are then rounded to the nearest 5 K and 5000 Pa, respectively.

    Parameters
    ----------
    setting_df : dict of {str: list of numpy.float64}
    data_df : dict of {str: list of numpy.fload64}

    Returns
    -------
    pandas.DataFrame
        Updated setting_df

    Examples
    --------
    >>> dataframes = _get_tdms_objs_as_df(filepath)
    >>> setting_df = dataframes['settings']
    >>> data_df = dataframes['data']
    >>> setting_df = _build_setting_df(setting_df, data_df)

    """
    if setting_df.loc[0, 'IsMass'] == 1.0:
            tc_numbers = range(4, 14)
    else:
            tc_numbers = range(0, 14)

    tc_cols = ['TC{}'.format(num) for num in tc_numbers]

    avg_temp = data_df.loc[:, tc_cols].mean().mean()
    avg_pressure = data_df.loc[:, 'Pressure'].mean()

    rounded_temp = 5*round(avg_temp/5)
    rounded_pressure = 5000*round(avg_pressure/5000)

    setting_df.loc[0, 'Temperature'] = rounded_temp
    setting_df.loc[0, 'Pressure'] = rounded_pressure

    return setting_df
