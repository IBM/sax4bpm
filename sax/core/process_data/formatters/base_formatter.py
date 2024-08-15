# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from abc import abstractmethod
from typing import Tuple

from pandas import DataFrame

from sax.core.process_data.raw_event_data import RawEventData


class BaseFormatter:

    '''
    Formatter base class which can transform event log data from a file in different event log formats to standard raw event log representation for further use.
    '''      

    def __init__(self, parameters = None):
        """
        Initializes the formatter.

        Parameters
        ----------
        parameters : dict, optional
            A mapping of mandatory event attribute names to actual names in the log. The mandatory attribute names include: Constants.CASE_ID_KEY, Constants.ACTIVITY_KEY, Constants.TIMESTAMP_KEY, Constants.TIMESTAMP_FORMAT_KEY, Constants.TYPE_KEY, by default None

        Raises
        ------
        TypeError
            If the input parameter is not a dictionary
        """               
        # set the parameters
        if (parameters is None): parameters = dict()
        self.parameters = dict(parameters)
    
    @abstractmethod
    def extract_data(self, event_log_data,lifecycleTypes=None) -> RawEventData:
        """
        Create RawEventData data object from the provided event log file

        Parameters
        ----------
        event_log_data : The path designation of the event log file.
        type event_log_data : File

        Returns
        -------
        A RawEventData representing the event log in a tabular format.
        type : RawEventData        
        """
        pass


    def _getProperties(self,dataframe:DataFrame, parameters: dict) -> Tuple[dict, dict]:
        """
        Extracts the properties of the dataframe based on the given parameters.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            The dataframe to extract the properties from.
        parameters : dict
            A dictionary containing the parameters to extract. The keys are the keywords to use, and the values are the names of the columns in the dataframe.

        Returns
        -------
        tuple[dict, dict]
            A tuple containing two dictionaries. The first contains the mandatory properties, and the second contains the optional properties.

        Raises
        ------
        TypeError
            If the dataframe is not a pandas.DataFrame.
        ValueError
            If any of the parameters are not present in the dataframe.
        """
        if type(dataframe) not in [DataFrame]: raise TypeError("the method can be applied only to a dataframe!")              
        mandatory_dict={}
        optional_dict={}
        for keyword, column_name in parameters.items():
            if column_name in dataframe.columns:
                mandatory_dict[keyword] = column_name
    
        for column_name in dataframe.columns:
            if column_name not in parameters.values():
                optional_dict[column_name] = column_name
    
        return mandatory_dict,optional_dict

        