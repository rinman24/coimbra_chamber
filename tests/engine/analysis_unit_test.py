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
    index=list(range(29750, 30251)),
    data=[
        0.098650326, 0.09865032, 0.098650314, 0.098650308, 0.098650302,
        0.098650296, 0.09865029, 0.098650284, 0.098650278, 0.098650272,
        0.098650266, 0.09865026, 0.098650254, 0.098650248, 0.098650243,
        0.098650237, 0.098650231, 0.098650225, 0.09865022, 0.098650215,
        0.098650209, 0.098650203, 0.098650198, 0.098650192, 0.098650186,
        0.09865018, 0.098650174, 0.098650168, 0.098650162, 0.098650157,
        0.098650151, 0.098650145, 0.098650139, 0.098650133, 0.098650127,
        0.098650121, 0.098650115, 0.09865011, 0.098650104, 0.098650098,
        0.098650092, 0.098650086, 0.09865008, 0.098650074, 0.098650069,
        0.098650063, 0.098650057, 0.098650051, 0.098650045, 0.09865004,
        0.098650034, 0.098650028, 0.098650021, 0.098650015, 0.098650009,
        0.098650003, 0.098649997, 0.09864999, 0.098649984, 0.098649978,
        0.098649972, 0.098649966, 0.09864996, 0.098649955, 0.098649949,
        0.098649944, 0.098649938, 0.098649933, 0.098649927, 0.098649921,
        0.098649915, 0.098649909, 0.098649903, 0.098649897, 0.098649892,
        0.098649886, 0.09864988, 0.098649874, 0.098649869, 0.098649863,
        0.098649858, 0.098649852, 0.098649847, 0.098649841, 0.098649836,
        0.09864983, 0.098649825, 0.098649819, 0.098649813, 0.098649808,
        0.098649802, 0.098649797, 0.098649791, 0.098649786, 0.09864978,
        0.098649775, 0.098649769, 0.098649763, 0.098649758, 0.098649752,
        0.098649747, 0.098649741, 0.098649735, 0.098649729, 0.098649723,
        0.098649717, 0.098649711, 0.098649705, 0.098649699, 0.098649693,
        0.098649687, 0.098649681, 0.098649675, 0.098649669, 0.098649664,
        0.098649658, 0.098649652, 0.098649646, 0.098649641, 0.098649635,
        0.098649629, 0.098649623, 0.098649618, 0.098649612, 0.098649606,
        0.0986496, 0.098649595, 0.098649589, 0.098649583, 0.098649577,
        0.098649572, 0.098649567, 0.098649562, 0.098649557, 0.098649551,
        0.098649545, 0.098649539, 0.098649533, 0.098649527, 0.09864952,
        0.098649514, 0.098649508, 0.098649502, 0.098649497, 0.098649491,
        0.098649486, 0.098649479, 0.098649473, 0.098649467, 0.098649461,
        0.098649455, 0.098649449, 0.098649443, 0.098649438, 0.098649432,
        0.098649426, 0.09864942, 0.098649415, 0.098649409, 0.098649403,
        0.098649397, 0.098649392, 0.098649386, 0.09864938, 0.098649374,
        0.098649369, 0.098649363, 0.098649357, 0.098649351, 0.098649345,
        0.098649339, 0.098649333, 0.098649327, 0.09864932, 0.098649313,
        0.098649307, 0.0986493, 0.098649293, 0.098649287, 0.09864928,
        0.098649274, 0.098649268, 0.098649262, 0.098649256, 0.09864925,
        0.098649245, 0.098649239, 0.098649233, 0.098649227, 0.098649221,
        0.098649216, 0.09864921, 0.098649204, 0.098649198, 0.098649192,
        0.098649186, 0.098649181, 0.098649175, 0.098649169, 0.098649163,
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
        0.098648575, 0.098648569, 0.098648563, 0.098648557, 0.098648551,
        0.098648545, 0.098648539, 0.098648533, 0.098648527, 0.098648521,
        0.098648515, 0.098648509, 0.098648503, 0.098648497, 0.098648492,
        0.098648486, 0.098648481, 0.098648476, 0.09864847, 0.098648464,
        0.098648458, 0.098648452, 0.098648446, 0.09864844, 0.098648434,
        0.098648428, 0.098648422, 0.098648416, 0.098648411, 0.098648405,
        0.0986484, 0.098648394, 0.098648389, 0.098648383, 0.098648377,
        0.098648371, 0.098648365, 0.098648359, 0.098648354, 0.098648348,
        0.098648343, 0.098648337, 0.098648332, 0.098648326, 0.098648321,
        0.098648315, 0.098648309, 0.098648304, 0.098648299, 0.098648293,
        0.098648288, 0.098648283, 0.098648278, 0.098648273, 0.098648268,
        0.098648262, 0.098648257, 0.098648252, 0.098648247, 0.098648242,
        0.098648236, 0.098648231, 0.098648226, 0.09864822, 0.098648215,
        0.098648209, 0.098648203, 0.098648198, 0.098648192, 0.098648186,
        0.098648181, 0.098648175, 0.098648169, 0.098648164, 0.098648158,
        0.098648153, 0.098648147, 0.098648142, 0.098648136, 0.098648129,
        0.098648123, 0.098648116, 0.09864811, 0.098648103, 0.098648097,
        0.098648091, 0.098648085, 0.098648079, 0.098648073, 0.098648067,
        0.098648061, 0.098648055, 0.098648049, 0.098648043, 0.098648037,
        0.098648031, 0.098648025, 0.098648019, 0.098648013, 0.098648007,
        0.098648001, 0.098647995, 0.098647989, 0.098647984, 0.098647978,
        0.098647972, 0.098647966, 0.09864796, 0.098647954, 0.098647948,
        0.098647942, 0.098647936, 0.098647931, 0.098647925, 0.09864792,
        0.098647914, 0.098647907, 0.098647901, 0.098647894, 0.098647888,
        0.098647881, 0.098647875, 0.098647869, 0.098647863, 0.098647857,
        0.098647851, 0.098647845, 0.098647839, 0.098647833, 0.098647827,
        0.098647821, 0.098647815, 0.098647809, 0.098647803, 0.098647797,
        0.098647791, 0.098647786, 0.09864778, 0.098647775, 0.098647769,
        0.098647764, 0.098647758, 0.098647753, 0.098647747, 0.098647741,
        0.098647735, 0.098647729, 0.098647723, 0.098647717, 0.098647711,
        0.098647705, 0.098647699, 0.098647693, 0.098647687, 0.09864768,
        0.098647674, 0.098647668, 0.098647662, 0.098647656, 0.09864765,
        0.098647644, 0.098647638, 0.098647632, 0.098647626, 0.09864762,
        0.098647615, 0.098647609, 0.098647603, 0.098647597, 0.098647591,
        0.098647585, 0.098647579, 0.098647573, 0.098647568, 0.098647562,
        0.098647557, 0.098647551, 0.098647546, 0.098647541, 0.098647536,
        0.09864753, 0.098647524, 0.098647519, 0.098647513, 0.098647507,
        0.0986475, 0.098647494, 0.098647489, 0.098647483, 0.098647477,
        0.098647471, 0.098647466, 0.09864746, 0.098647454, 0.098647448,
        0.098647442, 0.098647437, 0.098647431, 0.098647425, 0.098647419,
        0.098647413
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

def test_perform_single_chi2_fit_returns_correct_result():  # noqa: D103
    # Arrange
    correct_result = dict(
        a=0.09882587052278162,
        sig_a=9.267470252615915e-07,
        b=-5.821445616358414e-09,
        sig_b=3.089120854352089e-11,
        r2=0.9997744853277771,
        p_val=0.0,
        )

    # Act
    result = anlys_eng._perform_single_chi2_fit(_CHI2_TEST_DATA)

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
        p_val=0.0,
        )

    # Act
    result = anlys_eng._select_best_fit(_CHI2_TEST_DATA, target_idx, max_hl)

    # Assert
    for key in result.keys():
        assert math.isclose(result[key], correct_result[key], rel_tol=1e-4)


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
