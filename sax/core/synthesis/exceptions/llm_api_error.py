# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------

class LLMApiErrorException(Exception):
   """Exception raised when an error occurs while calling an external LLM API"""
   def __init__(self, message, details):
        self.message = message
        self.details = details
        super().__init__(self.message)