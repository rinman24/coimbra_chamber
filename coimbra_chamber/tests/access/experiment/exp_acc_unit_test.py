"""Unit test suite for ChamberAccess."""

# import dataclasses
# import datetime
from decimal import Decimal
from unittest.mock import call, MagicMock

import dacite
import pytest
# from nptdms import TdmsFile
# from pandas import DataFrame
# from pytz import utc
# from sqlalchemy import and_

# from coimbra_chamber.access.experiment.contracts import TemperatureSpec
# from coimbra_chamber.access.experiment.models import (
#     Experiment,
#     Fit,
#     Observation,
#     Tube,
#     Setting,
#     Temperature)
from coimbra_chamber.access.experiment.contracts import TubeSpec
from coimbra_chamber.access.experiment.service import ExperimentAccess

# from coimbra_chamber.tests.conftest import tdms_path


# ----------------------------------------------------------------------------
# ChamberAccess


# _get_tube_spec -------------------------------------------------------------

def test_get_tube_spec(monkeypatch):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    access = ExperimentAccess()
    # _get_tube_spec is going to ask for several inputs. In order they are:
    # inner diameter, outer diameter, height, material, and mass.
    # We want to make sure that we coerce the user to input the correct type.
    # As a result, we will need to mock io_util to pass in incorrect values
    # and then correct values.
    user_input = [['inner diameter'], ['0.12345'],
                  ['outer diamter'], ['0.67891'],
                  ['height'], ['0.24681'],
                  ['mass'], ['0.1234567'],
                  ['material']]
    # Now we need to wire this up to the io_utility
    mock_io = MagicMock(side_effect=user_input)
    monkeypatch.setattr(
        'coimbra_chamber.utility.io.service.IOUtility.get_input',
        mock_io)
    # Create the expected tube spec
    data = dict(
        inner_diameter=Decimal(0.12345),
        outer_diameter=Decimal(0.67891),
        height=Decimal(0.24681),
        material='material',
        mass=Decimal(0.1234567),
    )
    tube_spec = dacite.from_dict(TubeSpec, data)
    # Act --------------------------------------------------------------------
    access._get_tube_spec()
    # Assert -----------------------------------------------------------------
    assert access._tube_spec == tube_spec


def test_public_add_tube(tube_spec, monkeypatch):  # noqa: D103
    # Arrange ------------------------------------------------------------
    access = ExperimentAccess()
    access._tube_spec = tube_spec
    mock_access = MagicMock()
    monkeypatch.setattr(
        'coimbra_chamber.access.experiment.service.ExperimentAccess'
        '._get_tube_spec',
        mock_access._get_tube_spec
    )
    monkeypatch.setattr(
        'coimbra_chamber.access.experiment.service.ExperimentAccess'
        '._add_tube',
        mock_access._add_tube
    )
    get_tube_spec_calls = [call()]
    add_tube_calls = [call(access._tube_spec)]
    # Act ----------------------------------------------------------------
    access.add_tube()
    # Assert -------------------------------------------------------------
    mock_access._get_tube_spec.assert_has_calls(get_tube_spec_calls)
    mock_access._add_tube.assert_has_calls(add_tube_calls)
