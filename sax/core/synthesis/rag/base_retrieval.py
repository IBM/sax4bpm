# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from abc import abstractmethod

class BaseRetriever: 
    @abstractmethod                
    def getContext(self, query):
        pass