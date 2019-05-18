"""Integration test suite for TdmsAccess."""

from decimal import Decimal
from pathlib import Path

import pytest
from nptdms import TdmsFile
from pandas import DataFrame

from chamber.access.tdms.service import TdmsAccess
from chamber.access.sql.contracts import TemperatureSpec


# Module level globals -------------------------------------------------------


PATH_1 = Path('chamber/tests/access/tdms/resources/test_1.tdms')
PATH_2 = Path('chamber/tests/access/tdms/resources/test_2.tdms')


# TdmsAccess -----------------------------------------------------------------


@pytest.mark.parametrize('filepath', [PATH_1, PATH_2, 'bad_path'])
def test_connect(tdms_access, filepath):  # noqa: D103
    # Act --------------------------------------------------------------------
    tdms_access.connect(filepath)
    # Assert -----------------------------------------------------------------
    if filepath:
        assert isinstance(tdms_access._tdms_file, TdmsFile)
        assert isinstance(tdms_access._settings, DataFrame)
        assert isinstance(tdms_access._data, DataFrame)
    else:
        assert not hasattr(tdms_access._tdms_file)


@pytest.mark.parametrize('index', [0, 1, 2])
def test_get_temperature_spec(tdms_access, index):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    path = PATH_1
    tdms_access.connect(path)
    # Act --------------------------------------------------------------------
    results = tdms_access._get_temperature_specs(index)
    # Assert -----------------------------------------------------------------
    for temp_spec in results:
        assert isinstance(temp_spec, TemperatureSpec)
        tc_num = temp_spec.thermocouple_num
        if index == 0:
            if tc_num == 4:
                assert temp_spec.temperature == Decimal('296.58')
            if tc_num == 5:
                assert temp_spec.temperature == Decimal('297.33')
            if tc_num == 6:
                assert temp_spec.temperature == Decimal('297.08')
            if tc_num == 7:
                assert temp_spec.temperature == Decimal('296.46')
            if tc_num == 8:
                assert temp_spec.temperature == Decimal('297.08')
            if tc_num == 9:
                assert temp_spec.temperature == Decimal('297.03')
            if tc_num == 10:
                assert temp_spec.temperature == Decimal('297.66')
            if tc_num == 11:
                assert temp_spec.temperature == Decimal('296.59')
            if tc_num == 12:
                assert temp_spec.temperature == Decimal('297.42')
            if tc_num == 13:
                assert temp_spec.temperature == Decimal('296.36')
        elif index == 1:
            if tc_num == 4:
                assert temp_spec.temperature == Decimal('296.58')
            if tc_num == 5:
                assert temp_spec.temperature == Decimal('297.32')
            if tc_num == 6:
                assert temp_spec.temperature == Decimal('297.09')
            if tc_num == 7:
                assert temp_spec.temperature == Decimal('296.45')
            if tc_num == 8:
                assert temp_spec.temperature == Decimal('297.08')
            if tc_num == 9:
                assert temp_spec.temperature == Decimal('297.03')
            if tc_num == 10:
                assert temp_spec.temperature == Decimal('297.65')
            if tc_num == 11:
                assert temp_spec.temperature == Decimal('296.58')
            if tc_num == 12:
                assert temp_spec.temperature == Decimal('297.42')
            if tc_num == 13:
                assert temp_spec.temperature == Decimal('296.36')
        else:  # index must be 2
            if tc_num == 4:
                assert temp_spec.temperature == Decimal('296.58')
            if tc_num == 5:
                assert temp_spec.temperature == Decimal('297.32')
            if tc_num == 6:
                assert temp_spec.temperature == Decimal('297.07')
            if tc_num == 7:
                assert temp_spec.temperature == Decimal('296.45')
            if tc_num == 8:
                assert temp_spec.temperature == Decimal('297.08')
            if tc_num == 9:
                assert temp_spec.temperature == Decimal('297.02')
            if tc_num == 10:
                assert temp_spec.temperature == Decimal('297.65')
            if tc_num == 11:
                assert temp_spec.temperature == Decimal('296.57')
            if tc_num == 12:
                assert temp_spec.temperature == Decimal('297.42')
            if tc_num == 13:
                assert temp_spec.temperature == Decimal('296.36')
