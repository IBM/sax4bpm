# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import List
import pandas as pd
from pandas import DataFrame
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.conversion.log import converter as log_converter

from .data import BaseProcessDataObject
from .tabular_data import TabularEventData
from ..utils.constants import Constants, LifecycleTypes


class RawEventData(BaseProcessDataObject):
    
    """
    Raw event representation of event log, where each row represents a single event in a trace (one activity), and the columns
    are the activity name, activity timestamp, and additional activity payload attributes

    """    

    _permutations = None
    def __init__(self,data:DataFrame, mandatory_properties:dict,optional_properties:dict):           
        """
        Initializes a SAX raw event object.

        Parameters
        ----------
        data : pandas.DataFrame
            The input event log
        mandatory_properties : dict
            A dictionary containing the constants of the mandatory properties as keys and the names of corresponding columns in the dataframe
        optional_properties : dict
            A dictionary containing the names of the optional properties as keys and the names of corresponding columns in the dataframe

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If any of the input arguments are not of the expected type.
        ValueError
            If any of the input arguments do not have the expected value.
        """   
        super().__init__(data=data,mandatory_properties=mandatory_properties,optional_properties =optional_properties)        
        self._initLog() 


        
    def copy(self):
        """
        Creates a copy of the current RawEventData object.

        Returns
        -------
        copied_object : RawEventData
            A copy of the current RawEventData object.

        """
        # Call the copy method of the base class
        copied_base_object = super().copy()
        # Cast the copied object to RawEventData
        copied_object = RawEventData(copied_base_object.data,
                                      copied_base_object.mandatory_properties,
                                      copied_base_object.optional_properties)      
        return copied_object

    def _filter_dataframe(self, original_dataframe, column_dict):
        """
        Filters a dataframe based on a column names provided in the input dictionary.

        Parameters
        ----------
        original_dataframe : pandas.DataFrame
            The original dataframe to be filtered.
        column_dict : dict
            A dictionary mapping column names to property names.

        Returns
        -------
        subset_dataframe : pandas.DataFrame
            A filtered version of the original dataframe.

    """
        relevant_columns = [col for col in original_dataframe.columns if col in column_dict.values()]
        subset_dataframe = original_dataframe[relevant_columns]
        return subset_dataframe
    
    # Filter the event log according to the specified lifecycle transition types
    def filterLifecycleEvents(self, lifecycleTypes)->'RawEventData':
        """
        Filter the data according to the provided list of desired event lifecycle types, and return a new data object containing only the chosen lifecycle event types

        Parameters
        ----------
        lifecycleTypes : List of chosen lifecycleTypes events (such as 'complete')
        type lifecycleTypes: List

        Returns
        -------
        a new dataobject containing only the chosen event types
        rtype: RawEventData

        """                        
        if lifecycleTypes is None:
            lifecycleTypes = [LifecycleTypes.COMPLETE.value]
        filtered_df = self.data[self.data[self.mandatory_properties[Constants.TYPE_KEY]].str.lower().isin(lifecycleType.lower() for lifecycleType in lifecycleTypes)]   
        return RawEventData(filtered_df, self.mandatory_properties, self.optional_properties)
    
    def getVariants(self)->dict:
        """
        Get all variants in the event log, along with number of traces for each variant

        Returns
        -------
        A dictionary where each key represents a variant name, which is a comma-separated list of all activities in the variant in the order of occurence,and the corresponding value is the number of traces for that variant.

        """
        self._permutations = self._getVariants()        
        count_dict = {key: len(value) for key, value in self._permutations.items()}        
        return count_dict
    
    def getVariantsKeys(self)->dict:
        """
        Get the names of all variants in the event log

        Returns
        -------
        A dictionary where each key represents a variant name, which is a comma-separated list of all activities in the variant in the order of occurence, and the corresponding value is a list of all traces case-ids in this variant.

        """
        self._permutations = self._getVariants()        
        return self._permutations
    
    def _getVariants(self)->dict:
        """
        Build a dictionary representing all process variants in the event log using process mining techniques

        Returns
        -------
        A dictionary where each key represents a variant name joined from all activities within the variant in the order of occurence, and the corresponding value is a list of all trace case-ids in this variant.

        """
        data_map = {}

        if Constants.TYPE_KEY in self.getMandatoryProperties():               
            event_log= self.filterLifecycleEvents([LifecycleTypes.COMPLETE.value])
        else:
            event_log = self
                                   
        formatted_log = event_log.getLog()
        variants = variants_filter.get_variants(formatted_log)

        trace_variant_index=list(variants.keys())
        data_map={}
        for idx, key in enumerate(trace_variant_index):
            case_variant_link=[]
            for trace in variants[key]:
                    case_variant_link.append(trace.attributes[Constants.ACTIVITY_KEY])
            #converting the tuple to string value            
            string_key=",".join(key)
            data_map[string_key]=case_variant_link
        return data_map    
 
        
            
    def getMandatoryPropertiesData(self):
        """
        Return the mandatory properties columns: caseID, activity and event lifecycle columns and timestamp columns
        
        Parameters
        ----------
        None

        Returns
        -------        
        :return: mandatory properties data
        :rtype: _type_
        """        
        return self._filter_dataframe(self.data, self.mandatory_properties)
    
    def getOptionalPropertiesData(self):
        """
        Return the mandatory properties columns: caseID, activity and event lifecycle columns and timestamp columns
        
        Parameters
        ----------
        None

        Returns
        -------        
        :return: mandatory properties data
        :rtype: _type_
        """        
        return self._filter_dataframe(self.data, self.optional_properties)
    
    def _initLog(self):
        """
        Validates that the data in the object is proper event log - has all the mandatory columns, the values of which are of the proper type

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        df = self.getData().copy()
        if type(df) not in [pd.DataFrame]: raise Exception("The method can be applied only to a dataframe!")

        case_id = self.mandatory_properties[Constants.CASE_ID_KEY]
        activity_key = self.mandatory_properties[Constants.ACTIVITY_KEY]
        timestamp_key = self.mandatory_properties[Constants.TIMESTAMP_KEY]
    
        if case_id not in df.columns:
            raise Exception(case_id + " column (case ID) is not in the dataframe!")
        if activity_key not in df.columns:
            raise Exception(activity_key + " column (activity) is not in the dataframe!")
        if timestamp_key not in df.columns:
            raise Exception(timestamp_key + " column (timestamp) is not in the dataframe!")
   
        # make sure the case ID column is of string type
        df[case_id] = df[case_id].astype("string")
        # make sure the activity column is of string type
        df[activity_key] = df[activity_key].astype("string")

        self.data = df
   
    def getLog(self): 
        """
        Return the pm4py event log representing this dataframe object

        Parameters
        ----------
        None

        Returns
        -------
        log : pm4py event log
            The pm4py event log representing this dataframe object

        """     
        df = self.getData().copy()
        if type(df) not in [pd.DataFrame]: raise Exception("The method can be applied only to a dataframe!")

        case_id = self.mandatory_properties[Constants.CASE_ID_KEY]
        activity_key = self.mandatory_properties[Constants.ACTIVITY_KEY]
        timestamp_key = self.mandatory_properties[Constants.TIMESTAMP_KEY]
    
        if case_id not in df.columns:
            raise Exception(case_id + " column (case ID) is not in the dataframe!")
        if activity_key not in df.columns:
            raise Exception(activity_key + " column (activity) is not in the dataframe!")
        if timestamp_key not in df.columns:
            raise Exception(timestamp_key + " column (timestamp) is not in the dataframe!")
   
   
        # make sure the case ID column is of string type
        df[case_id] = df[case_id].astype("string")
        # make sure the activity column is of string type
        df[activity_key] = df[activity_key].astype("string")
   
        name_mapping = {
            case_id: Constants.CASE_ID_KEY,
            activity_key: Constants.ACTIVITY_KEY,
             timestamp_key: Constants.TIMESTAMP_KEY       
        }

        # Rename the columns using the dictionary
        df.rename(columns=name_mapping, inplace=True)       
        return log_converter.apply(df)
    

    from typing import List

    def filterVariants(self, variant_keys: List[str]) -> 'RawEventData':   
        """
        Get specific variants data for specified variants and return a new RawEventData object only with the filtered variants data.

        Parameters
        ----------
        variant_keys : List[str]
            The list of variant names to retrieve.

        Returns
        -------
        variant : RawEventData
            The RawEventData object representing the specified variant subset of traces.
        """            
        if self._permutations is None:
            self._permutations = self._getVariants()

        # Initialize an empty set to store all chosen_ids across variant_keys
        all_chosen_ids = set()

        # Iterate over each key to collect the chosen_ids
        for variant_key in variant_keys:
            if variant_key in self._permutations:
                chosen_ids = self._permutations[variant_key]
                all_chosen_ids.update(chosen_ids)
            else:
                raise KeyError(f"Variant key '{variant_key}' not found in variants")

        # Filter the dataframe for rows that match any of the chosen_ids
        id_columns = self.data[self.mandatory_properties[Constants.CASE_ID_KEY]]        
        selected_df = self.data[id_columns.isin(all_chosen_ids)]                         
        original_df = selected_df.copy()

        # Return the new RawEventData object with the filtered data
        return RawEventData(original_df, self.mandatory_properties, self.optional_properties)

    # def _getVariant(self, variant_key) -> 'RawEventData':   
    #     """
    #     Get a specific variant data and return a new RawEventData object only with the filtered variant data.

    #     Parameters
    #     ----------
    #     variant_key : str
    #         The name of the variant to retrieve.

    #     Returns
    #     -------
    #     variant : RawEventData
    #         The RawEventData object representing the specified variant subset of traces.

    #     """            
    #     if self._permutations is None:
    #         self._permutations = self._getVariants()

    #     chosen_ids = self._permutations[variant_key]        
    #     id_columns = self.data[self.mandatory_properties[Constants.CASE_ID_KEY]]        
    #     selected_df = self.data[id_columns.isin(chosen_ids)]                         
    #     original_df = selected_df.copy()       
        
    #     return RawEventData(original_df, self.mandatory_properties, self.optional_properties)        
    
    
    
    def transposeToTabular(self) -> TabularEventData:
        """
        Transposes the provided event log data object to a new data object where each trace is represented by a single row (instead of a row per activity),
         where the columns are activity names and the values in the columns are the timestamps of those activities end time.

        Returns
        -------
        data object in tabular format : TabularEventData
            A new data object in tabular format.

        """      
        
        dataFrame = self.getData()
        mandatory_propreties = self.getMandatoryProperties()              
        optional_properties_list =  list(self.getOptionalProperties().values())

        if Constants.TYPE_KEY in mandatory_propreties:
            columns_list = [mandatory_propreties[Constants.CASE_ID_KEY],mandatory_propreties[Constants.ACTIVITY_KEY],mandatory_propreties[Constants.TYPE_KEY],mandatory_propreties[Constants.TIMESTAMP_KEY]]
        else:
            columns_list = [mandatory_propreties[Constants.CASE_ID_KEY],mandatory_propreties[Constants.ACTIVITY_KEY],mandatory_propreties[Constants.TIMESTAMP_KEY]]
        columns_list+=optional_properties_list  
                

        new_df= self._flat_sources_updated(dataFrame,optional_properties_list,mandatory_propreties)

        id_column= mandatory_propreties[Constants.CASE_ID_KEY]
        start_time_column = mandatory_propreties[Constants.STARTTIME_COLUMN]       
        
        unique_start_times = dataFrame[[id_column, start_time_column]].drop_duplicates(subset=id_column, keep='first')              
        new_df = pd.merge(new_df,unique_start_times, on = id_column, how='left')
        new_df = new_df[[id_column,  start_time_column] + [col for col in new_df.columns if col not in [id_column, start_time_column]]]

        mandatory_columns_names,optional_column_names = self._extract_properties(new_df,self.getMandatoryProperties())

        new_df = new_df.reset_index(drop=True)   
        
        
        return  TabularEventData(new_df,mandatory_columns_names,optional_column_names)
    
    def transposeFullDataframe(self) -> DataFrame:
        mandatory_properties = self.getMandatoryProperties()
        transposedMandatory = self.transposeToTabular().getData()
        transposedOptional = self._transposeToTabularOptionalProperties()
        merged_df = pd.merge(transposedMandatory, transposedOptional, on=mandatory_properties[Constants.CASE_ID_KEY], how='inner')
        return merged_df
    
    def _transposeToTabularOptionalProperties(self) -> DataFrame:
        mandatory_properties = self.getMandatoryProperties()
        optional_properties = self.getOptionalProperties()
        
        new_data = {}
        df = self.getData()
        for _, row in df.iterrows():
            case_id = row[mandatory_properties[Constants.CASE_ID_KEY]]
            activity = row[mandatory_properties[Constants.ACTIVITY_KEY]]
    
            if case_id not in new_data:
                new_data[case_id] = {}
    
            for column in df.columns:
                if column != mandatory_properties[Constants.CASE_ID_KEY] and column != mandatory_properties[Constants.ACTIVITY_KEY] and column in optional_properties:
                    new_column_name = f"{activity}_{column}"
                    new_data[case_id][new_column_name] = row[column]
        
        new_df = pd.DataFrame.from_dict(new_data, orient='index').reset_index().rename(columns={'index': mandatory_properties[Constants.CASE_ID_KEY]})
        print(new_df)
        return new_df

    def _flat_sources_updated(self,x,columns,mandatory_propreties) -> DataFrame:
        """
        Pivots the dataframe and returns a new dataframe with the pivoted data.

        Parameters
        ----------
        x : DataFrame
            The input dataframe to be pivoted.
        columns : list
            A list of column names to be used as the new column names.
        mandatory_propreties : dict
            A dictionary containing the mandatory properties of the data object.

        Returns
        -------
        DataFrame
            A new dataframe with the pivoted data.

        """
        # Pivot the dataframe
        new_x = pd.DataFrame() 
        #get variants in this dataframe and perform this for each variant        
        Id_column_name = mandatory_propreties[Constants.CASE_ID_KEY]
        Activity_column_name = mandatory_propreties[Constants.ACTIVITY_KEY]
        Timestamp_column_name = mandatory_propreties[Constants.TIMESTAMP_KEY]
        #taking care of loops - taking the last loop
        #TODO: add function with config how to treat loops. Possible option: last loop, remove variants with loops altogether, "open" loops. Right now takes max timestamp value - last occurence
        pivoted_df = x.pivot_table(index=Id_column_name, columns=Activity_column_name, values=Timestamp_column_name, aggfunc='max', fill_value=None)


        # Reset index to make 'caseId' a column again
        pivoted_df.reset_index(inplace=True)

        # Rename the columns
        pivoted_df.columns.name = None  # Remove the name of the columns index
        pivoted_df.columns = [Id_column_name] + pivoted_df.columns[1:].tolist()
        return pivoted_df


       
        
        
                        
        



        