# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
class LLMTimeoutException(Exception):
    """Exception risen when there is timeout problem when invoking external LLM
    """ 
    def __init__(self, message, details):
        self.message = message
        self.details = details
        super().__init__(self.message)