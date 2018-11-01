"""Experiment access unit test suite."""

import chamber.access.experiment as exp


def test_can_call_connect():  # noqa D103
    exp.connect('schema')
