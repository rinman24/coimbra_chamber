"""Integration test suite for ChamberAccess."""

from dataclasses import replace
from decimal import Decimal

from dacite import from_dict
import pytest

from chamber.access.sql.models import Experiment, Observation, Tube
from chamber.access.sql.models import Setting, Temperature


# ----------------------------------------------------------------------------
# ChamberAccess


# _add_tube ------------------------------------------------------------------


def test_add_tube_that_does_not_exist(chamber_access, tube_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    tube_id = chamber_access._add_tube(tube_spec)
    # Assert -----------------------------------------------------------------
    assert tube_id == 1
    # Now query result -------------------------------------------------------
    session = chamber_access.Session()
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


def test_add_tube_that_already_exists(chamber_access, tube_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the tube
    # NOTE: These tests are intended to be run sequently
    chamber_access._add_tube(tube_spec)
    # Act --------------------------------------------------------------------
    new_tube_id = chamber_access._add_tube(tube_spec)
    # Assert -----------------------------------------------------------------
    assert new_tube_id == 1

# _add_setting ---------------------------------------------------------------


def test_add_setting_that_does_not_exist(chamber_access, setting_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    setting_id = chamber_access._add_setting(setting_spec)
    # Assert -----------------------------------------------------------------
    assert setting_id == 1
    # Now query result -------------------------------------------------------
    session = chamber_access.Session()
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


def test_add_setting_that_already_exists(chamber_access, setting_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the setting
    # NOTE: These tests are intended to be run sequently
    chamber_access._add_setting(setting_spec)
    # Act --------------------------------------------------------------------
    new_setting_id = chamber_access._add_setting(setting_spec)
    # Assert -----------------------------------------------------------------
    assert new_setting_id == 1


# _add_experiment ------------------------------------------------------------


def test_add_experiment_that_does_not_exist(chamber_access, experiment_spec):  # noqa: D103
    # Act --------------------------------------------------------------------
    setting_id = 1
    experiment_id = chamber_access._add_experiment(experiment_spec, setting_id)
    # Assert -----------------------------------------------------------------
    assert experiment_id == 1
    # Now query result -------------------------------------------------------
    session = chamber_access.Session()
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


def test_add_experiment_that_already_exists(chamber_access, experiment_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the experiment
    # NOTE: These tests are intended to be run sequently
    setting_id = 1
    chamber_access._add_experiment(experiment_spec, setting_id)
    # Act --------------------------------------------------------------------
    new_experiment_id = chamber_access._add_experiment(experiment_spec, setting_id)
    # Assert -----------------------------------------------------------------
    assert new_experiment_id == 1


# _add_observations ----------------------------------------------------------


def test_add_observations_that_do_not_exist(chamber_access, observation_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    experiment_id = 1
    #  Act --------------------------------------------------------------------
    returned_dict = chamber_access._add_observations(observation_spec, experiment_id)
    # Assert -----------------------------------------------------------------
    assert returned_dict == dict(observations=2, temperatures=6)
    # Now query result -------------------------------------------------------
    session = chamber_access.Session()
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


def test_add_observations_that_already_exist(chamber_access, observation_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The test above already added the observations
    # NOTE: These tests are intended to be run sequently
    experiment_id = 1
    # Act --------------------------------------------------------------------
    returned_dict = chamber_access._add_observations(observation_spec, experiment_id)
    # Assert -----------------------------------------------------------------
    assert returned_dict == dict(observations=2, temperatures=6)


# add_data -------------------------------------------------------------------

@pytest.mark.parametrize('tube_id', [1, 999])
def test_add_data(chamber_access, data_spec, tube_id):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    # NOTE: The tests above have already added the this to the database for
    # tube_id == 1, but not for tube_id == 999.
    changes = dict(tube_id=tube_id)
    experimental_spec = replace(data_spec.experiment, **changes)
    changes = dict(experiment=experimental_spec)
    data_spec = replace(data_spec, **changes)
    # Act --------------------------------------------------------------------
    result = chamber_access.add_data(data_spec)
    # Assert -----------------------------------------------------------------
    if tube_id == 1:
        assert result['tube_id'] == 1
        assert result['setting_id'] == 1
        assert result['experiment_id'] == 1
        assert result['observations'] == 2
        assert result['temperatures'] == 6
    else:
        assert not result
