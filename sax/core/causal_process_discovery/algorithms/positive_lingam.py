# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Optional

from pandas import DataFrame

from sax.core.causal_process_discovery.algorithms.base_causal_alg import BaseCausalAlgorithm, CausalDataException, \
    CausalResultInfo
from sax.core.causal_process_discovery.prior_knowledge import PriorKnowledge
import networkx as nx

from sax.core.causal_process_discovery.algorithms.positive_lingam import positive_direct_lingam

class PositiveLingamImpl(BaseCausalAlgorithm):
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
        #if self.data.isna().any().any():
        #    raise  CausalDataException("Cannot apply Lingam on dataframe with NaN values, if using chain anchor please first filter the data to the desired variant")

    def run(self) ->CausalResultInfo:
        """
        Runs DirectLINGAM on the data the algorithm instance was initiated with, and returns result object containing LINGAM adjaceny matrix.

        :return: CausalResultInfo
        :rtype: CausalResultInfo
        """       
        #TODO implement differently with/without prior knowledge,target variables etc.  
        self.sanity_check()     
        if self.prior_knowledge is not None:
            model = positive_direct_lingam.PositiveDirectLiNGAM(prior_knowledge=self.prior_knowledge.getPriorKnowledge())    
        else:
            model = positive_direct_lingam.PositiveDirectLiNGAM()
        full_columns_list = list(self.data.columns)
        if self.data.isna().any().any():
            full_graph = nx.DiGraph()
            for column in full_columns_list:
                full_graph.add_node(column)
            nan_columns = self.data.columns[self.data.isna().any()].tolist()
            #adjacency_matrix = [[0]* len(full_columns_list)] * len(full_columns_list)
            for nan_column in nan_columns:
                sub_data = self.data[~self.data[nan_column].isna()]
                sub_data = sub_data.dropna(axis=1)
                sub_columns_list = list(sub_data.columns)
                indecies_sub = [full_columns_list.index(i) for i in sub_columns_list]
                if len(sub_data) < 100:
                    continue

                if self.prior_knowledge is not None:
                    prior_knowledge = self.prior_knowledge.getPriorKnowledge()
                    sub_prior_knowledge = []

                    for i in indecies_sub:
                        to_add = []
                        for j in indecies_sub:
                            to_add.append(prior_knowledge[i][j])
                        sub_prior_knowledge.append(to_add)
                    sub_prior_knowledge = prior_knowledge[indecies_sub]
                    sub_prior_knowledge = sub_prior_knowledge[:, indecies_sub]

                    model = positive_direct_lingam.PositiveDirectLiNGAM(prior_knowledge=sub_prior_knowledge)
                model.fit(sub_data)
                new_adjacency_matrix = model.adjacency_matrix_
                new_graph = nx.from_numpy_array(new_adjacency_matrix, create_using=nx.DiGraph())
                num_to_name = {}
                for i in range(len(sub_columns_list)):
                    num_to_name[i] = sub_columns_list[i]
                new_graph = nx.relabel_nodes(new_graph, num_to_name)
                full_graph = nx.compose(full_graph, new_graph)
                #for first_column in list(sub_data.columns):
                #    for second_column in list(sub_data.columns):
                #        i = full_columns_list.index(first_column)
                #        j = full_columns_list.index(second_column)
                #        sub_i = sub_columns_list.index(first_column)
                #        sub_j = sub_columns_list.index(second_column)
                        
                #        adjacency_matrix[i][j] = max(adjacency_matrix[i][j], new_adjacency_matrix[sub_i][sub_j])

            return CausalResultInfo(nx.adjacency_matrix(full_graph).toarray(),list(self.data.columns))
        else:
            model.fit(self.data)
        
            return CausalResultInfo(model.adjacency_matrix_,list(self.data.columns))
    
