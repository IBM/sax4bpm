# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Any, Dict, Tuple, List

import pandas as pd
from pandas import DataFrame

from sax.core.utils.constants import Constants


class BaseProcessDataObject:
    '''
    Data object for process event log data. The data object contains dataframe created from various event log formats 
    holding basic process event log data, such as trace id, activity name, activity timestamp.
    '''
    def __init__(self, data:DataFrame, mandatory_properties:dict,optional_properties: dict):
        """
        Creates data object representing the event log.

        Args:
        :param data: : dataframe representing event log data
        :type data: DataFrame

        :param mandatory_properties: Dictionary representing a mapping between mandatory standard event log attribute names [ "case:concept:name","concept:name","lifecycle:transition","time:timestamp","org:resource"] and name of corresponding columns in the dataframe
        :type mandatory_properties: dict

        :param optional_properties: Dictionary representing a mapping between optional attribute names and names of corresponding columns in the dataframe
        :type optional_properties: dict
        """ 
        if type(data) not in [pd.DataFrame]: raise TypeError("the method can be applied only to a dataframe!")
      
        self.data = data
        self.mandatory_properties = dict(mandatory_properties)      
        self.optional_properties = dict(optional_properties) 
       
    def __str__(self):
        """
        Return string representaion of the data class content
        :return: Dataframe content, mandatory properties and optional properties
        :rtype: string
        """        
        return f"Data: {self.data},\n Mandatory properties: {self.mandatory_properties} \n Optional properties: {self.optional_properties}"
    
    def copy(self):
        """
        Make a deep copy of the data object.

        :return: A copy of the BaseProcessDataObject instance.
        :rtype: BaseProcessDataObject
        """    
        # Make a deep copy of the DataFrame
        data_copy = self.data.copy(deep=True)
        # Make shallow copies of the dictionaries
        mandatory_properties_copy = self.mandatory_properties.copy()
        optional_properties_copy = self.optional_properties.copy()
        # Create a new instance of BaseProcessDataObject with copied data
        return BaseProcessDataObject(data_copy, mandatory_properties_copy, optional_properties_copy)
    
    def getData(self) -> DataFrame:
        """
        Return the dataframe represeting the event log part of the data object

        :return: A dataframe representing the event log 
        :rtype: DataFrame
        """ 
        return pd.DataFrame(self.data)
    
    def getMandatoryProperties(self) -> dict:
        """
        Get mandatory properties of the data object

        :return: Mandatory properties mapping
        :rtype: dict
        """        
        return self.mandatory_properties
    
    def getOptionalProperties(self) -> dict:
        """
        Get optional properties of the data object

        :return: Optional properties mapping
        :rtype: dict
        """   
        return self.optional_properties

    def getCaseIdColumnName(self) -> str:
        """
        Get the name of the column representing case id

        :return: CaseId column name
        :rtype: str
        """        
        return self.mandatory_properties[Constants.CASE_ID_KEY]
    

    def _extract_properties(self,df, mandatory_properties) -> Tuple[dict, dict]:
        """
        Extract the optional and mandatory properties from the dataframe columns.

        :param df: The input dataframe.
        :type df: pd.DataFrame
        :param mandatory_properties: The mandatory properties dictionary.
        :type mandatory_properties: dict
        :return: The extracted mandatory and optional properties dictionaries.
        :rtype: Tuple[dict, dict]
        """
        mandatory_columns_names = [col for col in df.columns if "__" not in col]
        optional_column_names = [col for col in df.columns if "__" in col]
        #create dictionaries from the column names
        Id_column_name = mandatory_properties[Constants.CASE_ID_KEY]
      
        mandatory_dict = {col: col for col in mandatory_columns_names if col is not mandatory_properties[Constants.CASE_ID_KEY]} 
        mandatory_dict[Constants.CASE_ID_KEY]=Id_column_name

        optional_dict = {col: col for col in optional_column_names}
        return mandatory_dict, optional_dict
    

    def getActivitiesForTrace(self,pid:str) -> list[str]:
        """
        Return a list of all activities for the provided case id

        :param pid: process id
        :type pid: str
        :return: List of all activity names
        :rtype: list[str]
        """            
        return NotImplementedError
    

    def getTrace(self,pid:str) -> Dict[str, Any]:
        """
        Return all the information regarding the given trace in a dictionary, where the keys are the activity names and the values are the activity payloads

        :return: A dictionary representing a single trace
        :rtype: Dict[str, List[str]]
        """                    
        return NotImplementedError  
            

    def getVariant(self, activities: List[str]) -> 'BaseProcessDataObject':
        """
        Provided a list of activity names, return in a dataframe all traces instances which belong to this variant

        :param activities: List of activities names
        :type: List
        :return: Dataframe with all trace instances containing specified activities
        :rtype: BaseProcessDataObject
        """        
        return NotImplementedError  
    
    def getVariants(self) -> dict:
        """
        Return a dictionary mapping of all possible process variants in the event log, to a number of traces per each variant
        
        :return:  Mapping of all possible process variants in the event log, to a number of traces per each variant
        :rtype: dict
        """        
        return NotImplementedError  
    
    def getLength(self) -> int:
        """
        Return the number of traces in the event log

        :return: Length of the event log
        :rtype: int
        """        
        
        return len(self.data)
        
    
        
    

   
  