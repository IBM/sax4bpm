# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
class ValidationException(Exception):
    """Exception risen then there is validation exception on the passed parameters
    """
    def __init__(self, message, details):
        self.message = message
        self.details = details
        super().__init__(self.message)