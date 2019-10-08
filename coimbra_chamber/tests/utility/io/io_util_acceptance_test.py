"""Unit test suite for io utility."""

import dacite

from coimbra_chamber.utility.io.service import IOUtility
from coimbra_chamber.utility.io.contracts import Prompt

# ----------------------------------------------------------------------------
# Acceptance tests


def test_can_get_single_input():  # noqa: D103
    # Arrange ----------------------------------------------------------------
    io_util = IOUtility()
    data = dict(messages=['Would you like to proceed?'])
    prompt = dacite.from_dict(Prompt, data)
    # Act --------------------------------------------------------------------
    response = io_util.get_input(prompt)
    print(response)


def test_can_get_double_input():  # noqa: D103
    # Arrange ----------------------------------------------------------------
    io_util = IOUtility()
    data = dict(messages=['Lower limit on index:', 'Upper limit on index:'])
    prompt = dacite.from_dict(Prompt, data)
    # Act --------------------------------------------------------------------
    response = io_util.get_input(prompt)
    print(response)
