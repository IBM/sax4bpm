# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import graphviz
import numpy as np

from pandas import DataFrame


class PriorKnowledge:
    """
    Prior knowledge representation for a particular event log. This object should be created and passed to the causal dependency discovery algorithm in case the user intends
    to run the algorithm with prior knowledge. The rules for creation of prior knowledge matrix are described here https://lingam.readthedocs.io/en/stable/tutorial/pk_direct.html
    """    
    def __init__(self,data: DataFrame, threshold=0.5):
        '''
        This class allows adding any prior knoweledge to the causal discovery process 
        '''
        self.prior_knowledge = self._assesPriorKnowledge(data, threshold=threshold)
        self.data = data

    def _assesPriorKnowledge(self,data: DataFrame,threshold = 0.5):      
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        '''
        Asses prior knowledge of the provided event log
        
        Parameters
        ----------
        data : pandas.DataFrame
            Event log data

        Returns
        -------
        np.ndarray
            Prior knowledge matrix
        '''
        prior_knowledge = np.eye(len(data.columns)) -1
        for ind1, column1 in enumerate(data.columns):
            for ind2, column2 in enumerate(data.columns):
                if column1!=column2 :
                    residuals = data[column1] - data[column2]
                    if ((residuals >= 0).sum()/ len(residuals))>=threshold:                        
                        prior_knowledge[ind2][ind1] = 0
        return prior_knowledge
    
    def getPriorKnowledge(self):
        """
        Get the prior knowledge matrix embedded in this object

        Returns
        -------
        np.ndarray
            Prior knowledge matrix
        """        
        return self.prior_knowledge
    
    def make_prior_knowledge_graph(self):
        """
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        Creates a graphviz.Digraph object representing the prior knowledge embedded in this object.

        Parameters
        ----------
        None

        Returns
        -------
        graphviz.Digraph
            Graphviz Digraph object representing the prior knowledge

        """        
        prior_knowledge_matrix = self.prior_knowledge
        d = graphviz.Digraph(engine='dot')

        labels = self.data.columns
        for label in labels:
            d.node(label, label)

        dirs = np.where(prior_knowledge_matrix > 0)
        for to, from_ in zip(dirs[0], dirs[1]):
            d.edge(labels[from_], labels[to])

        dirs = np.where(prior_knowledge_matrix < 0)
        for to, from_ in zip(dirs[0], dirs[1]):
            if to != from_:
                d.edge(labels[from_], labels[to], style='dashed')
        return d
       
    