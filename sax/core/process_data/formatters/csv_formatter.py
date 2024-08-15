# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import pandas as pd

from sax.core.process_data.raw_event_data import RawEventData
from sax.core.utils import helper_utils
from sax.core.utils.constants import Constants, ConstantsMeta
from .base_formatter import BaseFormatter


class CSVFormatter(BaseFormatter):
    '''
    Formatter class for CSV event log files transforming the file to standard event log dataframe representation
    '''      

    class Parameters(metaclass=ConstantsMeta):
        """
        Constants representing various default values for mandatory attributes for CSV-based event log
        """
        ACTIVITY = "Source"
        CASE_ID = "Id"
        TYPE = "Type"
        TIMESTAMP = "Timestamp"
        TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S%z"
        RESOURCE_ID = "Resource"
        CSV_SEPARATOR = ","
        STARTTIME_COLUMN = ""
        

    def __init__(self,  parameters=None):
        """
        Initialize a new instance of the CSVFormatter class.

        Parameters
        ----------
        parameters : dict, optional
            A dictionary of parameters to use when formatting the event log, by default None.

        Raises
        ------
        ValueError
            If the parameters argument is not a dictionary or None.
        """
        super().__init__(parameters=parameters)
        self.parameters[Constants.ACTIVITY_KEY]= helper_utils.get_param_value(Constants.ACTIVITY_KEY, parameters, CSVFormatter.Parameters.ACTIVITY)
        self.parameters[Constants.CASE_ID_KEY] = helper_utils.get_param_value(Constants.CASE_ID_KEY, parameters, CSVFormatter.Parameters.CASE_ID)
        self.parameters[Constants.TIMESTAMP_KEY] = helper_utils.get_param_value(Constants.TIMESTAMP_KEY, parameters, CSVFormatter.Parameters.TIMESTAMP)
        self.parameters[Constants.TYPE_KEY] = helper_utils.get_param_value(Constants.TYPE_KEY, parameters, CSVFormatter.Parameters.TYPE)
        self.parameters[Constants.TIMESTAMP_FORMAT_KEY] = helper_utils.get_param_value(Constants.TIMESTAMP_FORMAT_KEY, parameters, CSVFormatter.Parameters.TIMESTAMP_FORMAT)
        self.parameters[Constants.STARTTIME_COLUMN]= helper_utils.get_param_value(Constants.STARTTIME_COLUMN, parameters, CSVFormatter.Parameters.STARTTIME_COLUMN)
        
    
    
    def extract_data(self,event_log_data,lifecycleTypes=None) -> RawEventData:
        """
        Extract tabular data from the provided CSV event log file, instantiate raw data object containing the tabular data.

        Parameters
        ----------
        event_log_data : file
            File representing the event log data, in CSV format.
        separator : str, optional
            The separator used in the CSV file, by default Constants.CSV_SEPARATOR.

        Returns
        -------
        RawEventData
            A RawEventData representing the event log in a raw event format.

        Raises
        ------
        ValueError
            If the event_log_data argument is not a file.
        """           
        separator=Constants.CSV_SEPARATOR
        dataframe = pd.read_csv(event_log_data, sep=separator) #original dataframe
        return self._format_dataframe(dataframe,lifecycleTypes=lifecycleTypes)
    
    def _format_dataframe(self, dataframe : pd.DataFrame,lifecycleTypes=None) -> RawEventData:
        """
        Format the provided dataframe to represent event log: format timestamps, calculate trace start timestamps

        Parameters
        ----------
        dataframe : pd.DataFrame
            The dataframe to be formatted.

        Returns
        -------
        RawEventData
            A RawEventData object containing the formatted data.

        Raises
        ------
        ValueError
            If the dataframe argument is not a pandas DataFrame.
        """
        original_data = pd.DataFrame(dataframe)        
        mandatory_properties,optional_properties = self._getProperties(original_data, self.parameters)
        if Constants.STARTTIME_COLUMN in mandatory_properties: 
            #calculate the time for each trace based on this column, add it as separate column
            event_log = helper_utils.convert_timestamp_columns_in_df(original_data, timest_format=self.parameters[Constants.TIMESTAMP_FORMAT_KEY], timest_columns=[self.parameters[Constants.TIMESTAMP_KEY], self.parameters[Constants.STARTTIME_COLUMN]])
            event_log = helper_utils.add_start_time(event_log, timestamp_column_name=mandatory_properties[Constants.STARTTIME_COLUMN], id_column_name=mandatory_properties[Constants.CASE_ID_KEY], start_column_name=Constants.STARTTIME_COLUMN)
            #override to this column to be the indicator for trace start time
            mandatory_properties[Constants.STARTTIME_COLUMN]=Constants.STARTTIME_COLUMN  
        else:
            #create such a column for each row and add it to mandatory properties
            event_log = helper_utils.convert_timestamp_columns_in_df(original_data, timest_format=self.parameters[Constants.TIMESTAMP_FORMAT_KEY], timest_columns=[self.parameters[Constants.TIMESTAMP_KEY]])
            event_log = helper_utils.add_start_time(event_log, timestamp_column_name=mandatory_properties[Constants.TIMESTAMP_KEY], id_column_name=mandatory_properties[Constants.CASE_ID_KEY], start_column_name=Constants.STARTTIME_COLUMN)
            mandatory_properties[Constants.STARTTIME_COLUMN]=Constants.STARTTIME_COLUMN                                                                        
        return RawEventData(event_log,mandatory_properties,optional_properties,lifecycleTypes)
    
    def extract_from_dataframe(self,dataframe: pd.DataFrame,lifecycleTypes=None) -> RawEventData:
        """
        Extract event log tabular data from the provided dataframe, instantiate process raw event data object.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Dataframe representing the event log data.

        Returns
        -------
        RawEventData
            A RawEventData representing the event log in a raw event format.

        Raises
        ------
        ValueError
            If the dataframe argument is not a pandas DataFrame.
        """                  
        
        return self._format_dataframe(dataframe,lifecycleTypes=lifecycleTypes)