# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Optional

import numpy as np
import pandas as pd

from sax.core.utils.constants import Constants
from ...causal_process_discovery.algorithms.positive_lingam import PositiveLingamImpl
from ...causal_process_discovery.algorithms.base_causal_alg import CausalResultInfo
from ...causal_process_discovery.algorithms.lingam import LingamImpl
from ...causal_process_discovery.causal_constants import DEFAULT_VARIANT, Algorithm
from ...causal_process_discovery.modalities.base_anchor import BaseAnchor
from ...causal_process_discovery.prior_knowledge import PriorKnowledge
from ...process_data.raw_event_data import RawEventData


class ParentAnchorTransformer(BaseAnchor):
    '''
    Parent Causal Modality - methods to apply causal discovery on event log with PARENT modality
    '''    

    
    def apply(self, dataObject: RawEventData,variant: Optional[Algorithm] = DEFAULT_VARIANT,prior_knowledge: Optional[bool]=False, depth: int=1) -> CausalResultInfo:
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        """
        Transpose the original event log so that each column is activity name and the value is the timestamp of the activity. Calculate all possible pairs of activities
        within this process and all its variants which happen one after the other. For each part, across all variants holding this pair, compute the time diff with the 
        parent activity of the pair. Apply causal discovery algorithm of the subframe defined by the parent activity and the pair of activities and the time diff between them. 
        This will be a single coefficient in the adjacenty matrix of the whole process. At the end create global adjacency matrix out of all coefficients.

        Parameters
        ----------
        dataObject : RawEventData
            event log data object
        variant : Optional[Algorithm], optional
            algorithm variant to apply, defaults to LINGAM
        prior_knowledge : Optional[bool], optional
            whether to apply prior knowledge, defaults to False
        depth : int, optional
            depth of the distance between activities to consider as pair, defaults to 1

        Raises
        ------
        TypeError
            The method can be applied only to an object of type RawEventData!

        Returns
        -------
        CausalResultInfo
            causal discovery result
        """

        if type(dataObject) not in [RawEventData]: raise TypeError("the method can be applied only to an object of type RawEventData!")
       
        transposed = dataObject.transposeToTabular()    
        #change the id field name
        transposed_df = transposed.getData()
        caseColumnName = transposed.getMandatoryProperties()[Constants.CASE_ID_KEY]
        #rename the current column name to constant
        transposed_df.rename(columns={caseColumnName: Constants.CASE_ID_KEY}, inplace=True)

        #variants = dataObject.getVariants()
        # apply the name of the variant to each caseid
        variants_keys = dataObject.getVariantsKeys()
        transposed_df = self._join_keys(transposed_df,variants_keys)
        # iterate over the variants. va
        # For the first variant create the first global adjacency matrix
        tuples_map={}
        start_time_column_name = transposed.getMandatoryProperties()[Constants.STARTTIME_COLUMN]
        for key, value in variants_keys.items():
            
            #translate the key to list of activities
            activity_list = key.rstrip(",").split(",")
            #TODO: extend the implementation of _compute_tuples so that includes all permutations of forward facing activities
            tuples = self._compute_tuples(start_time_column_name,activity_list,depth) #return an array of tuples where each tuple consists of pair of consecutive activities and the parent activity of this pair
            for parent_activity, child_tuple in tuples:                
                reversed_tuple = tuple(reversed(child_tuple))

                if (child_tuple in tuples_map) or (reversed_tuple in tuples_map): #TODO need to check either order                    
                    continue
    
                # Accessing individual elements within the inner tuple
                first_activity = child_tuple[0]
                second_activity = child_tuple[1]
                if first_activity == second_activity:
                    #handle rework
                    continue                
                coefficient = self._apply_lingam(transposed_df,start_time_column_name,variant,first_activity, second_activity,prior_knowledge)
                tuples_map[child_tuple] = coefficient
        global_adj_matrix,list_columns= self._build_global_adj_matrix(tuples_map)
        #return result object built from global matrix
        return CausalResultInfo(global_adj_matrix,list_columns)
    
    def _get_variant(self,row,variant_map):
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        """
        Get the process variant the given trace belongs to

        Parameters
        ----------
        row : pd.Series
            Row of the transposed data frame
        variant_map : dict
            Dictionary containing the variants and the caseIDs of the traces belonging to this variant

        Returns
        -------
        str
            Variant of the case
        """

        for variant, case_ids in variant_map.items():
            if row[Constants.CASE_ID_KEY] in case_ids:
                return variant
        return None

    def _join_keys(self,transposed_df,variants_keys)-> pd.DataFrame:    
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        """
        For each trace in the dataframe compute which variant it belongs to and assign the name of the variant of each trace in the 'variant' column

        Parameters
        ----------
        transposed_df : pd.DataFrame
            Transposed data frame
        variants_keys : dict
            Dictionary containing the variants and their respective keys

        Returns
        -------
        pd.DataFrame
            Data frame with variant names for each trace
        """
   
        # Apply the _get_variant method to each row in transposed_df        
        transposed_df['variant'] = transposed_df.apply(lambda row: self._get_variant(row, variants_keys), axis=1)      
        return transposed_df
    

    
    def _compute_tuples(self,start_time_column,activity_list, depth):    
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        """
        Compute all possible tuples of activities within the variant specified by list of activities where the distance between the activities is less or equal to given depth

        Parameters
        ----------
        start_time_column : str
            Name of the start time column
        activity_list : list
            List of activities
        depth : int
            Depth of the distance between tuples

        Returns
        -------
        list
            List of tuples of activities
        """

        result = []
        #adding start time column name as the first activitiy in the list for the purpose of calculating the pairs
        for i in range(len(activity_list) - 1):
            first_activity = activity_list[i]
            if (i == 0): parent_activity = start_time_column
            else : parent_activity = activity_list[i-1]
            j=0
            while (j < depth and i+j+1 <len(activity_list)):            
                second_activity = activity_list[i+j+1]
                child_tuple = (first_activity, second_activity)
                result.append((parent_activity, child_tuple))
                j+=1
        return result
    
    def _calculate_df(self, transposed_df, first_activity, second_activity, parent_activity):     
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        """
        Given the dataframe, build a sub-dataframe composed only of the given three columns, and then calculate the time difference between the parent activity and each of the two activities 
        for each trace.

        Parameters
        ----------
        transposed_df : pandas.DataFrame
            Transposed dataframe containing the events
        first_activity : str
            First activity in the tuple
        second_activity : str
            Second activity in the tuple
        parent_activity : str
            Parent activity in the tuple

        Returns
        -------
        pandas.DataFrame
            Dataframe containing the time differences
        """
   
        subset_df = transposed_df[[parent_activity, first_activity, second_activity]]
        subset_df_clean = subset_df.apply(pd.to_datetime, utc=True) 
        first_activity_time = subset_df_clean.min(axis=1)      
   
        # Create a new DataFrame for storing time differences
        time_difference_df = subset_df_clean.copy()
        for col in subset_df_clean.columns:
            time_difference_df[col] = (subset_df_clean[col] - first_activity_time).dt.total_seconds()*1000
        return time_difference_df

    def _get_parent_string(self, start_time_column, string_list, first_activity,second_activity):
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        """
        Get the parent string for a given pair of activities - activity which happens just before the earlies activity of the two. If there is no such activity
        (the given activities are the first in the process) then the start time is the "parent" activity

        Parameters
        ----------
        start_time_column : str
            name of the start time column
        string_list : list
            list of strings representing activities
        first_activity : str
            first activity in the tuple
        second_activity : str
            second activity in the tuple

        Returns
        -------
        str
            parent string
        """

        #need to accept also the start time
        #need to examine if first activity is the first activity in the list, and if so then the parent activity shoud be start time
        #there is a chance that right now this function will not be called for first activity..because parent is missing for such
        for i in range(len(string_list) - 1):
            if string_list[i] == first_activity or string_list[i] == second_activity:
                if i > 0: return string_list[i-1]
                else: return start_time_column
        return None  # Return None if the tuple is not found

    def _apply_lingam(self,transposed_df,start_time_column_name, alg_variant, first_activity,second_activity,prior_knowledge):  
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        """
        Apply Lingam algorithm on the given sub-data frame specified by the first activity and second activity column names. The time difference is calculated on 
        per variant basis (for all variants which have those activities) vrs parent activity in this variant. After time diff calculations, the chosen causal discovery algorithm
        is applied on this dataframe to produce adjacency matrix

        Parameters
        ----------
        transposed_df : pd.DataFrame
            data frame containing the event log data
        start_time_column_name : str
            name of the start time column - the column holding start time of each process case
        alg_variant : Algorithm
            algorithm variant to apply
        first_activity : str
            name of the first activity
        second_activity : str
            name of the second activity
        prior_knowledge : bool
            whether to apply prior knowledge

        Returns
        -------
        float
            coefficient of the causal relationship between the two activities
        """
        
        # retrieve a sub df with all variants where those activities are not NaN
        subset_df_clean = transposed_df.dropna(subset=[first_activity, second_activity])
        # retrive a list of variants for those cases
        result_list = subset_df_clean['variant'].unique()
        result_df = pd.DataFrame()
        # iterate over the variants
        for variant in result_list:
        # for each variants retrieve the name of parent activity (the activity preceeding the first activity or the second activity if the order is opposite) 
            activity_list = variant.rstrip(",").split(",")
            parent_activity = self._get_parent_string(start_time_column_name,activity_list,first_activity,second_activity)
            if parent_activity is None: continue         
            #take the variant sub df from the overall transposed df
            subset_variant_df = subset_df_clean[subset_df_clean['variant'] == variant]   
            # calculate sub df given the parent activity and the two activities columns                      
            new_df = self._calculate_df(subset_variant_df,first_activity,second_activity,parent_activity)
            new_column_names = ['Parent', first_activity, second_activity]
            new_df.columns = new_column_names
            # combine all dfs and apply lingam
            result_df = pd.concat([result_df, new_df], ignore_index=True)        
        # retrieve coefficient for our main columns
        num_rows = result_df.shape[0]
        #Given the two columns of time difference, apply Lingam    
        args = {"data": result_df}
        if prior_knowledge:
            args["prior_knowledge"] = PriorKnowledge(result_df)
        if num_rows > 0: 
            if alg_variant == Algorithm.LINGAM:
                algorithm = LingamImpl(**args)
            elif variant == Algorithm.POSITIVE_LINGAM:
                algorithm = PositiveLingamImpl(**args)
            try:
                result  = algorithm.run()     
                adjacency_matrix = result.getAdjacencyMatrix()
                return adjacency_matrix[2,1]             
            except Exception as e:
                print(e)                                
        return 0
         

 
    def _build_global_adj_matrix(self, coefficient_dict):
        # Assisted by WCA for GP
        # Latest GenAI contribution: granite-20B-code-instruct-v2 model
        """
        Build a global adjacency matrix from a dictionary of coefficients.

        Parameters
        ----------
        coefficient_dict : dict
            dictionary of coefficients

        Returns
        -------
        np.ndarray
            global adjacency matrix
        list
            list of unique elements
        """

        # Step 1: Identify unique elements
        unique_elements = set()
        for key in coefficient_dict.keys():
            unique_elements.update(key)

        # Step 2: Create an empty matrix with dimensions NxN
        num_nodes = len(unique_elements)
        adjacency_matrix = np.zeros((num_nodes, num_nodes))

        # Step 3: Populate the matrix with coefficients
        element_to_index = {element: index for index, element in enumerate(unique_elements)}
  
        for key, value in coefficient_dict.items():
            i, j = element_to_index[key[0]], element_to_index[key[1]]
            adjacency_matrix[j, i] = value  # Swap i and j

        return adjacency_matrix, list(unique_elements)

    

    

