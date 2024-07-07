# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from abc import abstractmethod


class ResultInfo(object):
    """
    Object holding the result of the discovery on particular dimension.
    The purpose of the object is to summarize and return the discovery results

    :param object: _description_
    :type object: _type_
    """ 
    def __init__(self):
        """_summary_
        """        
    @abstractmethod
    def getDiscoveryResult(self) -> str:
        """
        Return the discovery results summarized as a string

        :return: Discovery result
        :rtype: str
        """        
        return NotImplementedError