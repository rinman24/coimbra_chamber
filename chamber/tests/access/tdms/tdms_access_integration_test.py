"""Integration test suite for TdmsAccess."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from pytz import utc

import pytest
from nptdms import TdmsFile
from pandas import DataFrame

from chamber.access.tdms.service import TdmsAccess
from chamber.access.sql.contracts import TemperatureSpec


# Module level globals -------------------------------------------------------


PATH = Path('chamber/tests/access/tdms/resources/test_1.tdms')


# TdmsAccess -----------------------------------------------------------------


@pytest.mark.parametrize('filepath', [PATH, 'bad_path'])
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
    tdms_access.connect(PATH)
    # Act --------------------------------------------------------------------
    results = tdms_access._get_temperature_specs(index)
    # Assert -----------------------------------------------------------------
    for temp_spec in results:
        assert isinstance(temp_spec, TemperatureSpec)
        tc_num = temp_spec.thermocouple_num
        if index == 0:
            if tc_num == 4:
                assert temp_spec.temperature == Decimal('296.58')
            elif tc_num == 5:
                assert temp_spec.temperature == Decimal('297.33')
            elif tc_num == 6:
                assert temp_spec.temperature == Decimal('297.08')
            elif tc_num == 7:
                assert temp_spec.temperature == Decimal('296.46')
            elif tc_num == 8:
                assert temp_spec.temperature == Decimal('297.08')
            elif tc_num == 9:
                assert temp_spec.temperature == Decimal('297.03')
            elif tc_num == 10:
                assert temp_spec.temperature == Decimal('297.66')
            elif tc_num == 11:
                assert temp_spec.temperature == Decimal('296.59')
            elif tc_num == 12:
                assert temp_spec.temperature == Decimal('297.42')
            else:  # index must be 13
                assert temp_spec.temperature == Decimal('296.36')
        elif index == 1:
            if tc_num == 4:
                assert temp_spec.temperature == Decimal('296.58')
            elif tc_num == 5:
                assert temp_spec.temperature == Decimal('297.32')
            elif tc_num == 6:
                assert temp_spec.temperature == Decimal('297.09')
            elif tc_num == 7:
                assert temp_spec.temperature == Decimal('296.45')
            elif tc_num == 8:
                assert temp_spec.temperature == Decimal('297.08')
            elif tc_num == 9:
                assert temp_spec.temperature == Decimal('297.03')
            elif tc_num == 10:
                assert temp_spec.temperature == Decimal('297.65')
            elif tc_num == 11:
                assert temp_spec.temperature == Decimal('296.58')
            elif tc_num == 12:
                assert temp_spec.temperature == Decimal('297.42')
            else:  # index must be 13
                assert temp_spec.temperature == Decimal('296.36')
        else:  # index must be 2
            if tc_num == 4:
                assert temp_spec.temperature == Decimal('296.58')
            elif tc_num == 5:
                assert temp_spec.temperature == Decimal('297.32')
            elif tc_num == 6:
                assert temp_spec.temperature == Decimal('297.07')
            elif tc_num == 7:
                assert temp_spec.temperature == Decimal('296.45')
            elif tc_num == 8:
                assert temp_spec.temperature == Decimal('297.08')
            elif tc_num == 9:
                assert temp_spec.temperature == Decimal('297.02')
            elif tc_num == 10:
                assert temp_spec.temperature == Decimal('297.65')
            elif tc_num == 11:
                assert temp_spec.temperature == Decimal('296.57')
            elif tc_num == 12:
                assert temp_spec.temperature == Decimal('297.42')
            else:  # index must be 13
                assert temp_spec.temperature == Decimal('296.36')


@pytest.mark.parametrize('index', [0, 1, 2])
def test_get_observation_sepc(tdms_access, index):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    tdms_access.connect(PATH)
    # Act --------------------------------------------------------------------
    results = tdms_access._get_observation_specs(index)
    # Assert -----------------------------------------------------------------
    for temp_spec in results.temperatures:
        assert isinstance(temp_spec, TemperatureSpec)
    if index == 0:
        assert results.cap_man_ok is True
        assert results.dew_point == Decimal('286.43')
        assert results.idx == 1
        assert results.mass == Decimal('0.0118974')
        assert results.optidew_ok is True
        assert results.pow_out == Decimal('-0.0011')
        assert results.pow_ref == Decimal('-0.0011')
        assert results.pressure == 100025
        assert results.surface_temp == Decimal('296.02')
    elif index == 1:
        assert results.cap_man_ok is True
        assert results.dew_point == Decimal('286.41')
        assert results.idx == 2
        assert results.mass == Decimal('0.0118974')
        assert results.optidew_ok is True
        assert results.pow_out == Decimal('-0.001')
        assert results.pow_ref == Decimal('-0.0011')
        assert results.pressure == 99981
        assert results.surface_temp == Decimal('295.92')
    else:  # index must be 2
        assert results.cap_man_ok is True
        assert results.dew_point == Decimal('286.46')
        assert results.idx == 3
        assert results.mass == Decimal('0.0118974')
        assert results.optidew_ok is True
        assert results.pow_out == Decimal('-0.0011')
        assert results.pow_ref == Decimal('-0.0010')
        assert results.pressure == 100016
        assert results.surface_temp == Decimal('295.82')


def test_get_experiment_spec(tdms_access):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    tdms_access.connect(PATH)
    setting_id = 1
    # Act --------------------------------------------------------------------
    result = tdms_access._get_experiment_specs(setting_id)
    # Assert -----------------------------------------------------------------
    assert result.author == 'Test'
    assert result.datetime == datetime(
        2019, 5, 15, 20, 10, 29, 882475, tzinfo=utc)
    assert result.description == 'Test description 1.'
    assert result.pool_id == 1
    assert result.setting_id == setting_id


def test_get_setting_spec(tdms_access):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    tdms_access.connect(PATH)
    # Act --------------------------------------------------------------------
    result = tdms_access._get_setting_specs()
    # Assert -----------------------------------------------------------------
    assert result.duty == Decimal('0.0')
    assert result.pressure == int(1e5)
    assert result.temperature == Decimal('300.0')
    assert result.time_step == Decimal('1.0')
