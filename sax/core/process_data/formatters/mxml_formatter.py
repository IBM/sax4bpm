# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Optional
import xml.etree.ElementTree as Xet

import pandas as pd

from sax.core.process_data.data import BaseProcessDataObject
from sax.core.process_data.raw_event_data import RawEventData
from sax.core.utils import helper_utils
from sax.core.utils.constants import Constants, ConstantsMeta, LifecycleTypes
from .base_formatter import BaseFormatter


class MXMLConstants(metaclass=ConstantsMeta):
        """
        Constants representing standart metafields in the MXML format
        
        - PROCESS_INSTANCE: designatation of a the process entry
        - TRACE_INSTANCE: designation of separate trace within the process
        - ID_ATTRIBUTE: designation of the attribute representing trace id
        - EVENT_TYPE: designation of event lifecycle element
        - ACTIVITY: designation of activity element
        - RESOURCE: designation of resource element
        - ATTRIBUTE: designation of attribute element
        - ATTRIBUTE_NAME: designation of attribute name field within attribute element
        """    
        PROCESS_INSTANCE = ".//ProcessInstance"
        TRACE_INSTANCE = ".//AuditTrailEntry"
        ID_ATTRIBUTE = "id"
        EVENT_TYPE = "EventType"
        TIMESTAMP = "Timestamp"
        ACTIVITY = "WorkflowModelElement"
        RESOURCE = "originator"
        ATTRIBUTE = "attribute"
        ATTRIBUTE_NAME = "name"
        DATA = "Data"
        ELEMENT_ID="elementId"
        PROCESS_ID="processId"

    

class MXMLFormatter(BaseFormatter):
    '''
    Formatter class for MXML event log files transforming the file to standard event log dataframe representation
    '''             
    class Parameters(metaclass=ConstantsMeta):
        """
        Constants representing various default values for mandatory attributes values for MXML-based event log

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
        Initializes the MXML formatter with relevant information about the MXML parameters and how to extract relevant information from MXML

        Args:
        :param parameters: Mapping between MXML based attributes and resulting event log attributes
        :type parameters: dict

        Raises:
        :raises ValueError: If any of the mandatory parameters are missing or invalid.
        """
        super().__init__(parameters=parameters)
        self.parameters[Constants.ACTIVITY_KEY]= helper_utils.get_param_value(Constants.ACTIVITY_KEY, parameters, MXMLFormatter.Parameters.ACTIVITY)
        self.parameters[Constants.CASE_ID_KEY] = helper_utils.get_param_value(Constants.CASE_ID_KEY, parameters, MXMLFormatter.Parameters.CASE_ID)
        self.parameters[Constants.TIMESTAMP_KEY] = helper_utils.get_param_value(Constants.TIMESTAMP_KEY, parameters, MXMLFormatter.Parameters.TIMESTAMP)
        self.parameters[Constants.TYPE_KEY] = helper_utils.get_param_value(Constants.TYPE_KEY, parameters, MXMLFormatter.Parameters.TYPE)
        self.parameters[Constants.TIMESTAMP_FORMAT_KEY] = helper_utils.get_param_value(Constants.TIMESTAMP_FORMAT_KEY, parameters, MXMLFormatter.Parameters.TIMESTAMP_FORMAT)        
        self.parameters[Constants.RESOURCE_KEY] = helper_utils.get_param_value(Constants.RESOURCE_KEY, parameters, MXMLFormatter.Parameters.RESOURCE_ID)        

    def extract_data(self,event_log_data,lifecycle_type: Optional[LifecycleTypes] = None) -> BaseProcessDataObject:
        """
        Extract tabular data from the provided MXML event log file, instantiate raw data object containing the tabular data.

        Parameters
        -----------
        :param event_log_data: File representing the event log data, in MXML format
        :type event_log_data: file

        Returns
        -------
        :return: A RawEventData representing the event log in a raw event format
        :rtype: RawEventData

        Raises
        ------
        :raises ValueError: If the event log data is not in MXML format.
        """ 
        df = self._parse_xml(event_log_data)        
        original_data = pd.DataFrame(df)       
        event_log = helper_utils.convert_timestamp_columns_in_df(original_data, timest_format=self.parameters[Constants.TIMESTAMP_FORMAT_KEY], timest_columns=self.parameters[Constants.TIMESTAMP_KEY])
        mandatory_properties,optional_properties = self._getProperties(event_log, self.parameters)
        event_log = helper_utils.add_start_time(event_log, timestamp_column_name=mandatory_properties[Constants.TIMESTAMP_KEY], id_column_name=mandatory_properties[Constants.CASE_ID_KEY], start_column_name=Constants.STARTTIME_COLUMN)
        mandatory_properties[Constants.STARTTIME_COLUMN]=Constants.STARTTIME_COLUMN     
        return RawEventData(event_log,mandatory_properties,optional_properties,lifecycle_type)
    
        
    

    def  _parse_xml(self,event_log_data) -> pd.DataFrame:
        """
        Parse the XML event log data into a Pandas DataFrame.

        Parameters
        -----------
        :param event_log_data: File representing the event log data, in MXML format
        :type event_log_data: file

        Returns
        --------
        :return: A Pandas DataFrame representation of the event log data.
        :rtype: pd.DataFrame

        Raises
        ------
        :raises ValueError: If the event log data is not in MXML format.
        """
        root = event_log_data.getroot()
        rows = []       
        for process_instance in root.findall(MXMLConstants.PROCESS_INSTANCE):
            process_instance_id = process_instance.get(MXMLConstants.ID_ATTRIBUTE)
            for audit_entry in process_instance.findall(MXMLConstants.TRACE_INSTANCE):
                data_dict = {}
                resource_element = None
                for child_element in audit_entry:
                    tag_name_lower = child_element.tag.lower()
                    if tag_name_lower == MXMLConstants.ACTIVITY.lower():
                        activity = child_element.text
                    elif tag_name_lower == MXMLConstants.EVENT_TYPE.lower():
                        event_type = child_element.text
                    elif tag_name_lower == MXMLConstants.TIMESTAMP.lower():
                        timestamp = child_element.text
                    elif tag_name_lower == MXMLConstants.RESOURCE.lower():
                        resource_element = child_element
                    elif tag_name_lower == MXMLConstants.DATA.lower():
                        data_element = child_element
                        attribute_elements = [element for element in data_element if element.tag.lower() == MXMLConstants.ATTRIBUTE]
                        for attr in attribute_elements:
                            attr_name = attr.get(MXMLConstants.ATTRIBUTE_NAME)
                            #use only those attribute which do not appear in the mandatory attributes list
                            if (attr_name.lower() != Constants.CASE_ID_KEY.lower() and attr_name.lower() != Constants.ACTIVITY_KEY.lower() and attr_name.lower() != Constants.TYPE_KEY.lower() and attr_name.lower() != Constants.TIMESTAMP_KEY.lower() and attr_name.lower() != Constants.RESOURCE_KEY.lower() and attr_name.lower() != MXMLConstants.PROCESS_ID.lower() and attr_name.lower() != MXMLConstants.ELEMENT_ID.lower()):
                                attr_value = attr.text
                                new_attr_name = f"Attr_{attr_name}"  # Add a prefix to avoid name collision
                                data_dict[new_attr_name] = attr_value   
                                        
                resource = resource_element.text if resource_element is not None else None

                row = {
                            self.parameters[Constants.CASE_ID_KEY]: process_instance_id,
                            self.parameters[Constants.ACTIVITY_KEY]: activity,
                            self.parameters[Constants.TYPE_KEY]: event_type,
                            self.parameters[Constants.TIMESTAMP_KEY]: timestamp,
                            self.parameters[Constants.RESOURCE_KEY]: resource,
                            **data_dict
                        }
                rows.append(row)
        df = pd.DataFrame(rows)
        return df