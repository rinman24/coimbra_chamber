import chamber.const as const

class TestConstants(object):
    """Unit testing of const.py."""

    def test_access_to_constants(self):
        """Check that constants can be imported."""
        assert const.D_PORT == 2.286e-2
