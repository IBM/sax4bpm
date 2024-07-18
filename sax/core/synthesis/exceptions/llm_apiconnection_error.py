# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
class LLMApiConnectionException(Exception):
   """Exception risen when there is connection problem to external LLM
   """
   def __init__(self, message, details):
        self.message = message
        self.details = details
        super().__init__(self.message)