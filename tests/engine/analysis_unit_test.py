"""Analysis engine unit test suite."""

import datetime
import math
import pdb
import unittest.mock as mock

import pandas as pd
import pytest
import pytz
import uncertainties as un

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
        Pressure=[80261.060, 80282.947, 80269.815, 80261.060, 80269.815],
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

_CORRECT_TEMP_OBSERVATION_DF_MASS_0 = pd.DataFrame(
    data=dict(
        ThermocoupleNum=[
            0, 0, 0, 0, 0,
            1, 1, 1, 1, 1,
            2, 2, 2, 2, 2,
            3, 3, 3, 3, 3,
            4, 4, 4, 4, 4,
            5, 5, 5, 5, 5,
            6, 6, 6, 6, 6,
            7, 7, 7, 7, 7,
            8, 8, 8, 8, 8,
            9, 9, 9, 9, 9,
            10, 10, 10, 10, 10,
            11, 11, 11, 11, 11,
            12, 12, 12, 12, 12,
            13, 13, 13, 13, 13
            ],
        Temperature=[
            2572.301, 2572.309, 2572.316, 2572.303, 2572.297,
            2572.301, 2572.309, 2572.316, 2572.303, 2572.297,
            2572.301, 2572.309, 2572.316, 2572.303, 2572.297,
            2572.301, 2572.309, 2572.316, 2572.303, 2572.297,
            302.283, 302.285, 302.304, 302.311, 302.311,
            300.989, 300.997, 300.998, 301.002, 300.995,
            300.914, 300.919, 300.921, 300.920, 300.923,
            301.237, 301.244, 301.264, 301.258, 301.256,
            301.593, 301.603, 301.601, 301.595, 301.586,
            300.829, 300.823, 300.835, 300.826, 300.823,
            300.915, 300.914, 300.929, 300.914, 300.909,
            300.753, 300.767, 300.771, 300.762, 300.753,
            300.860, 300.863, 300.872, 300.859, 300.851,
            301.159, 301.167, 301.168, 301.151, 301.147
            ],
        Idx=[
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0
            ]
        )
    )

_CORRECT_TEMP_OBSERVATION_DF_MASS_1 = pd.DataFrame(
    data=dict(
        ThermocoupleNum=[
            4, 4, 4, 4, 4,
            5, 5, 5, 5, 5,
            6, 6, 6, 6, 6,
            7, 7, 7, 7, 7,
            8, 8, 8, 8, 8,
            9, 9, 9, 9, 9,
            10, 10, 10, 10, 10,
            11, 11, 11, 11, 11,
            12, 12, 12, 12, 12,
            13, 13, 13, 13, 13
            ],
        Temperature=[
            302.283, 302.285, 302.304, 302.311, 302.311,
            300.989, 300.997, 300.998, 301.002, 300.995,
            300.914, 300.919, 300.921, 300.920, 300.923,
            301.237, 301.244, 301.264, 301.258, 301.256,
            301.593, 301.603, 301.601, 301.595, 301.586,
            300.829, 300.823, 300.835, 300.826, 300.823,
            300.915, 300.914, 300.929, 300.914, 300.909,
            300.753, 300.767, 300.771, 300.762, 300.753,
            300.860, 300.863, 300.872, 300.859, 300.851,
            301.159, 301.167, 301.168, 301.151, 301.147
            ],
        Idx=[
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0,
            12.0, 13.0, 14.0, 15.0, 16.0
            ]
        )
    )

_BASE_OBS_COL_SET = {'CapManOk', 'DewPoint', 'OptidewOk', 'Pressure'}

_TEMP_DATA_QUERY = pd.DataFrame(
    dict(
        ThermocoupleNum=[
            4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
            4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
            4, 5, 6, 7, 8, 9, 10, 11, 12, 13
            ],
        Temperature=[
            302.28, 300.99, 300.91, 301.24, 301.59, 300.83, 300.92, 300.75,
            300.86, 301.16, 302.29, 301.00, 300.92, 301.24, 301.60, 300.82,
            300.91, 300.77, 300.86, 301.17, 302.30, 301.00, 300.92, 301.26,
            301.60, 300.84, 300.93, 300.77, 300.87, 301.17, 302.31, 301.00,
            300.92, 301.26, 301.60, 300.83, 300.91, 300.76, 300.86, 301.15,
            302.31, 301.00, 300.92, 301.26, 301.59, 300.82, 300.91, 300.75,
            300.85, 301.15
            ],
        Idx=[
            12, 12, 12, 12, 12, 12, 12, 12, 12, 12,
            13, 13, 13, 13, 13, 13, 13, 13, 13, 13,
            14, 14, 14, 14, 14, 14, 14, 14, 14, 14,
            15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
            16, 16, 16, 16, 16, 16, 16, 16, 16, 16
            ]
        )
    )
_CORRECT_AVERAGE_TEMP_UNCERTAINTIES = pd.DataFrame(
    data=dict(
        AvgTe=[
            un.ufloat(301.153, 0.4668106920607228),
            un.ufloat(301.158, 0.46908421418760887),
            un.ufloat(301.166, 0.4687619628103208),
            un.ufloat(301.16, 0.4750204673952965),
            un.ufloat(301.15600000000006, 0.4764265129295566),
            ]
        ),
    index=[12, 13, 14, 15, 16]
    )
_CORRECT_AVERAGE_TEMP_UNCERTAINTIES.index.name = 'Idx'

_PHI_TESTING_DF = pd.DataFrame(
        data=[
            un.ufloat(0.06, 0.01), un.ufloat(0.12, 0.01),
            un.ufloat(0.18, 0.01), un.ufloat(0.24, 0.01),
            un.ufloat(0.30, 0.01), un.ufloat(0.36, 0.01),
            un.ufloat(0.42, 0.01), un.ufloat(0.48, 0.01),
            un.ufloat(0.54, 0.01), un.ufloat(0.60, 0.01),
            un.ufloat(0.66, 0.01), un.ufloat(0.72, 0.01)
            ],
        index=[12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
        columns=['phi']
        )

_CHI2_TEST_DATA = pd.DataFrame(
    index=list(range(29950, 30051)),
    data=[
        0.098649157, 0.098649152, 0.098649146, 0.09864914, 0.098649134,
        0.098649129, 0.098649123, 0.098649118, 0.098649112, 0.098649107,
        0.098649101, 0.098649095, 0.09864909, 0.098649084, 0.098649078,
        0.098649073, 0.098649067, 0.098649061, 0.098649056, 0.09864905,
        0.098649045, 0.098649039, 0.098649034, 0.098649028, 0.098649023,
        0.098649017, 0.098649011, 0.098649005, 0.098648999, 0.098648994,
        0.098648989, 0.098648983, 0.098648978, 0.098648972, 0.098648966,
        0.09864896, 0.098648953, 0.098648947, 0.09864894, 0.098648934,
        0.098648928, 0.098648922, 0.098648916, 0.09864891, 0.098648903,
        0.098648897, 0.098648891, 0.098648884, 0.098648878, 0.098648872,
        0.098648865, 0.098648859, 0.098648852, 0.098648846, 0.09864884,
        0.098648834, 0.098648828, 0.098648822, 0.098648816, 0.09864881,
        0.098648804, 0.098648799, 0.098648793, 0.098648787, 0.098648782,
        0.098648776, 0.09864877, 0.098648764, 0.098648758, 0.098648752,
        0.098648745, 0.098648739, 0.098648733, 0.098648728, 0.098648722,
        0.098648716, 0.098648711, 0.098648705, 0.098648699, 0.098648694,
        0.098648688, 0.098648682, 0.098648677, 0.098648671, 0.098648665,
        0.09864866, 0.098648654, 0.098648649, 0.098648644, 0.098648638,
        0.098648632, 0.098648626, 0.09864862, 0.098648614, 0.098648608,
        0.098648602, 0.098648597, 0.098648591, 0.098648586, 0.09864858,
        0.098648575
        ],
    columns=['Mass']
    )


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


def test_get_tdms_objs_as_df_returns_correct_dicts(mock_TdmsFile):  # noqa: D103
    # Act
    dataframes = anlys_eng._tdms_2_dict_of_df('test_path')

    # Assert
    pd.testing.assert_frame_equal(dataframes['setting'], _SETTINGS_OBJ_AS_DF)
    pd.testing.assert_frame_equal(dataframes['data'], _DATA_OBJ_AS_DF)
    pd.testing.assert_frame_equal(dataframes['test'], _TEST_PROPS_AS_DF)

# ----------------------------------------------------------------------------
# _build_setting_df


@pytest.mark.parametrize('duty', [0, 1])
@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_setting_df_returns_correct_df(duty, is_mass, mock_TdmsFile):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=duty, is_mass=is_mass)
    correct_setting_df = _build_correct_setting_df(duty=duty, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(dataframes['setting'], correct_setting_df)


@pytest.mark.parametrize('duty', [0, 1])
def test_build_setting_drops_mass_from_data_when_ismass_0(duty, mock_TdmsFile):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=duty, is_mass=0)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    assert 'Mass' not in set(dataframes['data'].columns)


@pytest.mark.parametrize('duty', [0, 1])
def test_build_setting_keeps_mass_in_data_when_ismass_1(duty, mock_TdmsFile):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=duty, is_mass=1)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    assert 'Mass' in set(dataframes['data'].columns)


@pytest.mark.parametrize('duty', [0, 1])
def test_build_setting_drops_tcs_0_to_3_when_ismass_1(duty, mock_TdmsFile):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=duty, is_mass=1)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    assert not {'TC0', 'TC1', 'TC2', 'TC3'}.issubset(
        set(dataframes['data'].columns)
        )


@pytest.mark.parametrize('duty', [0, 1])
def test_build_setting_keeps_tcs_0_to_3_when_ismass_0(duty, mock_TdmsFile):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=duty, is_mass=0)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    assert {'TC0', 'TC1', 'TC2', 'TC3'}.issubset(
        set(dataframes['data'].columns)
        )


@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_setting_drops_powout_powref_from_data_when_duty_is_0(
        is_mass, mock_TdmsFile
        ):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=0, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    assert not {'PowOut', 'PowRef'}.issubset(set(dataframes['data'].columns))


@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_setting_keeps_powout_powref_in_data_when_duty_is_1(
        is_mass, mock_TdmsFile
        ):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=1, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_setting_df(dataframes)

    # Assert
    assert {'PowOut', 'PowRef'}.issubset(set(dataframes['data'].columns))


# ----------------------------------------------------------------------------
# _build_observation_df


@pytest.mark.parametrize('duty', [0, 1])
@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_observation_df_returns_correct_df(duty, is_mass, mock_TdmsFile):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=duty, is_mass=is_mass)
    correct_observation_df = _build_correct_observation_df(
        duty=duty, is_mass=is_mass
        )

    # Act
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(
        dataframes['observation'], correct_observation_df
        )


@pytest.mark.parametrize('duty', [0, 1])
@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_observation_removes_keys_from_data(
        duty, is_mass, mock_TdmsFile
        ):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(duty=duty, is_mass=is_mass)

    # Act
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Assert
    assert not (
        set(dataframes['observation'].columns)
        & set(dataframes['data'].columns)
        )


# ----------------------------------------------------------------------------
# _build_temp_observation_df


@pytest.mark.parametrize('duty', [0, 1])
def test_build_temp_observation_with_is_mass_1(duty, mock_TdmsFile):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(is_mass=1, duty=duty)
    dataframes = anlys_eng._build_setting_df(dataframes)
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Act
    dataframes = anlys_eng._build_temp_observation_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(
        dataframes['temp_observation'], _CORRECT_TEMP_OBSERVATION_DF_MASS_1
        )


@pytest.mark.parametrize('duty', [0, 1])
def test_build_temp_observation_with_is_mass_0(duty, mock_TdmsFile):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(is_mass=0, duty=duty)
    dataframes = anlys_eng._build_setting_df(dataframes)
    dataframes = anlys_eng._build_observation_df(dataframes)

    # Act
    dataframes = anlys_eng._build_temp_observation_df(dataframes)

    # Assert
    pd.testing.assert_frame_equal(
        dataframes['temp_observation'], _CORRECT_TEMP_OBSERVATION_DF_MASS_0
        )


@pytest.mark.parametrize('duty', [0, 1])
@pytest.mark.parametrize('is_mass', [0, 1])
def test_build_temp_observation_drops_data_columns(
        duty, is_mass, mock_TdmsFile
        ):  # noqa: D103
    # Arrange
    dataframes = _configure_input_dataframes(is_mass=is_mass, duty=duty)
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
    temp_data = _TEMP_DATA_QUERY.pivot(
        index='Idx', columns='ThermocoupleNum', values='Temperature'
        )

    # Act
    avg_te = anlys_eng._calc_avg_te(temp_data)

    # Assert
    for i in avg_te.index:
        assert math.isclose(
            avg_te.loc[i, 'AvgTe'].nominal_value,
            _CORRECT_AVERAGE_TEMP_UNCERTAINTIES.loc[i, 'AvgTe'].nominal_value
            )
        assert math.isclose(
            avg_te.loc[i, 'AvgTe'].std_dev,
            _CORRECT_AVERAGE_TEMP_UNCERTAINTIES.loc[i, 'AvgTe'].std_dev
            )


# ----------------------------------------------------------------------------
# _filter_observations


def test_filter_observations_has_correct_call_stack(monkeypatch):  # noqa: D103
    # Arrange
    mock_df = mock.MagicMock()

    mock_signal = mock.MagicMock()
    monkeypatch.setattr('chamber.engine.analysis.signal', mock_signal)
    savgol_calls = [
        mock.call(mock_df.copy().DewPoint, 1801, 2),
        mock.call(mock_df.copy().Mass, 301, 2),
        mock.call(mock_df.copy().Pressure, 3601, 1)
        ]

    mock_pd = mock.MagicMock()
    monkeypatch.setattr('chamber.engine.analysis.pd', mock_pd)

    # Act
    anlys_eng._filter_observations(mock_df)

    # Assert
    mock_signal.savgol_filter.assert_has_calls(savgol_calls)


# ----------------------------------------------------------------------------
# _preprocess_observations


@pytest.mark.parametrize(
    'user_input, expected',
    [
        ('n', 'Analysis canceled.'),
        ('foobar', 'Unrecognized response.')
        ]
    )
def test_preprocess_observations_returns_correct_result_when_not_y(
        user_input, expected, monkeypatch
        ):  # noqa: D103
    # Arrange
    mock_input = mock.MagicMock()
    monkeypatch.setattr('builtins.input', mock_input)
    mock_input.return_value = user_input

    mock_plt = mock.MagicMock()
    monkeypatch.setattr('chamber.engine.analysis.plt', mock_plt)

    _calc_avg_te = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.engine.analysis._calc_avg_te', _calc_avg_te
        )

    _filter_observations = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.engine.analysis._filter_observations', _filter_observations
        )

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
        [dp, 'mass', p, t], index=['DewPoint', 'Mass', 'Pressure', 'AvgTe']
        )

    # Act
    rh, rh_std = anlys_eng._calc_single_phi(row)

    # Assert
    assert math.isclose(rh, correct_rh, rel_tol=1e-3)
    assert math.isclose(rh_std, correct_rh_std, rel_tol=1e-2)


# ----------------------------------------------------------------------------
# _get_valid_phi_targets


def test_get_valid_phi_targets():  # noqa: D103
    # Arrange
    correct_targets = [
        0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7
        ]

    # Act
    result = anlys_eng._get_valid_phi_targets(_PHI_TESTING_DF)

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
    result = anlys_eng._get_valid_phi_indexes(_PHI_TESTING_DF)

    # Assert
    assert result == correct_result


# ----------------------------------------------------------------------------
# _get_max_window_lengths


def test_get_max_window_lengths():  # noqa: D103
    # Arrange
    indexes = anlys_eng._get_valid_phi_indexes(_PHI_TESTING_DF)
    max_half_lengths = [1, 2, 3, 4, 5, 5, 5, 4, 3, 2, 1, 1, 0]
    for idx, _dict in enumerate(indexes):
        _dict.update({'max_hl': max_half_lengths[idx]})
    correct_result = indexes

    # Act
    result = anlys_eng._get_max_window_lengths(_PHI_TESTING_DF)

    # Assert
    assert result == correct_result


# ----------------------------------------------------------------------------
# _perform_single_chi2

def test_perform_single_chi2_fit():  # noqa: D103
    # Arrange
    correct_result = dict(
        a=0.09882587052278162,
        sig_a=1.0238853052090132e-05,
        b=-5.90014009179836e-09,
        sig_b=3.4129494056932055e-10,
        r2=0.9997744853277771,
        p_val=2.98315986172661e-137,
        )

    # Act
    result = anlys_eng._perform_single_chi2_fit(_CHI2_TEST_DATA)

    # Assert
    assert result == correct_result


# ----------------------------------------------------------------------------
# read_tdms


def test_call_read_tdms_returns_correct_dfs(mock_TdmsFile):  # noqa: D103
    # Arrange
    duty, is_mass = 0, 1
    correct_setting_df = _build_correct_setting_df(duty=duty, is_mass=is_mass)
    correct_observation_df = _build_correct_observation_df(
        duty=duty, is_mass=is_mass
        )

    # Act
    dataframes = anlys_eng.read_tdms('test_path')

    # Assert
    assert 'data' not in dataframes.keys()
    pd.testing.assert_frame_equal(dataframes['setting'], correct_setting_df)
    pd.testing.assert_frame_equal(dataframes['test'], _TEST_PROPS_AS_DF)
    pd.testing.assert_frame_equal(
        dataframes['observation'], correct_observation_df
        )
    pd.testing.assert_frame_equal(
        dataframes['temp_observation'], _CORRECT_TEMP_OBSERVATION_DF_MASS_1
        )


# ----------------------------------------------------------------------------
# helpers


def _configure_input_dataframes(is_mass, duty):
    dataframes = anlys_eng._tdms_2_dict_of_df('test_path')

    dataframes['setting'].loc[0, 'IsMass'] = is_mass
    dataframes['setting'].loc[0, 'Duty'] = duty

    return dataframes


def _build_correct_setting_df(is_mass, duty):
    correct_setting_df = _SETTINGS_OBJ_AS_DF.copy()

    correct_setting_df.loc[0, 'IsMass'] = is_mass
    correct_setting_df.loc[0, 'Duty'] = duty

    correct_setting_df['Pressure'] = 80e3

    if is_mass:
        correct_setting_df['Temperature'] = 300.0
    else:
        correct_setting_df['Temperature'] = 950.0

    return correct_setting_df


def _build_correct_observation_df(is_mass, duty):
    correct_observation_df = _DATA_OBJ_AS_DF.copy()
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
