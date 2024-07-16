# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Optional

import graphviz
import numpy as np
from lingam.utils import make_dot

from sax.core.causal_process_discovery.algorithms.base_causal_alg import CausalResultInfo
from sax.core.causal_process_discovery.causal_constants import DEFAULT_MODALITY, DEFAULT_VARIANT, Algorithm, Modality
from sax.core.causal_process_discovery.modalities.chain_anchor import ChainAnchorTransformer
from sax.core.causal_process_discovery.modalities.parent_anchor import ParentAnchorTransformer
from sax.core.process_data.raw_event_data import RawEventData


def discover_causal_dependencies(dataObject:RawEventData,variant: Optional[Algorithm] = DEFAULT_VARIANT, modality: Optional[Modality] = DEFAULT_MODALITY,prior_knowledge: Optional[bool]=False, depth: int =1) -> CausalResultInfo:
    """
    Create causal execution dependency model for the given event log

    :param dataObject: event log
    :type dataObject: RawEventData
    :param variant: Algorithm to use for causal discovery, defaults to Lingam
    :type variant: Optional[Algorithm], optional
    :param modality: Anchor modality to use for discovery, defaults to CHAIN modality
    :type modality: Optional[Modality], optional
    :param prior_knowledge: whether to use prior knowledge, defaults to False
    :type prior_knowledge: Optional[bool], optional
    :raises TypeError: in case the event log is not of appropriate format
    :return: causal dependency model representation
    :rtype: CausalResultInfo
    """       
    # Perform causal discovery algorithm here and generate the dependencies            
    if type(dataObject) not in [RawEventData]: raise TypeError("the method can be applied only to an object of type RawEventData!")
    
    if modality == Modality.CHAIN:
        
        #check the required modality and invoke the relevant transformer with provided algorithm       
        result = ChainAnchorTransformer().apply(dataObject,variant,prior_knowledge)
    else : #modality parent
        result  = ParentAnchorTransformer().apply(dataObject,variant,prior_knowledge,depth) 

    return result     



def getDataCausalRepresentation(dataframe: RawEventData,modality,prior_knowledge,p_value_threshold):
        """
        The purpose of this function is to take a raw event log as input and output a dictionary representation of the causal model discovered from this event log.
        :param dataframe: A pandas dataframe containing the raw event log data.
        :type dataframe: RawEventData
        :return: A dictionary representing the causal model, where each key is a tuple representing a transition between two activities, and the value is the strength of that transition as determined causal discovery.
        :rtype: dict
        """
        causalModel = discover_causal_dependencies(dataObject=dataframe,modality=modality,prior_knowledge=prior_knowledge)
        causalPairs = getModelCausalRepresentation(causalModel,p_value_threshold)
        return causalPairs

def getModelCausalRepresentation(model,p_value_threshold):
    def _get_causal_graph_representation(result: CausalResultInfo,p_value_threshold=None):
        result_dict = {}
        np_matrix = result.getAdjacencyMatrix()
        if p_value_threshold is not None:
            np_matrix = np.array(np_matrix)

            # Create a boolean mask where True indicates that the value is below the p-value threshold
            mask = np_matrix < p_value_threshold 
            
            # Replace values below the p-value threshold with zeros
            np_matrix[mask] = 0

        for i, row in enumerate(np_matrix):
            for j, coefficient in enumerate(row):
                if coefficient != 0.0:
                    key = (result.columns[j], result.columns[i])
                    result_dict[key] = coefficient

        return result_dict
    causalRepresentation = _get_causal_graph_representation(model,p_value_threshold)
    return causalRepresentation

def view_causal_dependencies(dependencies: CausalResultInfo, p_value_threshold: float=None) ->graphviz.Digraph:
    """
    View the causal dependency model graph

    :param dependencies: causal dependency model representation
    :type dependencies: CausalResultInfo
    :param p_value_threshold: threshold for displaying causal relationships, no edges with coefficients less than specified will be displayed, defaults to None
    :type p_value_threshold: float, optional
    :return: graph
    :rtype: graphviz.Digraph
    """        
    # Convert the input matrix to a NumPy array for easier manipulation
    np_matrix = dependencies.getAdjacencyMatrix()
    if p_value_threshold is not None:
        np_matrix = np.array(np_matrix)

        # Create a boolean mask where True indicates that the value is below the p-value threshold
        mask = np_matrix < p_value_threshold 
        
        # Replace values below the p-value threshold with zeros
        np_matrix[mask] = 0
        
    return make_dot(np_matrix, labels = dependencies.getColumns())    
