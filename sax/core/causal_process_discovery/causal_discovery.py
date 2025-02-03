# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import collections
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


def discover_causal_dependencies(dataObject:RawEventData,variants: Optional[List[str]] = None, algorithm: Optional[Algorithm] = DEFAULT_VARIANT, modality: Optional[Modality] = DEFAULT_MODALITY,prior_knowledge: Optional[bool]=True, threshold: Optional[float]=0.5,depth: int =1) -> CausalResultInfo:
    """
    Create causal execution dependency model for the given event log represented by the dataobject

    :param dataObject: event log
    :type dataObject: RawEventData 
    :param variants: a List of one or more variant specifications to perform causal discovery on , optional (if not specified will perform causal discovery on the whole event log)
    :type variants:  Optional[List[str]], optional
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
    if variants is None:
        return _discover_causal_dependencies_unification(dataObject=dataObject,algorithm=algorithm,modality=modality,prior_knowledge=prior_knowledge,threshold=threshold,depth=depth)
    else:
        # Handle case where variants is provided
        return _discover_causal_dependencies_unification_variant_specific(dataObject=dataObject,variants=variants,algorithm=algorithm,modality=modality,prior_knowledge=prior_knowledge,threshold=threshold,depth=depth)



def _discover_causal_dependencies_unification(dataObject:RawEventData,algorithm: Optional[Algorithm] = DEFAULT_VARIANT, modality: Optional[Modality] = DEFAULT_MODALITY,prior_knowledge: Optional[bool]=True, threshold: Optional[float]=0.5,depth: int =1) -> CausalResultInfo:
    variants_dict = __get_variants_dict__(rawEventData=dataObject)
    results_per_variant =  __results_per_variants__(rawEventData=dataObject, variants_dict=variants_dict,modality=modality ,prior_knowledge=prior_knowledge, threshold=threshold,algorithm=algorithm)
    general_graph = __unification_of_results__(results=results_per_variant)


    return CausalResultInfo((nx.to_numpy_array(general_graph)).T, list(general_graph.nodes()))




def _discover_causal_dependencies_unification_variant_specific(dataObject:RawEventData, variants:List[str],algorithm: Optional[Algorithm] = DEFAULT_VARIANT, modality: Optional[Modality] = DEFAULT_MODALITY,prior_knowledge: Optional[bool]=True, threshold: Optional[float]=0.5,depth: int =1) -> CausalResultInfo:
    results_per_variants = []
    for variant_str in variants:
        variant = variant_str.split(",")
        variant_sorted = sorted(variant)
        variant_set_str = str(variant_sorted)
        variants_dict = __get_variants_dict__(rawEventData=dataObject)
        variant_specific_dict = {}
        variant_specific_dict[variant_set_str] = variants_dict[variant_set_str]
        results_per_variant =  __results_per_variants__(rawEventData=dataObject, variants_dict=variant_specific_dict,modality=modality ,prior_knowledge=prior_knowledge, threshold=threshold,algorithm=algorithm)
        general_graph = __unification_of_results__(results=results_per_variant)
        results_per_variants.append(CausalResultInfo((nx.to_numpy_array(general_graph)).T, list(general_graph.nodes())))

    if len(results_per_variants)>1:
        general_graph = __unification_of_results__(results=results_per_variants)

    return CausalResultInfo((nx.to_numpy_array(general_graph)).T, list(general_graph.nodes()))



def _discover_causal_dependencies(dataObject:RawEventData,variant: Optional[Algorithm] = DEFAULT_VARIANT, modality: Optional[Modality] = DEFAULT_MODALITY,prior_knowledge: Optional[bool]=True, threshold: Optional[float]=0.5,depth: int =1) -> CausalResultInfo:
    """
    Internal method -create causal execution dependency model for the given event log

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
        result = ChainAnchorTransformer().apply(dataObject,variant,prior_knowledge,threshold)
    else : #modality parent
        result  = ParentAnchorTransformer().apply(dataObject,variant,prior_knowledge,depth, threshold) 

    return result     



def get_data_causal_representation(dataframe: RawEventData, modality,prior_knowledge,p_value_threshold,variants: Optional[List[str]] = None):
        """
        The purpose of this function is to take a raw event log as input and output a dictionary representation of the causal model discovered from this event log.
        :param dataframe: A pandas dataframe containing the raw event log data.
        :type dataframe: RawEventData
        :param modality: Anchor modality to use for discovery, defaults to CHAIN modality
        :type modality: Optional[Modality], optional
        :param prior_knowledge: whether to use prior knowledge, defaults to False
        :type prior_knowledge: Optional[bool], optional   
        :param p_value_threshold: a threshold for casual strength coefficient, edges with weights bellow this coefficient will not be presented
        :type p_value_threshold: float
        :param variants: a List of one or more variant specifications to perform causal discovery on , optional (if not specified will perform causal discovery on the whole event log)
        :type variants:  Optional[List[str]], optional
        :return: A dictionary representing the causal model, where each key is a tuple representing a transition between two activities, and the value is the strength of that transition as determined causal discovery.
        :rtype: dict
        """
        causalModel = discover_causal_dependencies(dataObject=dataframe,variants=variants,modality=modality,prior_knowledge=prior_knowledge)
        causalPairs = get_model_causal_representation(causalModel,p_value_threshold)
        return causalPairs



def get_model_causal_representation(model,p_value_threshold):
    """
    The purpose of this function is to take a causal model which is an adjacency matrix and create a dictionary representing this model, optionally filtering out edges with coefficient weights below specified threshold.
    :param model The causal model represented by CausalResultInfo object
    :type model CausalResultInfo
    :param p_value_threshold: a threshold for casual strength coefficient, edges with weights bellow this coefficient will not be presented
    :type p_value_threshold: float

    :return: A dictionary representing the causal model, where each key is a tuple representing a transition between two activities, and the value is the strength of that transition as determined causal discovery.
    :rtype: dict
    """    
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
        
        dot = make_dot(np_matrix, labels = dependencies.getColumns())

    for i, line in enumerate(dot.body):
        if '->' in line:  # Check if the line represents an edge
            if '[' in line and 'label=' in line:  # Check for edge attributes
                # Remove the label attribute while keeping other attributes
                parts = line.split('[')
                edge_definition = parts[0]
                attributes = parts[1] if len(parts) > 1 else ''
                # Remove label attribute
                new_attributes = ','.join(attr for attr in attributes.split(',') if not attr.strip().startswith('label='))
                dot.body[i] = '\t' + edge_definition.strip() + (' [' + new_attributes + ']' if new_attributes else '') + '\n'
    # Update nodes with labels starting with "and", "or", "xor" to have a diamond shape
    # Update nodes with prefixes "and", "or", "xor" to have a diamond shape
    
        # Check for node definitions (ignore edges and other elements)
        if '->' not in line and not line.strip().startswith("{"):
            # Extract the node name (strip quotes if present)
            node_name = line.split()[0]#.strip('"')
            # Check if the node name starts with the desired prefixes
            if node_name.startswith(("AND", "or", "XOR", "OR")):
                # Add the diamond shape to the node
                if "[" in line:  # If attributes already exist
                    dot.body[i] = line.replace("[", "[shape=diamond, ")
                else:  # Add attributes if none exist
                    dot.body[i] = f'{line[:-1]} [shape=diamond]\n'

    return dot    


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


def __results_per_variants__(rawEventData : RawEventData, variants_dict: Dict[str, List[str]], modality:Optional[Modality] = Modality.CHAIN, prior_knowledge:Optional[bool]=True,threshold: Optional[float]=0.5,algorithm: Optional[Algorithm] = DEFAULT_VARIANT)-> List[CausalResultInfo]:
    results = []
    current_mapping = rawEventData.getMandatoryProperties()
    for variant in variants_dict:
        variants_combined = []
        #find activities from other 
        for second_variant in variants_dict: 
            if set(variants_dict[variant][0]) <= set(variants_dict[second_variant][0]):
                for sub_variant in variants_dict[second_variant]:
                    sub_variant_str = ','.join(sub_variant)                    
                    or_variant = rawEventData.filterVariants([sub_variant_str])
                    variant_df = or_variant.getData()
                    columns = variants_dict[variant][0]
                    variant_df = variant_df.reset_index()
                    #why do i need this?
                    variant_df = variant_df[variant_df[current_mapping[Constants.ACTIVITY_KEY]].isin(columns)][[current_mapping[Constants.CASE_ID_KEY], current_mapping[Constants.ACTIVITY_KEY], \
                                                                                                                current_mapping[Constants.TIMESTAMP_KEY], current_mapping[Constants.TIMESTAMP_KEY]]]
                    variants_combined.append(variant_df)
        combined_df = pd.concat(variants_combined, ignore_index=True)
        combined_df.columns = [Constants.CASE_ID_KEY, Constants.ACTIVITY_KEY, Constants.TIMESTAMP_KEY, Constants.START_BASE_COLUMN]
        combined_event = pm.create_from_dataframe(combined_df,False,case_id=Constants.CASE_ID_KEY, activity_key=Constants.ACTIVITY_KEY, timestamp_key=Constants.TIMESTAMP_KEY, starttime_column=Constants.START_BASE_COLUMN)
        if len(combined_df) > len(combined_df.columns):
            try:
                result_single = _discover_causal_dependencies(combined_event, modality=modality, prior_knowledge=prior_knowledge, threshold=threshold,variant=algorithm)
                results.append(result_single)
            except Exception:
                pass

    return results


def __simplify_descendants__(descendants_list, G, or_counter, permmisive=True):
    while True:
        merged = False
        # Sort descendants_list by length of sublists, descending order
        descendants_list = sorted(descendants_list, key=len, reverse=True)
        for i, current_list in enumerate(descendants_list):
            # Find all sublists of the current list in descendants_list
            sublists = [lst for lst in descendants_list if set(lst).issubset(set(current_list))]
            print(f'we start from {current_list}')
            print(f'all the sons are {sublists}')
            # Restrictive OR Gate
            if len(sublists) == 2**len(current_list)-1 and len(sublists) != 1:
                merged = True

                # Remove all the sublists and the current list from descendants_list
                descendants_list = [lst for lst in descendants_list if lst not in sublists]

                # Create a new OR node
                or_node = f"OR_{or_counter}"
                or_counter += 1
                G.add_node(or_node)

                # Connect all elements of the removed sublists to the new OR node
                for node in current_list:
                    G.add_edge(or_node, node)

                # Add the new OR node to descendants_list
                descendants_list.append([or_node])

                break  # Restart the process to ensure recursive merging

        if not merged:
            break
    # Permissive OR Gate
    if permmisive:
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        while True:
            merged = False
            #Sort descendants_list by length of sublists, descending order
            descendants_list = sorted(descendants_list, key=len, reverse=True)
            for i, current_list in enumerate(descendants_list):
                sublists = [lst for lst in descendants_list if set(lst).issubset(set(current_list))]
                #this is where we flat the list of descentdents
                flat_list = [
                    x
                    for xs in sublists
                    for x in xs
                ]
                flat_list = list(set(flat_list))

                if len(current_list) > 1 and compare(current_list, flat_list):
                    merged = True

                    # Remove identified sublists and the current list from descendants_list
                    descendants_list = [lst for lst in descendants_list if lst not in sublists]

                    # Create a new OR node
                    or_node = f"or_{or_counter}"
                    or_counter += 1
                    G.add_node(or_node)

                    # Connect all elements of the removed sublists to the new OR node
                    for node in current_list:
                        G.add_edge(or_node, node)

                    # Add the new OR node to descendants_list
                    descendants_list.append([or_node])

            # Restart the process to ensure recursive merging
            if not merged:
                break


    return descendants_list, G, or_counter

# Step 1: XOR Check
def xor_check(family_of_sets):
    for i in range(len(family_of_sets)):
        for j in range(i + 1, len(family_of_sets)):
            if family_of_sets[i].intersection(family_of_sets[j]):
                return False  # XOR condition fails
    return True  # XOR condition satisfied

# Step 2: Exhaustive OR Check
def exhaustive_or_check(family_of_sets):
    # Step 1: Compute the universal set
    universal_set = set().union(*family_of_sets)
    
    # Step 2: Generate the powerset of U
    num_of_expected = 2**len(universal_set) - 1
    
    # Step 3: Compare with the input family
    return len(family_of_sets) == num_of_expected, universal_set

# Step 3.1: Partial Intersection Check with Propagation
def partial_intersection_check_with_propagation(family_of_sets, and_counter):
    updated_family = []
    replacements = {}  # Track replacements of sets with their concatenated labels
    
    # Step 1: Check each set
    for S_i in family_of_sets:
        if len(S_i) <= 1:  # Skip single-element sets
            updated_family.append(S_i)
            continue
        
        partially_intersects = False
        for S_j in family_of_sets:
            if S_i == S_j:
                continue
            if S_i.intersection(S_j) and S_i - S_j:  # Partial intersection check
                partially_intersects = True
                break
        
        if partially_intersects:
            updated_family.append(S_i)  # Retain original set
        else:
            # Replace with concatenated label
            label = f'AND_{and_counter}'  # Create a concatenated label
            and_counter += 1
            replacements[label] = frozenset(S_i)  # Map original set to its replacement
            updated_family.append({label})
    
    # Step 2: Propagate replacements
    final_family = []
    for S in updated_family:
        new_set = set()
        for element in S:
            # Replace element if it belongs to a replaced set
            added = False
            for replacement_set, original_set in replacements.items():
                if element in original_set:
                    new_set.update({replacement_set})
                    added = True
                    break
            if not added:
                new_set.add(element)
        final_family.append(new_set)
    
    return final_family, replacements, and_counter

# Combined Algorithm
def process_family_of_sets(family_of_sets, and_counter):
    # Step 1: create AND gates
    revised_family, replacements, and_counter = partial_intersection_check_with_propagation(family_of_sets, and_counter)
    if len(revised_family)==1 and len(revised_family[0])==1:
        return "", revised_family, and_counter, replacements, {}
    # Step 2: XOR Check on Revised Family
    if xor_check(revised_family):
        return "XOR", revised_family, and_counter, replacements, {}
    
    # Step 3: Exhaustive OR Check on Revised Family
    result_or = exhaustive_or_check(revised_family)
    if result_or[0]:
        return "EOR", result_or[1], and_counter, replacements, {}
    
    # If all checks fail
    return "OR", result_or[1], and_counter, replacements, revised_family


def __unification_of_results__(results: List[CausalResultInfo]) -> nx.DiGraph:
    # 1) Gather all unique columns
    all_columns = []
    for result in results:
        all_columns += result.columns
    all_columns = list(set(all_columns))

    # 2) Create empty DiGraph
    G = nx.DiGraph()
    G.add_nodes_from(all_columns)  # Add your “data” nodes

    # Gate counters
    and_counter = 0  # In case you need AND
    xor_counter = 0
    or_counter = 0
    OR_counter = 0

    # 3) Iterate over all the nodes in the original (unified) set
    for node in all_columns:
        # Collect child sets from each graph
        child_sets = []
        for result in results:
            current_graph = __create_graph__(result, 0.4)
            if node in current_graph.nodes():
                successors_list = list(current_graph.successors(node))
                if len(successors_list) == 0:
                    continue
                # Convert to a set for easier logic
                successors_set = set(successors_list)
                if successors_set not in child_sets:
                    child_sets.append(successors_set)

        # If node has no children in any graph, skip
        if not child_sets:
            continue

        # If exactly 1 child set, just connect directly, no gate

        #if len(child_sets) == 1:
        #    print(f'we got from {node} to {child_sets}')
        #    for child in child_sets[0]:
        #        G.add_edge(node, child)
        #    continue
        # 4) Decide which gateway to create
        type_gate, child_desendents, and_counter, replacements, dict_for_or = process_family_of_sets(child_sets, and_counter)
        if type_gate == 'XOR':
            gate_label = f'XOR_{xor_counter}'
            xor_counter+=1
            G.add_node(gate_label)
        elif type_gate == 'EOR':
            gate_label = f'OR_{OR_counter}'
            OR_counter+=1
            G.add_node(gate_label)
        elif type_gate == 'OR':
            gate_label = f'or_{or_counter}'
            or_counter+=1
            G.add_node(gate_label)
        for replacement, original_set in replacements.items():
            G.add_node(replacement)
            for item in original_set:
                G.add_edge(replacement, item)
            if type_gate == "":
                G.add_edge(node, replacement)
        if type_gate != '':
            for desendent in child_desendents:
                if len(desendent) > 0:
                    if type(desendent) is set:
                        for item in desendent:
                            G.add_edge(gate_label, item)    
                    else:
                        G.add_edge(gate_label, desendent)
        
            G.add_edge(node, gate_label)
        elif len(replacements) == 0 and len(child_desendents)==1:
            G.add_edge(node,list(child_desendents[0])[0])

    return G
