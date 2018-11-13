"""Experiment manager unit test suite."""

import chamber.manager.experiment as expr_mngr


def test_can_call_add_tube():  # noqa: D103
    expr_mngr.add_tube()
