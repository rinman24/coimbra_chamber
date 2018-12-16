"""Fixtures used for analysis engine unit testing."""

import unittest.mock as mock

import pytest

import chamber.tests.engine.analysis.resources.constants as constants

@pytest.fixture
def mock_TdmsFile(monkeypatch):
    """Mock of nptdms.TdmsFile class."""
    mock_TdmsFile = mock.MagicMock()
    monkeypatch.setattr(
        'chamber.engine.analysis.service.nptdms.TdmsFile', mock_TdmsFile
        )

    mock_tdms = mock_TdmsFile.return_value
    mock_tdms.object.return_value.as_dataframe.side_effect = [
        constants.setting_obj_as_df.copy(), constants.data_obj_as_df.copy()
        ]

    mock_tdms.object.return_value.properties.__getitem__.side_effect = [
        'me', constants.datetime, 'test description.'
        ]

    return mock_TdmsFile
