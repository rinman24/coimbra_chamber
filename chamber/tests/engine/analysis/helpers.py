"""Helper functions for analysis engine unit testing."""

import chamber.engine.analysis.service as anlys_eng
import chamber.tests.engine.analysis.constants as constants


def configure_input_dataframes(is_mass, duty):  # noqa: D103
    dataframes = anlys_eng._tdms_2_dict_of_df('test_path')

    dataframes['setting'].loc[0, 'IsMass'] = is_mass
    dataframes['setting'].loc[0, 'Duty'] = duty

    return dataframes


def build_correct_setting_df(is_mass, duty):  # noqa: D103
    correct_setting_df = constants.setting_obj_as_df.copy()

    correct_setting_df.loc[0, 'IsMass'] = is_mass
    correct_setting_df.loc[0, 'Duty'] = duty

    correct_setting_df['Pressure'] = 80e3

    if is_mass:
        correct_setting_df['Temperature'] = 300.0
    else:
        correct_setting_df['Temperature'] = 950.0

    return correct_setting_df


def build_correct_observation_df(is_mass, duty):  # noqa: D103
    correct_observation_df = constants.data_obj_as_df.copy()
    # This is required to match the order columns are added in production.
    # Also drops all 'TC' columns as they are not in new_col_order.
    new_col_order = [
        'CapManOk', 'DewPoint', 'Idx', 'OptidewOk', 'Pressure',
        'Mass', 'PowOut', 'PowRef'
        ]
    correct_observation_df = correct_observation_df.loc[:, new_col_order]

    if not is_mass:
        correct_observation_df.drop(columns=['Mass'], inplace=True)
    if not duty:
        correct_observation_df.drop(
             columns=['PowOut', 'PowRef'], inplace=True
             )

    return correct_observation_df
