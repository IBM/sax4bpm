# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from abc import abstractmethod

class BaseRetriever: 
    """
    Base class for all document retriever wrappers   
    """ 
    @abstractmethod                
    def get_retriever(self):
        """Get the embedded retriever
        """
        pass

