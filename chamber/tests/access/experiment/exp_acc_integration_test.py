"""Integration test suite for ChamberAccess."""

import dataclasses
import datetime
from decimal import Decimal

import dacite
import pytest
from nptdms import TdmsFile
from pandas import DataFrame
from pytz import utc

from chamber.access.experiment.contracts import TemperatureSpec
from chamber.access.experiment.models import (
    Experiment,
    Observation,
    Tube,
    Setting,
    Temperature)
from chamber.access.experiment.service import ExperimentAccess

from chamber.tests.conftest import tdms_path



# ----------------------------------------------------------------------------
# ChamberAccess


# _add_tube ------------------------------------------------------------------


def test_add_tube_that_does_not_exist(exp_acc, tube_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    tube_id = exp_acc._add_tube(tube_spec)
    # Assert -----------------------------------------------------------------
    assert tube_id == 1
    # Now query result -------------------------------------------------------
    session = exp_acc.Session()
    try:
        query = session.query(Tube).filter(Tube.material == 'test_material')
        result = query.one()
        session.commit()
        assert result.inner_diameter == Decimal('0.1000')
        assert result.outer_diameter == Decimal('0.2000')
        assert result.height == Decimal('0.3000')
        assert result.mass == Decimal('0.4000000')
    finally:
        session.close()


def test_add_tube_that_already_exists(exp_acc, tube_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the tube
    # NOTE: These tests are intended to be run sequently
    exp_acc._add_tube(tube_spec)
    # Act --------------------------------------------------------------------
    new_tube_id = exp_acc._add_tube(tube_spec)
    # Assert -----------------------------------------------------------------
    assert new_tube_id == 1

# _add_setting ---------------------------------------------------------------


def test_add_setting_that_does_not_exist(exp_acc, setting_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    setting_id = exp_acc._add_setting(setting_spec)
    # Assert -----------------------------------------------------------------
    assert setting_id == 1
    # Now query result -------------------------------------------------------
    session = exp_acc.Session()
    try:
        query = session.query(Setting)
        query = query.filter(Setting.pressure == setting_spec.pressure)
        result = query.one()
        session.commit()
        assert result.duty == Decimal('0.0')
        assert result.temperature == Decimal('290.0')
        assert result.time_step == Decimal('1.0')
    finally:
        session.close()


def test_add_setting_that_already_exists(exp_acc, setting_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the setting
    # NOTE: These tests are intended to be run sequently
    exp_acc._add_setting(setting_spec)
    # Act --------------------------------------------------------------------
    new_setting_id = exp_acc._add_setting(setting_spec)
    # Assert -----------------------------------------------------------------
    assert new_setting_id == 1


# _add_experiment ------------------------------------------------------------


def test_add_experiment_that_does_not_exist(exp_acc, experiment_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    setting_id = 1
    experiment_id = exp_acc._add_experiment(experiment_spec, setting_id)
    # Assert -----------------------------------------------------------------
    assert experiment_id == 1
    # Now query result -------------------------------------------------------
    session = exp_acc.Session()
    try:
        query = session.query(Experiment)
        query = query.filter(Experiment.datetime == experiment_spec.datetime)
        result = query.one()
        session.commit()
        assert result.author == 'RHI'
        assert result.description == 'The description is descriptive.'
        assert result.tube_id == 1
        assert result.setting_id == 1
    finally:
        session.close()


def test_add_experiment_that_already_exists(exp_acc, experiment_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the experiment
    # NOTE: These tests are intended to be run sequently
    setting_id = 1
    exp_acc._add_experiment(experiment_spec, setting_id)
    # Act --------------------------------------------------------------------
    new_experiment_id = exp_acc._add_experiment(experiment_spec, setting_id)
    # Assert -----------------------------------------------------------------
    assert new_experiment_id == 1


# _add_observations ----------------------------------------------------------


def test_add_observations_that_do_not_exist(exp_acc, observation_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    experiment_id = 1
    #  Act --------------------------------------------------------------------
    returned_dict = exp_acc._add_observations(observation_spec, experiment_id)
    # Assert -----------------------------------------------------------------
    assert returned_dict == dict(observations=2, temperatures=6)
    # Now query result -------------------------------------------------------
    session = exp_acc.Session()
    try:
        query = session.query(Observation)
        query = query.filter(Observation.experiment_id == experiment_id)
        observations = query.all()
        for observation in observations:
            if observation.idx == 0:
                assert observation.cap_man_ok
                assert observation.dew_point == Decimal('280.12')
                assert observation.idx == 0
                assert observation.mass == Decimal('0.1234567')
                assert observation.optidew_ok
                assert observation.pow_out == 0
                assert observation.pow_ref == 0
                assert observation.pressure == 987654
                assert observation.surface_temp == Decimal('280.0')
            elif observation.idx == 1:
                assert not observation.cap_man_ok
                assert observation.dew_point == Decimal('280.20')
                assert observation.idx == 1
                assert observation.mass == Decimal('0.1222222')
                assert not observation.optidew_ok
                assert observation.pow_out == 0
                assert observation.pow_ref == 0
                assert observation.pressure == 987000
                assert observation.surface_temp == Decimal('280.2')
        query = session.query(Temperature)
        temperatures = query.filter(Temperature.experiment_id == experiment_id)
        for temperature in temperatures:
            if temperature.idx == 0:
                if temperature.thermocouple_num == 0:
                    assert temperature.temperature == Decimal('300.0')
                elif temperature.thermocouple_num == 1:
                    assert temperature.temperature == Decimal('300.2')
                elif temperature.thermocouple_num == 2:
                    assert temperature.temperature == Decimal('300.4')
            elif temperature.idx == 1:
                if temperature.thermocouple_num == 0:
                    assert temperature.temperature == Decimal('301.0')
                elif temperature.thermocouple_num == 1:
                    assert temperature.temperature == Decimal('301.2')
                elif temperature.thermocouple_num == 2:
                    assert temperature.temperature == Decimal('301.4')
        session.commit()
    finally:
        session.close()


def test_add_observations_that_already_exist(exp_acc, observation_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the observations
    # NOTE: These tests are intended to be run sequently
    experiment_id = 1
    # Act --------------------------------------------------------------------
    returned_dict = exp_acc._add_observations(observation_spec, experiment_id)
    # Assert -----------------------------------------------------------------
    assert returned_dict == dict(observations=2, temperatures=6)


# add_raw_data -------------------------------------------------------------------

@pytest.mark.parametrize('tube_id', [1, 999])
def test_add_raw_data(exp_acc, data_spec, tube_id):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The tests above have already added the this to the database for
    # tube_id == 1, but not for tube_id == 999.
    changes = dict(tube_id=tube_id)
    experimental_spec = dataclasses.replace(data_spec.experiment, **changes)
    changes = dict(experiment=experimental_spec)
    data_spec = dataclasses.replace(data_spec, **changes)
    # Act --------------------------------------------------------------------
    result = exp_acc.add_raw_data(data_spec)
    # Assert -----------------------------------------------------------------
    if tube_id == 1:
        assert result['tube_id'] == 1
        assert result['setting_id'] == 1
        assert result['experiment_id'] == 1
        assert result['observations'] == 2
        assert result['temperatures'] == 6
    else:
        assert not result


@pytest.mark.parametrize('filepath', [tdms_path, 'bad_path'])
def test_connect(exp_acc, filepath):  # noqa: D103
    # Act --------------------------------------------------------------------
    exp_acc._connect(filepath)
    # Assert -----------------------------------------------------------------
    if filepath:
        assert isinstance(exp_acc._tdms_file, TdmsFile)
        assert isinstance(exp_acc._settings, DataFrame)
        assert isinstance(exp_acc._data, DataFrame)
    else:
        assert not hasattr(exp_acc._tdms_file)


@pytest.mark.parametrize('index', [0, 1, 2])
def test_get_temperature_spec(exp_acc, index):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    exp_acc._connect(tdms_path)
    # Act --------------------------------------------------------------------
    results = exp_acc._get_temperature_specs(index)
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
def test_get_observation_sepc(exp_acc, index):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    exp_acc._connect(tdms_path)
    # Act --------------------------------------------------------------------
    results = exp_acc._get_observation_specs(index)
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


def test_get_experiment_spec(exp_acc):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    exp_acc._connect(tdms_path)
    # Act --------------------------------------------------------------------
    result = exp_acc._get_experiment_specs()
    # Assert -----------------------------------------------------------------
    assert result.author == 'Test'
    assert result.datetime == datetime.datetime(
        2019, 5, 15, 20, 10, 29, 882475, tzinfo=utc)
    assert result.description == 'Test description 1.'
    assert result.tube_id == 1


def test_get_setting_spec(exp_acc):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    exp_acc._connect(tdms_path)
    # Act --------------------------------------------------------------------
    result = exp_acc._get_setting_specs()
    # Assert -----------------------------------------------------------------
    assert result.duty == Decimal('0.0')
    assert result.pressure == int(1e5)
    assert result.temperature == Decimal('300.0')
    assert result.time_step == Decimal('1.0')


def test_get_raw_data(exp_acc):  # noqa: D103
    # Act --------------------------------------------------------------------
    result = exp_acc.get_raw_data(tdms_path)
    # Assert -----------------------------------------------------------------
    # Spot check values from each attribute.
    assert result.setting.duty == Decimal('0')
    assert result.experiment.datetime == datetime.datetime(
        2019, 5, 15, 20, 10, 29, 882475, tzinfo=utc)
    assert result.observations[0].pressure == 100025
    assert result.observations[0].temperatures[0].thermocouple_num == 4
    # Check the length of observations and temperatures
    assert len(result.observations) == 3
    assert len(result.observations[0].temperatures) == 10
