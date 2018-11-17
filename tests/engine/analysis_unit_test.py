"""CRUD manager unit test suite."""

import unittest.mock as mock

import pandas as pd
import pytest

import chamber.engine.analysis as anlys_eng


_SETTINGS_OBJ_AS_DF = pd.DataFrame(
    dict(
            TubeID=[1.0],
            TimeStep=[1.0],
            IsMass=[1.0],
            DutyCycle=[0.0],
            Reservoir=[1.0]
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


@mock.patch("chamber.engine.analysis.nptdms.TdmsFile")
def test_get_tdms_returns_correct_dicts(mock_TdmsFile):
    mock_tdms = mock_TdmsFile.return_value
    mock_tdms.object.return_value.as_dataframe.side_effect = [
        _SETTINGS_OBJ_AS_DF, _DATA_OBJ_AS_DF
        ]

    setting_obj_as_df, data_obj_as_df = anlys_eng._get_tdms_objs('test_path')

    pd.testing.assert_frame_equal(setting_obj_as_df, _SETTINGS_OBJ_AS_DF)
    pd.testing.assert_frame_equal(data_obj_as_df, _DATA_OBJ_AS_DF)
