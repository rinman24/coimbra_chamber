"""Integration test suite for DataManager."""

from pathlib import Path
from unittest.mock import MagicMock

import chamber as cc


def test_successful_run(tube_spec, monkeypatch):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    manager = cc.DataManager()
    # Add the tube
    _ = manager._exp_acc._add_tube(tube_spec)
    # Mocks
    mock_manager = MagicMock()
    # Manually set the path rather than asking the user.
    path = Path('chamber/tests/manager/data/sample_data.tdms')
    mock_manager._get_path = MagicMock(return_value=path)
    monkeypatch.setattr(
        'chamber.manager.data.service.DataManager._get_path',
        mock_manager._get_path)
    # Stop plotting for this test
    monkeypatch.setattr(
        'chamber.utility.plot.service.PlotUtility.plot',
        mock_manager.plot)
    # Ensure user continues
    mock_manager.get_input = MagicMock(side_effect=[['y'], ['c']])
    monkeypatch.setattr(
        'chamber.utility.io.service.IOUtility.get_input',
        mock_manager.get_input)
    # Act --------------------------------------------------------------------
    manager.run()
    # Assert -----------------------------------------------------------------
    assert manager._success
