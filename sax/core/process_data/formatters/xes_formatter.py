# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Optional
import pm4py

from sax.core.process_data.raw_event_data import RawEventData
from sax.core.utils import helper_utils
from sax.core.utils.constants import Constants,LifecycleTypes
from .base_formatter import BaseFormatter


class XESFormatter(BaseFormatter):
    '''
    Formatter class for XES event log files transforming the file to standard event log dataframe representation
    '''      

    class Parameters(metaclass=ConstantsMeta):
        """
        Constants representing various default values for mandatory attributes values for XES-based event log

        Attributes
        ----------
        ACTIVITY : str
            Default value for activity key.
        CASE_ID : str
            Default value for case id key.
        TYPE : str
            Default value for lifecycle event key.
        TIMESTAMP : str
            Default value for timestamp key.
        TIMESTAMP_FORMAT : str
            Default value for timestamp format key.
        RESOURCE_ID : str
            Default value for resource id key.
        """
        ACTIVITY = "concept:name"
        CASE_ID = "case:concept:name"
        TYPE = "lifecycle:transition"
        TIMESTAMP = "time:timestamp"
        TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
        RESOURCE_ID = "org:resource" 
  
    def __init__(self,  parameters=None):
        """
        Initializes the XES formatter with relevant information about the MXML parameters and how to extract relevant information from XES

        Args:
        :param parameters: Mapping between XES based attributes and resulting event log attributes
        :type parameters: dict

        Raises:
        :raises ValueError: If any of the mandatory parameters are missing or invalid.
        """
        super().__init__(parameters=parameters)
        self.parameters[Constants.ACTIVITY_KEY]= helper_utils.get_param_value(Constants.ACTIVITY_KEY, parameters, XESFormatter.Parameters.ACTIVITY)
        self.parameters[Constants.CASE_ID_KEY] = helper_utils.get_param_value(Constants.CASE_ID_KEY, parameters, XESFormatter.Parameters.CASE_ID)
        self.parameters[Constants.TIMESTAMP_KEY] = helper_utils.get_param_value(Constants.TIMESTAMP_KEY, parameters, XESFormatter.Parameters.TIMESTAMP)
        self.parameters[Constants.TYPE_KEY] = helper_utils.get_param_value(Constants.TYPE_KEY, parameters, XESFormatter.Parameters.TYPE)
        self.parameters[Constants.TIMESTAMP_FORMAT_KEY] = helper_utils.get_param_value(Constants.TIMESTAMP_FORMAT_KEY, parameters, XESFormatter.Parameters.TIMESTAMP_FORMAT)        

    def extract_data(self,event_log_data,lifecycle_type: Optional[LifecycleTypes] = None) -> RawEventData:
        """
        Extract tabular data from the provided XES event log file, instantiate raw data object containing the tabular data.

        Args:
        :param event_log_data: File representing the event log data, in XES format
        :type event_log_data: file

        Returns:
        :return: A RawEventData representing the event log in a raw event format
        :rtype: RawEventData

        Raises:
        :raises ValueError: If the event log data is not in MXML format.
        """      
        event_log = pm4py.read_xes(event_log_data)        
        dataframe = pm4py.convert_to_dataframe(event_log)   
        event_log = helper_utils.convert_timestamp_columns_in_df(dataframe, timest_format=self.parameters[Constants.TIMESTAMP_FORMAT_KEY], timest_columns=self.parameters[Constants.TIMESTAMP_KEY])
        mandatory_properties,optional_properties = self._getProperties(dataframe, self.parameters) 
        event_log = helper_utils.add_start_time(event_log, timestamp_column_name=mandatory_properties[Constants.TIMESTAMP_KEY], id_column_name=mandatory_properties[Constants.CASE_ID_KEY], start_column_name=Constants.STARTTIME_COLUMN)
        mandatory_properties[Constants.STARTTIME_COLUMN]=Constants.STARTTIME_COLUMN          
        return RawEventData(event_log,mandatory_properties,optional_properties,lifecycle_type)
       