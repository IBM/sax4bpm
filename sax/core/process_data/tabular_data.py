# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Any, Dict

from pandas import DataFrame

from sax.core.utils.constants import Constants
from .data import BaseProcessDataObject


class TabularEventData(BaseProcessDataObject):
    """
    Tabular representation of event log, where each row represents a full trace,each column representing a particular activity within the trace. The column names
    are the names of the activities, the column values are the timestamps of activity completion times. Additional columns represent activity attribute, each attribute column name composed of
    ``<activityName>__<attributeName>``

    """  
  
    def __init__(self,data:DataFrame, mandatory_properties:dict,optional_properties:dict):       
        """
        Initialize a new instance of TabularEventData class.

        :param data: Dataframe containing the event log data
        :type data: DataFrame
        :param mandatory_properties: Dictionary containing the mandatory properties of the event log
        :type mandatory_properties: dict
        :param optional_properties: Dictionary containing the optional properties of the event log
        :type optional_properties: dict     
        """  
        super().__init__(data=data,mandatory_properties=mandatory_properties,optional_properties= optional_properties)

    def getCaseAndActivitiesData(self)->DataFrame:
        """
        Return the mandatory properties columns content
        Parameters
        ----------
        None

        Returns
        -------        
        :return: dataframe comprised only of the content of mandatory columns (caseID and activities columns)
        :rtype: DataFrame
        """        
        return self.getData()[list(self.getMandatoryProperties().values())]  
    
    def getCaseIDData(self)->DataFrame:
        """
        Return the values of case Id colum

        Parameters
        ----------
        None
                
        Returns
        ------- 
        :return: caseId column content
        :rtype: DataFrame
        """        
        return self.getData()[self.mandatory_properties[Constants.CASE_ID_KEY]]
    
    def getActivitiesData(self) ->DataFrame:
        """
        Return the content of activities columns 

        Parameters
        ----------
        None
                
        Returns
        ------- 

        :return: activities columns content
        :rtype: DataFrame
        """        
        return self.getCaseAndActivitiesData().drop(self.mandatory_properties[Constants.CASE_ID_KEY],axis=1) 
    
    def getActivitiesAttributesData(self)->DataFrame:
        """
        Return all optional attributes columns content
        
        Parameters
        ----------
        None
                
        Returns
        ------- 

        :return: optional attribute columns content
        :rtype: DataFrame
        """        
        return self.getData()[list(self.getOptionalProperties().values())]

    def getActivityAttributesData(self,activityName) -> DataFrame:
        """
        Return attribute columns for the specified activity

        Parameters
        ----------
        :param activityName: activityName
        :type activityName: str
        
        Returns
        ------- 
        
        :return: content of attribute columns for the specified activity
        :rtype: DataFrame
        """        
        activitiesData = self.getActivitiesAttributesData()
        matching_columns = [col for col in activitiesData.columns if col.startswith(activityName)]
        return self.getData()[list(matching_columns)] 
    
    
    def getTrace(self,pid:str) -> Dict[str, Any]:
        """
        Get a trace by its process id (case id).

        Parameters
        ----------
        pid : str
            Case id of the trace to retrieve.
            
        Returns
        ------- 
        Dict[str, Any]
            The trace data as a dictionary (activity names and timestamps)
        
        Raises
        ------
        KeyError
            If a trace with such case id does not exist in the log.
        """    
        return self._get_row_by_id(pid)
   
    
    def _get_row_by_id(self, unique_id):
        """
        Get a trace from the event log by its case id.

        Parameters
        ----------
        unique_id : str
            Case id of the row to retrieve.
            
        Returns
        ------- 
        Dict[str, Any]
            The row data as a dictionary.
        
        Raises
        ------
        KeyError
            If the case id does not exist in the log.
        """    
        # Filter the dataframe based on the given Id
        row = self.data[self.data[self.mandatory_properties[Constants.CASE_ID_KEY] ] == unique_id]        
        # Convert the row to a dictionary and return
        return row.to_dict(orient='records')[0] if not row.empty else None

        