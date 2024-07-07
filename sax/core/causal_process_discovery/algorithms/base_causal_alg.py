# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from abc import abstractmethod
from typing import List, Optional

from pandas import DataFrame

from sax.core.causal_process_discovery.prior_knowledge import PriorKnowledge
from sax.core.process_data.discovery_result import ResultInfo


class CausalDataException(Exception):
    """
    Exception indicating that the data object containing process data is not suitable for causal discovery in its present form.

    :param Exception: exception indicating the reason why the process data object is not suitable for causal discovery
    :type Exception:
    """    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CausalResultInfo(ResultInfo):
    # Assisted by WCA for GP
    # Latest GenAI contribution: granite-20B-code-instruct-v2 model
    """
    Class containing causal discovery results. Basically this is a wrapper around causal adjacency matrix.
    """
  
    def __init__(self, adjacencyMatrix: List[List[int]], columns: List[str]):
       super().__init__()
       self.adjacencyMatrix = adjacencyMatrix
       self.columns = columns

    def getAdjacencyMatrix(self) -> List[List[int]]:
        """
        Return causal adjacency matrix contained within this object

        :return: causal adjacency matrix
        :rtype: List[List[int]]
        """        
        return self.adjacencyMatrix
    
    def getColumns(self) -> List[str]:
        """
        Return a list with the names of the columns appearing in the adjacency matrix

        :return: List of column names
        :rtype: List[str]
        """        
        return self.columns
    
    #TODO convert the result to string
    def getDiscoveryResult(self) -> str:
        """
        Return a NL description of the causal relationships 

        :return: Textual description of causal relationships
        :rtype: str
        """        
        return self.adjacencyMatrix
    


class BaseCausalAlgorithm(object):
    # Assisted by WCA for GP
    # Latest GenAI contribution: granite-20B-code-instruct-v2 model
    """
    Parent class for all causal discovery algorithms implementations. Please extend this class to add more algorithms.    
    """
  

    def __init__(self, data: DataFrame, prior_knowledge: Optional[PriorKnowledge]=None):
        """
        Initialize an instance of the algorithm for particular data.

        Parameters
        ----------
        data : pandas.DataFrame
            Dataframe containing the event log.
        prior_knowledge : PriorKnowledge, optional
            Prior knowledge object containing the domain knowledge. Defaults to None.
        """    
        self.data = data
        self.prior_knowledge =prior_knowledge

    @abstractmethod    
    def sanity_check(self):
        """
        Sanity check of the data object for causal discovery

        Returns
        -------
        :return: Boolean indicator whether the data object is coherent
        :rtype: bool

        Raises
        --------
        :raises NotImplementedError:       
        """       
        raise NotImplementedError()
   
    @abstractmethod
    def run(self) ->ResultInfo:
        """
        Run the causal discovery algorithm and return the result
        
        Returns
        -------
        :return: A object holding the causal discovery result
        :rtype: ResultInfo

        Raises
        --------
        :raises NotImplementedError:
        
        """     
        raise NotImplementedError()

    