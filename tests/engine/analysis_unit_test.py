"""Analysis engine unit test suite."""

import datetime
import unittest.mock as mock

import pandas as pd
import pytest
import pytz

import chamber.engine.analysis as anlys_eng

# ----------------------------------------------------------------------------
# globals

_SETTINGS_OBJ_AS_DF = pd.DataFrame(
    dict(
            Duty=[0.0],
            IsMass=[1.0],
            TimeStep=[1.0],
            Reservoir=[1.0],
            TubeID=[1.0],
        )
    )

_DATA_OBJ_AS_DF = pd.DataFrame(
    dict(
            TC0=[2572.301, 2572.309, 2572.316, 2572.303, 2572.297],
            TC1=[2572.301, 2572.309, 2572.316, 2572.303, 2572.297],
            TC2=[2572.301, 2572.309, 2572.316, 2572.303, 2572.297],
            TC3=[2572.301, 2572.309, 2572.316, 2572.303, 2572.297],
            TC4=[302.283, 302.285, 302.304, 302.311, 302.311],
            TC5=[300.989, 300.997, 300.998, 301.002, 300.995],
            TC6=[300.914, 300.919, 300.921, 300.920, 300.923],
            TC7=[301.237, 301.244, 301.264, 301.258, 301.256],
            TC8=[301.593, 301.603, 301.601, 301.595, 301.586],
            TC9=[300.829, 300.823, 300.835, 300.826, 300.823],
            TC10=[300.915, 300.914, 300.929, 300.914, 300.909],
            TC11=[300.753, 300.767, 300.771, 300.762, 300.753],
            TC12=[300.860, 300.863, 300.872, 300.859, 300.851],
            TC13=[301.159, 301.167, 301.168, 301.151, 301.147],
            Mass=[0.099029, 0.099029, 0.099029, 0.099029, 0.099029],
            PowRef=[
                -4.794644e-05, 7.621406e-05, -9.593868e-06, -2.524701e-05,
                -6.144859e-07
                ],
            PowOut=[-0.000211, -0.000113, -0.000118, -0.000290, -0.000297],
            DewPoint=[244.424, 244.450, 244.473, 244.476, 244.493],
            Pressure=[
                80261.060, 80282.947, 80269.815, 80261.060, 80269.815
                ],
            Idx=[12.0, 13.0, 14.0, 15.0, 16.0],
            OptidewOk=[1.0, 1.0, 1.0, 1.0, 1.0],
            CapManOk=[1.0, 1.0, 1.0, 1.0, 1.0]
            )
        )

_DATETIME = datetime.datetime(2018, 9, 5, 23, 53, 44, 570569, pytz.UTC)

_TEST_PROPS_AS_DF = pd.DataFrame(
    dict(
        Author=['me'],
        DateTime=[_DATETIME],
        Description=['test description.']
        )
    )

_BASE_OBS_COL_SET = {'CapManOk', 'DewPoint', 'Idx', 'OptidewOk', 'Pressure'}


# ----------------------------------------------------------------------------
# fixtures


@pytest.fixture
def mock_TdmsFile(monkeypatch):
    """Mock of nptdms.TdmsFile class."""
    mock_TdmsFile = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.engine.analysis.nptdms.TdmsFile', mock_TdmsFile
        )

    mock_tdms = mock_TdmsFile.return_value
    mock_tdms.object.return_value.as_dataframe.side_effect = [
        _SETTINGS_OBJ_AS_DF.copy(), _DATA_OBJ_AS_DF.copy()
        ]

    mock_tdms.object.return_value.properties.__getitem__.side_effect = [
        'me', _DATETIME, 'test description.'
        ]

    return mock_TdmsFile

# ----------------------------------------------------------------------------
# _get_tdms_objs_as_df


def test_get_tdms_objs_as_df_returns_correct_dicts(mock_TdmsFile):
    # Act
    result = anlys_eng._get_tdms_objs_as_df('test_path')

    # Assert
    pd.testing.assert_frame_equal(result['setting'], _SETTINGS_OBJ_AS_DF)
    pd.testing.assert_frame_equal(result['data'], _DATA_OBJ_AS_DF)
    pd.testing.assert_frame_equal(result['test'], _TEST_PROPS_AS_DF)

# ----------------------------------------------------------------------------
# _build_setting_df


def test_build_setting_df_with_is_mass_1(mock_TdmsFile):
    # Arrange
    correct_setting_df = _setup_correct_setting_df(
        is_mass=1.0, avg_temp=300.0, avg_pres=80e3
        )
    dataframes = _setup_dataframes(is_mass=1.0)
    tc_dropped_set = set('TC{}'.format(tc_num) for tc_num in range(0, 4))

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(
        dataframes['setting'], correct_setting_df
        )
    assert not tc_dropped_set.issubset(
        set(dataframes['data'].columns)
        )


def test_build_setting_df_with_is_mass_0(mock_TdmsFile):
    # Arrange
    correct_setting_df = _setup_correct_setting_df(
        is_mass=0.0, avg_temp=950.0, avg_pres=80e3
        )
    dataframes = _setup_dataframes(is_mass=0.0)
    correct_tc_set = set('TC{}'.format(tc_num) for tc_num in range(0, 14))

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(
        dataframes['setting'], correct_setting_df
        )
    assert correct_tc_set.issubset(
        set(dataframes['data'].columns)
        )


# ----------------------------------------------------------------------------
# _build_observation_df


def test_build_observation_df_with_mass_1_and_duty_0(mock_TdmsFile):
    # Arrange
    is_mass, duty = 1.0, 0.0
    correct_col_set, dropped_col_set = _setup_observation_sets(
        is_mass=is_mass, duty=duty
        )
    dataframes = _setup_dataframes(is_mass=is_mass, duty=duty)

    # Act
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Assert
    assert _obs_has_correct_cols(dataframes, correct_col_set)
    assert _correct_data_tables_dropped(dataframes, dropped_col_set)


def test_build_observation_df_with_mass_0_and_duty_0(mock_TdmsFile):
    # Arrange
    is_mass, duty = 0.0, 0.0
    correct_col_set, dropped_col_set = _setup_observation_sets(
        is_mass=is_mass, duty=duty
        )

    dataframes = _setup_dataframes(is_mass=is_mass, duty=duty)

    # Act
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Assert
    assert _obs_has_correct_cols(dataframes, correct_col_set)
    assert _correct_data_tables_dropped(dataframes, dropped_col_set)


def test_build_observation_df_with_mass_0_and_duty_1(mock_TdmsFile):
    # Arrange
    is_mass, duty = 0.0, 1.0
    correct_col_set, dropped_col_set = _setup_observation_sets(
        is_mass=is_mass, duty=duty
        )

    dataframes = _setup_dataframes(is_mass=is_mass, duty=duty)

    # Act
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Assert
    assert _obs_has_correct_cols(dataframes, correct_col_set)
    assert _correct_data_tables_dropped(dataframes, dropped_col_set)


def test_build_observation_df_with_mass_1_and_duty_1(mock_TdmsFile):
    # Arrange
    is_mass, duty = 1.0, 1.0
    correct_col_set, dropped_col_set = _setup_observation_sets(
        is_mass=is_mass, duty=duty
        )

    dataframes = _setup_dataframes(is_mass=is_mass, duty=duty)

    # Act
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Assert
    assert set(dataframes['observation'].columns) == correct_col_set

    assert _correct_data_tables_dropped(dataframes, dropped_col_set)


# ----------------------------------------------------------------------------
# helpers

def _setup_correct_setting_df(is_mass=None, avg_temp=None, avg_pres=None):
    correct_setting_df = _SETTINGS_OBJ_AS_DF.copy()

    correct_setting_df.loc[0, 'IsMass'] = is_mass
    correct_setting_df['Temperature'] = avg_temp
    correct_setting_df['Pressure'] = avg_pres

    return correct_setting_df


def _setup_dataframes(is_mass=None, duty=None):
    dataframes = anlys_eng._get_tdms_objs_as_df('test path')
    dataframes['setting'].loc[0, 'IsMass'] = is_mass
    if duty:
        dataframes['setting'].loc[0, 'Duty'] = duty

    return dataframes


def _setup_observation_sets(is_mass=None, duty=None):
    obs_col_set = set(_BASE_OBS_COL_SET)
    dropped_col_set = set(obs_col_set)
    dropped_col_set.add('Mass')  # Mass is dropped wither way

    if is_mass:
        obs_col_set.add('Mass')

    if duty:
        obs_col_set.add('PowOut')
        obs_col_set.add('PowRef')

        dropped_col_set.add('PowOut')
        dropped_col_set.add('PowRef')

    return obs_col_set, dropped_col_set


def _obs_has_correct_cols(dataframes, correct_col_set):
    observation_cols_set = set(dataframes['observation'].columns)
    if observation_cols_set == correct_col_set:
        return True
    return False


def _correct_data_tables_dropped(dataframes, dropped_col_set):
    data_cols_set = set(dataframes['data'].columns)
    intersection = (data_cols_set & dropped_col_set)
    if not intersection:  # No intersection: correct dropped tables
        return True
    return False
