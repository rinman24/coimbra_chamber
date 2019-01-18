"""Analysis engine unit test suite."""

import math
import pdb
import unittest.mock as mock

import pandas as pd
import pytest
import uncertainties as un

import chamber.engine.analysis.service as anlys_eng
import chamber.tests.engine.analysis.constants as const


# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture
def tdms_file(monkeypatch):
    """Mock of nptdms.TdmsFile class."""
    mock_TdmsFile = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.engine.analysis.service.nptdms.TdmsFile', mock_TdmsFile)

    mock_tdms = mock_TdmsFile.return_value
    mock_tdms.object.return_value.as_dataframe.side_effect = [
        const.setting_obj_as_df.copy(), const.data_obj_as_df.copy()]

    mock_tdms.object.return_value.properties.__getitem__.side_effect = [
        'me', const.datetime, 'test description.']

    return mock_TdmsFile


# ----------------------------------------------------------------------------
# _get_tdms_objs_as_df


def test_get_tdms_objs_as_df_returns_correct_dicts(tdms_file):  # noqa: D103
    # Act
    dataframes = anlys_eng._tdms_2_dict_of_df('test_path')

    # Assert
    setting = dataframes['setting']
    data = dataframes['data']
    test = dataframes['test']

    pd.testing.assert_frame_equal(setting, const.setting_obj_as_df)
    pd.testing.assert_frame_equal(data, const.data_obj_as_df)
    pd.testing.assert_frame_equal(test, const.test_props_as_df)

# ----------------------------------------------------------------------------
# _build_setting_df


@pytest.mark.parametrize('duty', [0, 1])
@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_setting_df_returns_correct_df(duty, is_mass, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=duty, is_mass=is_mass)
    correct_setting_df = build_correct_setting_df(duty=duty, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(dataframes['setting'], correct_setting_df)


@pytest.mark.parametrize('duty', [0, 1])
def test_build_setting_drops_mass_from_data_when_ismass_0(duty, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=duty, is_mass=0)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    assert 'Mass' not in set(dataframes['data'].columns)


@pytest.mark.parametrize('duty', [0, 1])
def test_build_setting_keeps_mass_in_data_when_ismass_1(duty, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=duty, is_mass=1)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    assert 'Mass' in set(dataframes['data'].columns)


@pytest.mark.parametrize('duty', [0, 1])
def test_build_setting_drops_tcs_0_to_3_when_ismass_1(duty, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=duty, is_mass=1)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    data_col_set = set(dataframes['data'].columns)
    assert not const.tube_tc_set.issubset(data_col_set)


@pytest.mark.parametrize('duty', [0, 1])
def test_build_setting_keeps_tcs_0_to_3_when_ismass_0(duty, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=duty, is_mass=0)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    data_col_set = set(dataframes['data'].columns)
    assert const.tube_tc_set.issubset(data_col_set)


@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_setting_drops_powout_powref_from_data_when_duty_is_0(is_mass, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=0, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    data_col_set = set(dataframes['data'].columns)
    assert not const.c20_pow_set.issubset(data_col_set)


@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_setting_keeps_powout_powref_in_data_when_duty_is_1(is_mass, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=1, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    data_col_set = set(dataframes['data'].columns)
    assert const.c20_pow_set.issubset(data_col_set)


# ----------------------------------------------------------------------------
# _build_observation_df


@pytest.mark.parametrize('duty', [0, 1])
@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_observation_df_returns_correct_df(duty, is_mass, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=duty, is_mass=is_mass)
    correct_observation_df = build_correct_observation_df(duty=duty, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(
        dataframes['observation'], correct_observation_df
        )


@pytest.mark.parametrize('duty', [0, 1])
@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_observation_removes_keys_from_data(duty, is_mass, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(duty=duty, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Assert
    obs_col_set = set(dataframes['observation'].columns)
    data_col_set = set(dataframes['data'].columns)
    assert not (obs_col_set & data_col_set)


# ----------------------------------------------------------------------------
# _build_temp_observation_df


@pytest.mark.parametrize('duty', [0, 1])
def test_build_temp_observation_with_is_mass_1(duty, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(is_mass=1, duty=duty)
    dataframes = anlys_eng._build_setting_df(dataframes)
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Act
    dataframes = anlys_eng._build_temp_observation_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(
        dataframes['temp_observation'],
        const.correct_temp_observation_df_mass_1)


@pytest.mark.parametrize('duty', [0, 1])
def test_build_temp_observation_with_is_mass_0(duty, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(is_mass=0, duty=duty)
    dataframes = anlys_eng._build_setting_df(dataframes)
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Act
    dataframes = anlys_eng._build_temp_observation_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(
        dataframes['temp_observation'],
        const.correct_temp_observation_df_mass_0)


@pytest.mark.parametrize('duty', [0, 1])
@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_temp_observation_drops_data_columns(duty, is_mass, tdms_file):  # noqa: D103
    # Arrange
    dataframes = configure_input_dataframes(is_mass=is_mass, duty=duty)
    dataframes = anlys_eng._build_setting_df(dataframes)
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Act
    dataframes = anlys_eng._build_temp_observation_df(dataframes)

    # Assert
    assert dataframes['data'].empty


# ----------------------------------------------------------------------------
# _calc_avg_te

def test_calc_avg_te_returns_correct_df():  # noqa: D103
    # Arrange
    temp_data = const.temp_data_query.pivot(
        index='Idx', columns='ThermocoupleNum', values='Temperature')

    # Act
    avg_te = anlys_eng._calc_avg_te(temp_data)

    # Assert
    for i in avg_te.index:
        assert math.isclose(
            avg_te.loc[i, 'AvgTe'].nominal_value,
            const.correct_average_temp_uncertainties.loc[i, 'AvgTe'].nominal_value)
        assert math.isclose(
            avg_te.loc[i, 'AvgTe'].std_dev,
            const.correct_average_temp_uncertainties.loc[i, 'AvgTe'].std_dev)


# ----------------------------------------------------------------------------
# _filter_observations


def test_filter_observations_has_correct_call_stack(monkeypatch):  # noqa: D103
    # Arrange
    mock_df = mock.MagicMock()

    mock_signal = mock.MagicMock()
    monkeypatch.setattr('chamber.engine.analysis.service.signal', mock_signal)
    savgol_calls = [
        mock.call(mock_df.copy().DewPoint, 1801, 2),
        mock.call(mock_df.copy().Mass, 301, 2),
        mock.call(mock_df.copy().Pressure, 3601, 1)]

    mock_pd = mock.MagicMock()
    monkeypatch.setattr('chamber.engine.analysis.service.pd', mock_pd)

    # Act
    anlys_eng._filter_observations(mock_df)

    # Assert
    mock_signal.savgol_filter.assert_has_calls(savgol_calls)


# ----------------------------------------------------------------------------
# _preprocess_observations


@pytest.mark.parametrize(
    'user_input, expected',
    [('n', 'Analysis canceled.'), ('foobar', 'Unrecognized response.')])
def test_preprocess_observations_returns_correct_result_when_not_y(
        user_input, expected, monkeypatch
        ):  # noqa: D103
    # Arrange
    mock_input = mock.MagicMock()
    monkeypatch.setattr('builtins.input', mock_input)
    mock_input.return_value = user_input

    mock_plt = mock.MagicMock()
    monkeypatch.setattr('chamber.engine.analysis.service.plt', mock_plt)

    _calc_avg_te = mock.MagicMock()
    monkeypatch.setattr('chamber.engine.analysis.service._calc_avg_te', _calc_avg_te)

    _filter_observations = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.engine.analysis.service._filter_observations',
        _filter_observations)

    temp_data = mock.MagicMock()
    obs_data = mock.MagicMock()

    # Act
    result = anlys_eng._preprocess_observations(obs_data, temp_data)

    # Assert
    assert (result == expected)


# ----------------------------------------------------------------------------
# _calc_rh


def test_calc_single_phi_returns_correct_result():  # noqa: D103
    # Arrange
    correct_rh = 0.517
    correct_rh_std = 0.0087

    p, t, dp = 1e5, un.ufloat(290, 0.15), 280
    row = pd.Series(
        [dp, 'mass', p, t], index=['DewPoint', 'Mass', 'Pressure', 'AvgTe'])

    # Act
    rh, rh_std = anlys_eng._calc_single_phi(row)

    # Assert
    assert math.isclose(rh, correct_rh, rel_tol=1e-3)
    assert math.isclose(rh_std, correct_rh_std, rel_tol=1e-2)


# ----------------------------------------------------------------------------
# _get_valid_phi_targets


def test_get_valid_phi_targets():  # noqa: D103
    # Arrange
    correct_targets = [x/100 for x in range(10, 70+1, 5)]

    # Act
    result = anlys_eng._get_valid_phi_targets(const.phi_testing_df)

    # Assert
    assert result == correct_targets


# ----------------------------------------------------------------------------
# _get_phi_target_indexes


def test_get_valid_phi_indexes():  # noqa: D103
    # Arrange
    correct_result = [
        dict(target=0.1, idx=13), dict(target=0.15, idx=14),
        dict(target=0.2, idx=15), dict(target=0.25, idx=16),
        dict(target=0.3, idx=17), dict(target=0.35, idx=17),
        dict(target=0.4, idx=18), dict(target=0.45, idx=19),
        dict(target=0.5, idx=20), dict(target=0.55, idx=21),
        dict(target=0.6, idx=22), dict(target=0.65, idx=22),
        dict(target=0.7, idx=23)
        ]

    # Act
    result = anlys_eng._get_valid_phi_indexes(const.phi_testing_df)

    # Assert
    assert result == correct_result


# ----------------------------------------------------------------------------
# _get_max_window_lengths


def test_get_max_window_lengths():  # noqa: D103
    # Arrange
    indexes = anlys_eng._get_valid_phi_indexes(const.phi_testing_df)
    max_half_lengths = [1, 2, 3, 4, 5, 5, 5, 4, 3, 2, 1, 1, 0]
    for idx, _dict in enumerate(indexes):
        _dict.update({'max_hl': max_half_lengths[idx]})
    correct_result = indexes

    # Act
    result = anlys_eng._get_max_window_lengths(const.phi_testing_df)

    # Assert
    assert result == correct_result


# ----------------------------------------------------------------------------
# _perform_single_chi2

def test_perform_single_chi2_fit_returns_correct_result():  # noqa: D103
    # Arrange
    correct_result = dict(
        a=0.09882587052278162,
        sig_a=9.267470252615915e-07,
        b=-5.821445616358414e-09,
        sig_b=3.089120854352089e-11,
        r2=0.9997744853277771,
        p_val=0.0)

    # Act
    result = anlys_eng._perform_single_chi2_fit(const.chi2_test_data)

    # Assert
    for key in result.keys():
        assert math.isclose(result[key], correct_result[key], rel_tol=1e-3)


# -----------------------------------------------------------------------------
# _select_best_fit


def test_select_best_fit_returns_correct_result():  # noqa: D103
    # Arrange
    target_idx = 30000
    max_hl = 250
    correct_result = dict(
        a=0.09882345459664288,
        sig_a=1.7414949252793581e-06,
        b=-5.819486165995094e-09,
        sig_b=5.804953995067947e-11,
        r2=0.9999238006300767,
        p_val=0.0)

    # Act
    result = anlys_eng._select_best_fit(
        const.chi2_test_data, target_idx, max_hl)

    # Assert
    for key in result.keys():
        assert math.isclose(result[key], correct_result[key], rel_tol=1e-6)


def test_select_best_fit_returns_resunt_none_when_no_fit_is_found():  # noqa: D103
    # Arrange
    target_idx = 30000
    max_hl = 2  # This is what causes the test to return None.
    correct_result = None

    # Act
    result = anlys_eng._select_best_fit(
        const.chi2_test_data, target_idx, max_hl)

    # Assert
    assert result is correct_result

# ----------------------------------------------------------------------------
# read_tdms


def test_call_read_tdms_returns_correct_dfs(tdms_file):  # noqa: D103
    # Arrange
    duty, is_mass = 0, 1
    correct_setting_df = build_correct_setting_df(
        duty=duty, is_mass=is_mass)
    correct_observation_df = build_correct_observation_df(
        duty=duty, is_mass=is_mass)

    # Act
    dataframes = anlys_eng.read_tdms('test_path')

    # Assert
    setting = dataframes['setting']
    test = dataframes['test']
    observation = dataframes['observation']
    temp_obs = dataframes['temp_observation']

    assert 'data' not in dataframes.keys()
    pd.testing.assert_frame_equal(setting, correct_setting_df)
    pd.testing.assert_frame_equal(test, const.test_props_as_df)
    pd.testing.assert_frame_equal(observation, correct_observation_df)
    pd.testing.assert_frame_equal(temp_obs, const.correct_temp_observation_df_mass_1)


# ----------------------------------------------------------------------------
# Helpers


def configure_input_dataframes(is_mass, duty):  # noqa: D103
    dataframes = anlys_eng._tdms_2_dict_of_df('test_path')

    dataframes['setting'].loc[0, 'IsMass'] = is_mass
    dataframes['setting'].loc[0, 'Duty'] = duty

    return dataframes


def build_correct_setting_df(is_mass, duty):  # noqa: D103
    correct_setting_df = const.setting_obj_as_df.copy()

    correct_setting_df.loc[0, 'IsMass'] = is_mass
    correct_setting_df.loc[0, 'Duty'] = duty

    correct_setting_df['Pressure'] = 80e3

    if is_mass:
        correct_setting_df['Temperature'] = 300.0
    else:
        correct_setting_df['Temperature'] = 950.0

    return correct_setting_df


def build_correct_observation_df(is_mass, duty):  # noqa: D103
    correct_observation_df = const.data_obj_as_df.copy()
    # This is required to match the order columns are added in production.
    # Also drops all 'TC' columns as they are not in new_col_order.
    new_col_order = [
        'CapManOk', 'DewPoint', 'Idx', 'OptidewOk', 'Pressure',
        'Mass', 'PowOut', 'PowRef']
    correct_observation_df = correct_observation_df.loc[:, new_col_order]

    if not is_mass:
        correct_observation_df.drop(columns=['Mass'], inplace=True)
    if not duty:
        correct_observation_df.drop(columns=['PowOut', 'PowRef'], inplace=True)

    return correct_observation_df
