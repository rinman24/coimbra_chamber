"""Unit test suite for ChamberAccess."""

from unittest.mock import call, MagicMock

import pytest
from dacite import from_dict

from chamber.access.sql.contracts import DataSpec


# ----------------------------------------------------------------------------
# Fixtures


@pytest.fixture('function')
def access_mock(monkeypatch):
    """Mock of ChamberAccess fixture."""
    access_mock = MagicMock()
    # _add_pool
    access_mock._add_pool = MagicMock(return_value=1)
    monkeypatch.setattr(
        'chamber.access.sql.service.ChamberAccess._add_pool',
        access_mock._add_pool)
    # _add_setting
    access_mock._add_setting = MagicMock(return_value=1)
    monkeypatch.setattr(
        'chamber.access.sql.service.ChamberAccess._add_setting',
        access_mock._add_setting)
    # _add_experiment
    access_mock._add_experiment = MagicMock(return_value=1)
    monkeypatch.setattr(
        'chamber.access.sql.service.ChamberAccess._add_experiment',
        access_mock._add_experiment)
    # _add_observations
    return_value = dict(observations=2, temperatures=6)
    access_mock._add_observations = MagicMock(return_value=return_value)
    monkeypatch.setattr(
        'chamber.access.sql.service.ChamberAccess._add_observations',
        access_mock._add_observations)

    return access_mock


# ----------------------------------------------------------------------------
# ChamberAccess


# add_data -------------------------------------------------------------------


def test_add_data(
        pool_spec, setting_spec, experiment_spec, observation_specs, access,
        access_mock):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = dict(
        pool=pool_spec,
        setting=setting_spec,
        experiment=experiment_spec,
        observations=observation_specs)
    data_specs = from_dict(DataSpec, data)
    correct_calls = [
        call._add_pool(pool_spec),
        call._add_setting(setting_spec),
        call._add_experiment(experiment_spec),
        call._add_observations(observation_specs, 1)
        ]
    # Act --------------------------------------------------------------------
    result = access.add_data(data_specs)
    # Assert -----------------------------------------------------------------
    assert result['pool_id'] == 1
    assert result['setting_id'] == 1
    assert result['experiment_id'] == 1
    assert result['observations'] == 2
    assert result['temperatures'] == 6

    access_mock.assert_has_calls(correct_calls)
