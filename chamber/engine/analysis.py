"""Analysis engine module."""

import nptdms
import pandas as pd


def _get_tdms_objs_as_df(filepath):
    tdms_file = nptdms.TdmsFile(filepath)
    settings_df = tdms_file.object('Settings').as_dataframe()
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
