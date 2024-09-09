# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from itertools import chain
import pandas as pd
from typing import Dict
from typing import List
from typing import Optional


import graphviz
import networkx as nx
import numpy as np
from lingam.utils import make_dot

from sax.core.causal_process_discovery.algorithms.base_causal_alg import CausalResultInfo
from sax.core.causal_process_discovery.causal_constants import DEFAULT_MODALITY, DEFAULT_VARIANT, Algorithm, Modality
from sax.core.causal_process_discovery.modalities.chain_anchor import ChainAnchorTransformer
from sax.core.causal_process_discovery.modalities.parent_anchor import ParentAnchorTransformer

from sax.core.utils.constants import Constants
from sax.core.process_data.raw_event_data import RawEventData
import sax.core.process_mining.process_mining as pm

def discover_causal_dependencies_unification(dataObject:RawEventData,algorithm: Optional[Algorithm] = DEFAULT_VARIANT, modality: Optional[Modality] = DEFAULT_MODALITY,prior_knowledge: Optional[bool]=True, depth: int =1) -> CausalResultInfo:
    variants_dict = __get_variants_dict__(rawEventData=dataObject)
    results_per_variant =  __results_per_variants__(rawEventData=dataObject, variants_dict=variants_dict,modality=modality ,prior_knowledge=prior_knowledge, algorithm=algorithm)
    general_graph = __unification_of_results__(results=results_per_variant)


    return CausalResultInfo((nx.to_numpy_array(general_graph)).T, list(general_graph.nodes()))


def discover_causal_dependencies_unification_variant_specific(dataObject:RawEventData, variant:List[str],algorithm: Optional[Algorithm] = DEFAULT_VARIANT, modality: Optional[Modality] = DEFAULT_MODALITY,prior_knowledge: Optional[bool]=True, depth: int =1) -> CausalResultInfo:
    variant_sorted = sorted(variant)
    variant_set_str = str(variant_sorted)
    variants_dict = __get_variants_dict__(rawEventData=dataObject)
    variant_specific_dict = {}
    variant_specific_dict[variant_set_str] = variants_dict[variant_set_str]
    results_per_variant =  __results_per_variants__(rawEventData=dataObject, variants_dict=variant_specific_dict,modality=modality ,prior_knowledge=prior_knowledge, algorithm=algorithm)
    general_graph = __unification_of_results__(results=results_per_variant)


    return CausalResultInfo((nx.to_numpy_array(general_graph)).T, list(general_graph.nodes()))


def discover_causal_dependencies(dataObject:RawEventData,variant: Optional[Algorithm] = DEFAULT_VARIANT, modality: Optional[Modality] = DEFAULT_MODALITY,prior_knowledge: Optional[bool]=True, depth: int =1) -> CausalResultInfo:
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


def __get_variants_dict__(rawEventData:RawEventData) -> Dict[str,List[str]]:
    variants_dict = {}

    for sub_variant in rawEventData.getVariants():
        variant_list = sub_variant.split(',')
        variant_sorted = sorted(variant_list)
        variant_set_str = str(variant_sorted)
        if not variant_set_str in variants_dict.keys():
            variants_dict[variant_set_str] = [variant_list]
        else:
            variants_dict[variant_set_str].append(variant_list)

    return variants_dict


def __create_graph__(result, strength=0.48):
    mapping_index = {}
    for i, column in enumerate(result.getColumns()):
        mapping_index[i] = column

    np_matrix = np.array(result.getAdjacencyMatrix()).T

        # Create a boolean mask where True indicates that the value is below the p-value threshold
    mask = np_matrix < strength

    # Replace values below the p-value threshold with zeros
    np_matrix[mask] = 0
    #np_matrix = np.transpose(np_matrix)
    
    new_graph = nx.from_numpy_array(np_matrix, create_using=nx.DiGraph())
    new_graph = nx.relabel_nodes(new_graph, mapping_index)

    return new_graph


def __results_per_variants__(rawEventData : RawEventData, variants_dict: Dict[str, List[str]], modality:Optional[Modality] = Modality.CHAIN, prior_knowledge:Optional[bool]=True,algorithm: Optional[Algorithm] = DEFAULT_VARIANT)-> List[CausalResultInfo]:
    results = []
    current_mapping = rawEventData.getMandatoryProperties()
    for variant in variants_dict:
        variants_combined = []
        #find activities from other 
        for second_variant in variants_dict: 
            if set(variants_dict[variant][0]) <= set(variants_dict[second_variant][0]):
                for sub_variant in variants_dict[second_variant]:
                    sub_variant_str = ','.join(sub_variant)                    
                    or_variant = rawEventData.getVariant(sub_variant_str)
                    variant_df = or_variant.getData()
                    columns = variants_dict[variant][0]
                    variant_df = variant_df.reset_index()
                    variant_df = variant_df[variant_df[current_mapping[Constants.ACTIVITY_KEY]].isin(columns)][[current_mapping[Constants.CASE_ID_KEY], current_mapping[Constants.ACTIVITY_KEY], \
                                                                                                                current_mapping[Constants.TIMESTAMP_KEY], current_mapping[Constants.STARTTIME_COLUMN]]]
                    variants_combined.append(variant_df)
        combined_df = pd.concat(variants_combined, ignore_index=True)
        combined_df.columns = [Constants.CASE_ID_KEY, Constants.ACTIVITY_KEY, Constants.TIMESTAMP_KEY, Constants.START_BASE_COLUMN]
        combined_df = combined_df[combined_df[Constants.ACTIVITY_KEY]!= 'EVENT 6 THROW0']
        combined_df = combined_df[combined_df[Constants.ACTIVITY_KEY]!= 'EVENT 6 THROW']
        combined_event = pm.create_from_dataframe(combined_df,False,case_id=Constants.CASE_ID_KEY, activity_key=Constants.ACTIVITY_KEY, timestamp_key=Constants.TIMESTAMP_KEY, starttime_column=Constants.START_BASE_COLUMN)
        result_single = discover_causal_dependencies(combined_event, modality=modality, prior_knowledge=prior_knowledge, variant=algorithm)
        results.append(result_single)

    return results


def __unification_of_results__(results: List[CausalResultInfo]):
    all_columns = []
    for result in results:
        all_columns = all_columns + result.columns
    all_columns = list(set(all_columns))
    #all_columns.remove('EVENT 6 THROW0')
    #all_columns.remove('EVENT 6 THROW')

    G = nx.DiGraph()
    label = ''
    and_counter = 0
    xor_counter = 0
    or_counter = 0
    G.add_nodes_from(all_columns)
    
    for node in all_columns:
        current_sons = []
        label = ''
        mapper_inside_gates = {}

        for result in results:
            current_graph = __create_graph__(result, 0.4)
            if node in current_graph.nodes():
                sons_node = list(current_graph.successors(node))
                if sons_node in current_sons or len(sons_node)==0:
                        continue     
                else:
                    sons_node.sort()

                    current_sons.append(sons_node)
                    
    
        if len(current_sons) == 1:
            label = 'and'
        else:
            #find largest group of sons
            num_largest_group = 0
            largest_group = []
            for son_list in current_sons:
                if len(son_list) > num_largest_group:
                    num_largest_group = len(son_list)
                    largest_group = son_list
            changed = True
            while changed:
                changed = False
                all_son_list = list(set(list(chain.from_iterable(current_sons))))
                for i, first_son in enumerate(all_son_list[:-1]):
                    for second_son in all_son_list[(i+1):]:
                        change_to_add = True
                        #check if both of the selected sons appear togther in all of the graphs (if so we need to combine them into and because they always appear togther)
                        for son_list in current_sons:
                            if (first_son in son_list and not second_son in son_list) or (second_son in son_list and not first_son in son_list):
                                change_to_add = False
                                break
                        if change_to_add:
                            changed = True
                            #if one of the sons is and we combine the other with the and gate
                            if 'and_' in first_son:
                                new_node = first_son
                                G.add_edge(new_node, second_son, label=label)

                                for son_list in current_sons:
                                    if first_son in son_list:
                                        son_list.remove(second_son)
                            elif 'and_' in second_son:
                                new_node = second_son
                                G.add_edge(new_node, first_son, label=label)
                                
                                for son_list in current_sons:
                                    if first_son in son_list:
                                        son_list.remove(first_son)
                            #if none of the sons are and we create a and gate to combine them
                            else:
                                new_node = f'and_{and_counter}'
                                G.add_node(new_node)
                                and_counter+=1
                                G.add_edge(new_node, first_son, label=label)
                                G.add_edge(new_node, second_son, label=label)
                                for son_list in current_sons:
                                    if first_son in son_list:
                                        son_list.remove(first_son)
                                        son_list.remove(second_son)
                                        son_list.append(new_node) 




            #check if the gate should be or 
            label = 'xor'
            for i, son_list in enumerate(current_sons[:-1]):
                for current_son in current_sons[(i+1):]:
                    if set(son_list)<= set(current_son):
                        res = set(current_son) - set(son_list)
                        remove_func = False
                        for sub_set in current_sons[(i+1):]:
                            if set(sub_set) == res:
                                remove_func = True
                        if remove_func:
                            label = 'or'
                            current_sons.remove(current_son)
                            break
                    elif set(son_list) >= set(current_son):
                        res = set(son_list) - set(current_son)
                        remove_func = False
                        for sub_set in current_sons[(i+1):]:
                            if set(sub_set) == res:
                                remove_func = True
                        if remove_func:
                            label = 'or'
                            current_sons.remove(son_list)
                            break

        for sons_node in current_sons:
            if len(sons_node) >= 2:
                new_node = f'and_{and_counter}'
                G.add_node(new_node)
                and_counter+=1
                for son_node in sons_node:
                    G.add_edge(new_node, son_node, label=label)
                G.add_edge(node, new_node, label=label)
                sons_node.sort()
                mapper_inside_gates[str(sons_node)] = new_node            
                            
        connected_nodes = []
        to_remove = []
        for son_list in current_sons:
            should_add = True

            for insider in mapper_inside_gates.keys():
                son_list.sort()
                if insider == str(son_list):
                    should_add = False
                    connected_nodes.append(mapper_inside_gates[str(son_list)])
                    to_remove.append(mapper_inside_gates[str(son_list)])
            if should_add:
                connected_nodes = connected_nodes + son_list
        
        if len(connected_nodes) >=2 :
            if label == 'and':
                G.add_node(f'{label}_{and_counter}')
                new_node = f'{label}_{and_counter}'
                and_counter+=1
            if label == 'or':
                G.add_node(f'{label}_{or_counter}')
                new_node = f'{label}_{or_counter}'
                or_counter+=1
            if label == 'xor':
                G.add_node(f'{label}_{xor_counter}')
                new_node = f'{label}_{xor_counter}'
                xor_counter+=1
            G.add_edge(node, new_node, label=label)
            for parent in connected_nodes:
                G.add_edge(new_node, parent, label=label)
            for remove_node in to_remove:
                G.remove_edge(node, remove_node)
        elif len(connected_nodes) == 1:
            G.add_edge(node, connected_nodes[0])

    return G
