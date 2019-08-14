"""IO utility service."""


class IOUtility(object):
    """IO utility."""

    # ------------------------------------------------------------------------
    # Public methods: included in the API

    @staticmethod
    def get_input(prompt):
        """Get user input."""
        response = []
        for message in prompt.messages:
            response.append(input(message).lower())

        return response

    # ------------------------------------------------------------------------
    # Internal methods: not included in the API

    pass
