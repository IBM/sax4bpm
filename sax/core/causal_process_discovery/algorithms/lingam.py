# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Optional

from pandas import DataFrame

import lingam
from sax.core.causal_process_discovery.algorithms.base_causal_alg import BaseCausalAlgorithm, CausalDataException, \
    CausalResultInfo
from sax.core.causal_process_discovery.prior_knowledge import PriorKnowledge
import networkx as nx

class LingamImpl(BaseCausalAlgorithm):
    """DirectLINGAM causal discovery algorithm wrapper for process execution causal discovery. Make use of `DirectLINGAM algorithm <https://lingam.readthedocs.io/en/latest/reference/direct_lingam.html>`_

    :param BaseCausalAlgorithm: base type
    :type BaseCausalAlgorithm: BaseCausalAlgorithm
    """    
    def __init__(self,   data: DataFrame, prior_knowledge: Optional[PriorKnowledge]=None):      
        super().__init__(data,prior_knowledge)

    def sanity_check(self): 
        """
        Sanity check for LINGAM, validates that the data on which it is run does not contain NaN values.

        :raises CausalDataException: throws exception in case data contains NaN values.
        """               
        if self.data.isna().any().any():
            raise  CausalDataException("Cannot apply Lingam on dataframe with NaN values, if using chain anchor please first filter the data to the desired variant")

    def run(self) ->CausalResultInfo:
        """
        Runs DirectLINGAM on the data the algorithm instance was initiated with, and returns result object containing LINGAM adjaceny matrix.

        :return: CausalResultInfo
        :rtype: CausalResultInfo
        """       
        #TODO implement differently with/without prior knowledge,target variables etc.  
        self.sanity_check()     
        if self.prior_knowledge is not None:
            model = lingam.DirectLiNGAM(prior_knowledge=self.prior_knowledge.getPriorKnowledge())    
        else:
            model = lingam.DirectLiNGAM()    
        model.fit(self.data)
        
        return CausalResultInfo(model.adjacency_matrix_,list(self.data.columns))
