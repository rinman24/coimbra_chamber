"""Integration test suite for ChamberAccess."""

import dataclasses
import datetime
from decimal import Decimal

import dacite
import pytest
from nptdms import TdmsFile
from pandas import DataFrame
from pytz import utc
from sqlalchemy import and_

from chamber.access.experiment.contracts import TemperatureSpec
from chamber.access.experiment.models import (
    Experiment,
    Fit,
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
                assert observation.surface_temp == Decimal('290.0')
                assert observation.ic_temp == Decimal('291.00')
            elif observation.idx == 1:
                assert not observation.cap_man_ok
                assert observation.dew_point == Decimal('280.20')
                assert observation.idx == 1
                assert observation.mass == Decimal('0.1222222')
                assert not observation.optidew_ok
                assert observation.pow_out == 0
                assert observation.pow_ref == 0
                assert observation.pressure == 987000
                assert observation.surface_temp == Decimal('290.2')
                assert observation.ic_temp == Decimal('291.20')
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


# add_raw_data ---------------------------------------------------------------


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


# connect --------------------------------------------------------------------


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


# get_temperature_spec -------------------------------------------------------


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
                assert temp_spec.temperature == Decimal('290.21')
            elif tc_num == 5:
                assert temp_spec.temperature == Decimal('289.9')
            elif tc_num == 6:
                assert temp_spec.temperature == Decimal('289.88')
            elif tc_num == 7:
                assert temp_spec.temperature == Decimal('290.21')
            elif tc_num == 8:
                assert temp_spec.temperature == Decimal('290.21')
            elif tc_num == 9:
                assert temp_spec.temperature == Decimal('289.82')
            elif tc_num == 10:
                assert temp_spec.temperature == Decimal('289.72')
            elif tc_num == 11:
                assert temp_spec.temperature == Decimal('289.91')
            elif tc_num == 12:
                assert temp_spec.temperature == Decimal('289.7')
            else:  # index must be 13
                assert temp_spec.temperature == Decimal('290.1')
        elif index == 1:
            if tc_num == 4:
                assert temp_spec.temperature == Decimal('290.23')
            elif tc_num == 5:
                assert temp_spec.temperature == Decimal('289.9')
            elif tc_num == 6:
                assert temp_spec.temperature == Decimal('289.89')
            elif tc_num == 7:
                assert temp_spec.temperature == Decimal('290.23')
            elif tc_num == 8:
                assert temp_spec.temperature == Decimal('290.22')
            elif tc_num == 9:
                assert temp_spec.temperature == Decimal('289.83')
            elif tc_num == 10:
                assert temp_spec.temperature == Decimal('289.73')
            elif tc_num == 11:
                assert temp_spec.temperature == Decimal('289.92')
            elif tc_num == 12:
                assert temp_spec.temperature == Decimal('289.72')
            else:  # index must be 13
                assert temp_spec.temperature == Decimal('290.11')
        else:  # index must be 2
            if tc_num == 4:
                assert temp_spec.temperature == Decimal('290.23')
            elif tc_num == 5:
                assert temp_spec.temperature == Decimal('289.91')
            elif tc_num == 6:
                assert temp_spec.temperature == Decimal('289.9')
            elif tc_num == 7:
                assert temp_spec.temperature == Decimal('290.23')
            elif tc_num == 8:
                assert temp_spec.temperature == Decimal('290.23')
            elif tc_num == 9:
                assert temp_spec.temperature == Decimal('289.84')
            elif tc_num == 10:
                assert temp_spec.temperature == Decimal('289.74')
            elif tc_num == 11:
                assert temp_spec.temperature == Decimal('289.93')
            elif tc_num == 12:
                assert temp_spec.temperature == Decimal('289.73')
            else:  # index must be 13
                assert temp_spec.temperature == Decimal('290.11')


# get_observation_spec -------------------------------------------------------


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
        assert results.dew_point == Decimal('284.29')
        assert results.idx == 1
        assert results.mass == Decimal('0.0129683')
        assert results.optidew_ok is True
        assert results.pow_out == Decimal('-0.0012')
        assert results.pow_ref == Decimal('-0.0015')
        assert results.pressure == 99732
        assert results.surface_temp == Decimal('291.34')
        assert results.ic_temp == Decimal('294.86')
    elif index == 1:
        assert results.cap_man_ok is True
        assert results.dew_point == Decimal('284.3')
        assert results.idx == 2
        assert results.mass == Decimal('0.0129682')
        assert results.optidew_ok is True
        assert results.pow_out == Decimal('-0.0011')
        assert results.pow_ref == Decimal('-0.0015')
        assert results.pressure == 99749
        assert results.surface_temp == Decimal('291.3')
        assert results.ic_temp == Decimal('294.86')
    else:  # index must be 2
        assert results.cap_man_ok is True
        assert results.dew_point == Decimal('284.3')
        assert results.idx == 3
        assert results.mass == Decimal('0.0129682')
        assert results.optidew_ok is True
        assert results.pow_out == Decimal('-0.0011')
        assert results.pow_ref == Decimal('-0.0016')
        assert results.pressure == 99727
        assert results.surface_temp == Decimal('291.22')
        assert results.ic_temp == Decimal('294.86')


# get_experiment_spec --------------------------------------------------------


def test_get_experiment_spec(exp_acc):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    exp_acc._connect(tdms_path)
    # Act --------------------------------------------------------------------
    result = exp_acc._get_experiment_specs()
    # Assert -----------------------------------------------------------------
    assert result.author == 'RHI'
    assert result.datetime == datetime.datetime(
        2019, 6, 1, 17, 56, 34, 399828, tzinfo=utc)
    assert result.description == 'Test description 1.'
    assert result.tube_id == 1


# get_setting_spec -----------------------------------------------------------


def test_get_setting_spec(exp_acc):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    exp_acc._connect(tdms_path)
    # Act --------------------------------------------------------------------
    result = exp_acc._get_setting_specs()
    # Assert -----------------------------------------------------------------
    assert result.duty == Decimal('0.0')
    assert result.pressure == int(1e5)
    assert result.temperature == Decimal('290')
    assert result.time_step == Decimal('1.0')


# get_raw_data ---------------------------------------------------------------


def test_get_raw_data(exp_acc):  # noqa: D103
    # Act --------------------------------------------------------------------
    result = exp_acc.get_raw_data(tdms_path)
    # Assert -----------------------------------------------------------------
    # Spot check values from each attribute.
    assert result.setting.duty == Decimal('0')
    assert result.experiment.datetime == datetime.datetime(
        2019, 6, 1, 17, 56, 34, 399828, tzinfo=utc)
    assert result.observations[0].pressure == 99732
    assert result.observations[0].temperatures[0].thermocouple_num == 4
    # Check the length of observations and temperatures
    assert len(result.observations) == 3
    assert len(result.observations[0].temperatures) == 10


# layout_raw_data ------------------------------------------------------------


def test_layout_raw_data(exp_acc, raw_layout):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    raw_data = exp_acc.get_raw_data(tdms_path)
    # Act --------------------------------------------------------------------
    layout = exp_acc.layout_raw_data(raw_data)
    # Assert -----------------------------------------------------------------
    assert layout.style == raw_layout.style
    # mass and temperature
    assert layout.plots[0] == raw_layout.plots[0]
    # pressure
    assert layout.plots[1] == raw_layout.plots[1]


# add_fit --------------------------------------------------------------------


def test_add_fit_that_does_not_exist(exp_acc, fit_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    expected_experiment_id = 1
    expected_idx = fit_spec.idx
    # Act --------------------------------------------------------------------
    exp_id, idx = exp_acc.add_fit(fit_spec, expected_experiment_id)
    # Assert -----------------------------------------------------------------
    assert exp_id == expected_experiment_id
    assert idx == expected_idx
    # Now query result -------------------------------------------------------
    session = exp_acc.Session()
    try:
        query = session.query(Fit).filter(
            and_(Fit.idx == expected_idx, Fit.experiment_id == exp_id)
        )
        result = query.one()
        session.commit()
        assert result.a == 1.0
        assert result.sig_a == 2.0
        assert result.b == -3.0
        assert result.sig_b == 4.0
        assert result.r2 == 5.0
        assert result.q == 6.0
        assert result.chi2 == 7.0
        assert result.nu_chi == 8
        assert result.experiment_id == 1
        assert result.idx == 0
        assert result.mddp == 9
        assert result.sig_mddp == 9.1
        assert result.x1s == 10
        assert result.sig_x1s == 10.1
        assert result.x1e == 11
        assert result.sig_x1e == 11.1
        assert result.x1 == 12
        assert result.sig_x1 == 12.1
        assert result.m1s == 13
        assert result.sig_m1s == 13.1
        assert result.m1e == 14
        assert result.sig_m1e == 14.1
        assert result.m1 == 15
        assert result.sig_m1 == 15.1
        assert result.rhos == 16
        assert result.sig_rhos == 16.1
        assert result.rhoe == 17
        assert result.sig_rhoe == 17.1
        assert result.rho == 18
        assert result.sig_rho == 18.1
        assert result.Bm1 == 19
        assert result.sig_Bm1 == 19.1
        assert result.T == 20
        assert result.sig_T == 20.1
        assert result.D12 == 21
        assert result.sig_D12 == 21.1
        assert result.hfg == 22
        assert result.sig_hfg == 22.1
        assert result.hu == 23
        assert result.sig_hu == 23.1
        assert result.hs == 24
        assert result.sig_hs == 24.1
        assert result.cpv == 25
        assert result.sig_cpv == 25.1
        assert result.he == 26
        assert result.sig_he == 26.1
        assert result.cpl == 27
        assert result.sig_cpl == 27.1
        assert result.hT == 28
        assert result.sig_hT == 28.1
        assert result.qcu == 29
        assert result.sig_qcu == 29.1
        assert result.Ebe == 30
        assert result.sig_Ebe == 30.1
        assert result.Ebs == 31
        assert result.sig_Ebs == 31.1
        assert result.qrs == 32
        assert result.sig_qrs == 32.1
        assert result.kv == 33
        assert result.sig_kv == 33.1
        assert result.alpha == 34
        assert result.sig_alpha == 34.1
        assert result.Bh == 35
        assert result.sig_Bh == 35.1
        assert result.M == 36
        assert result.sig_M == 36.1
        assert result.gamma1 == 37
        assert result.sig_gamma1 == 37.1
        assert result.beta == 38
        assert result.sig_beta == 38.1
        assert result.Delta_m == 39
        assert result.sig_Delta_m == 39.1
        assert result.Delta_T == 40
        assert result.sig_Delta_T == 40.1
        assert result.mu == 41
        assert result.sig_mu == 41.1
        assert result.nu == 42
        assert result.sig_nu == 42.1
        assert result.gamma2 == 43
        assert result.sig_gamma2 == 43.1
    finally:
        session.close()


def test_add_fit_that_already_exists(exp_acc, fit_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    expected_experiment_id = 1
    expected_idx = fit_spec.idx
    # NOTE: The test above already added the fit
    # NOTE: These tests are intended to be run sequently
    # Act --------------------------------------------------------------------
    new_exp_id, new_idx = exp_acc.add_fit(fit_spec, expected_experiment_id)
    # Assert -----------------------------------------------------------------
    assert new_exp_id == expected_experiment_id
    assert new_idx == expected_idx
