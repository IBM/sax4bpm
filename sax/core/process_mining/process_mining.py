# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Tuple

import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.visualization.dfg import visualizer as dfg_visualization

from sax.core.process_data.formatters.csv_formatter import CSVFormatter
from sax.core.process_data.formatters.mxml_formatter import MXMLFormatter
from sax.core.process_data.formatters.xes_formatter import XESFormatter
from sax.core.process_data.raw_event_data import RawEventData
from sax.core.utils.constants import Constants


def import_xes(eventlog,case_id: str=XESFormatter.Parameters.CASE_ID, activity_key: str=XESFormatter.Parameters.ACTIVITY, timestamp_key: str=XESFormatter.Parameters.TIMESTAMP, lifecycle_type: str= XESFormatter.Parameters.TYPE,timestamp_format: str=XESFormatter.Parameters.TIMESTAMP_FORMAT,lifecycleTypes=None) ->RawEventData:
        """
        Parse XES file into event log

        Parameters
        ----------
        :param eventlog: XES event log file
        :type eventlog: Path to the file
        :param case_id: name of the case id column, defaults to XESFormatter.Parameters.CASE_ID
        :type case_id: str, optional
        :param activity_key: name of the activity column, defaults to XESFormatter.Parameters.ACTIVITY
        :type activity_key: str, optional
        :param timestamp_key: name of the timestamp column, defaults to XESFormatter.Parameters.TIMESTAMP
        :type timestamp_key: str, optional
        :param lifecycle_type: name of the event lifecycle column, defaults to XESFormatter.Parameters.TYPE
        :type lifecycle_type: str, optional
        :param timestamp_format: timestamp format, defaults to XESFormatter.Parameters.TIMESTAMP_FORMAT
        :type timestamp_format: str, optional
        :return: Raw event data object
        :rtype: RawEventData
        
        Raises:
        FileNotFoundError: If the specified event log file does not exist, this exception will be raised.
        """
        
        parameters = {}
        parameters[Constants.CASE_ID_KEY]=case_id
        parameters[Constants.ACTIVITY_KEY]=activity_key
        parameters[Constants.TIMESTAMP_KEY]=timestamp_key
        parameters[Constants.TIMESTAMP_FORMAT_KEY] = timestamp_format  
        parameters[Constants.TYPE_KEY]=lifecycle_type        
        formatter = XESFormatter(parameters)
        dataframe = formatter.extract_data(eventlog,lifecycleTypes)
        return dataframe
    
   
def import_csv(eventlog,case_id: str=CSVFormatter.Parameters.CASE_ID, activity_key: str=CSVFormatter.Parameters.ACTIVITY, timestamp_key: str=CSVFormatter.Parameters.TIMESTAMP,lifecycle_type: str= CSVFormatter.Parameters.TYPE, timestamp_format: str=CSVFormatter.Parameters.TIMESTAMP_FORMAT, starttime_column: str=CSVFormatter.Parameters.STARTTIME_COLUMN,lifecycleTypes=None) ->RawEventData:
        """
        Parse CSV file into event log

        Parameters
        -----------
        :param eventlog: CSV event log file
        :type eventlog: Path to the file
        :param case_id: name of the case id column, defaults to XESFormatter.Parameters.CASE_ID
        :type case_id: str, optional
        :param activity_key: name of the activity column, defaults to XESFormatter.Parameters.ACTIVITY
        :type activity_key: str, optional
        :param timestamp_key: name of the timestamp column, defaults to XESFormatter.Parameters.TIMESTAMP
        :type timestamp_key: str, optional
        :param lifecycle_type: name of the event lifecycle column, defaults to XESFormatter.Parameters.TYPE
        :type lifecycle_type: str, optional
        :param timestamp_format: timestamp format, defaults to XESFormatter.Parameters.TIMESTAMP_FORMAT
        :type timestamp_format: str, optional

        Returns
        -------
        :return: Raw event data object
        :rtype: RawEventData

        Raises:
        FileNotFoundError: If the specified event log file does not exist, this exception will be raised.
        """        
        parameters = {}
        parameters[Constants.CASE_ID_KEY]=case_id
        parameters[Constants.ACTIVITY_KEY]=activity_key
        parameters[Constants.TIMESTAMP_KEY]=timestamp_key
        parameters[Constants.TIMESTAMP_FORMAT_KEY] = timestamp_format    
        parameters[Constants.TYPE_KEY]=lifecycle_type      
        parameters[Constants.STARTTIME_COLUMN]=starttime_column
        formatter = CSVFormatter(parameters)
        dataframe = formatter.extract_data(eventlog,lifecycleTypes)
        return dataframe
    
   
def create_from_dataframe(dataframe,case_id: str=CSVFormatter.Parameters.CASE_ID, activity_key: str=CSVFormatter.Parameters.ACTIVITY, timestamp_key: str=CSVFormatter.Parameters.TIMESTAMP, lifecycle_type: str= CSVFormatter.Parameters.TYPE,timestamp_format: str=CSVFormatter.Parameters.TIMESTAMP_FORMAT,starttime_column: str=CSVFormatter.Parameters.STARTTIME_COLUMN,lifecycleTypes=None)->RawEventData:
        """
        Creates event log from dataframe
        
        Parameters
        -----------
        :param eventlog: XES event log file
        :type eventlog: Path to the file
        :param case_id: name of the case id column, defaults to XESFormatter.Parameters.CASE_ID
        :type case_id: str, optional
        :param activity_key: name of the activity column, defaults to XESFormatter.Parameters.ACTIVITY
        :type activity_key: str, optional
        :param timestamp_key: name of the timestamp column, defaults to XESFormatter.Parameters.TIMESTAMP
        :type timestamp_key: str, optional
        :param lifecycle_type: name of the event lifecycle column, defaults to XESFormatter.Parameters.TYPE
        :type lifecycle_type: str, optional
        :param timestamp_format: timestamp format, defaults to XESFormatter.Parameters.TIMESTAMP_FORMAT
        :type timestamp_format: str, optional

        Returns
        -------

        :return: Raw event data object
        :rtype: RawEventData

        Raises
        ---------
        ValueError: If the specified event log data is not in dataframe format
        """                
        parameters = {}
        parameters[Constants.CASE_ID_KEY]=case_id
        parameters[Constants.ACTIVITY_KEY]=activity_key
        parameters[Constants.TIMESTAMP_KEY]=timestamp_key
        parameters[Constants.TIMESTAMP_FORMAT_KEY] = timestamp_format  
        parameters[Constants.TYPE_KEY]=lifecycle_type     
        parameters[Constants.STARTTIME_COLUMN]=starttime_column
        formatter = CSVFormatter(parameters)
        extracted_log = formatter.extract_from_dataframe(dataframe,lifecycleTypes)
        return extracted_log

  
def import_mxml(eventlog,case_id: str=MXMLFormatter.Parameters.CASE_ID, activity_key: str=MXMLFormatter.Parameters.ACTIVITY, timestamp_key: str=MXMLFormatter.Parameters.TIMESTAMP, lifecycle_type: str= MXMLFormatter.Parameters.TYPE,timestamp_format: str=MXMLFormatter.Parameters.TIMESTAMP_FORMAT,lifecycleTypes=None) ->RawEventData:
        """
        Parse MXML file into event log

        Parameters
        -----------
        :param eventlog: XES event log file
        :type eventlog: Path to the file
        :param case_id: name of the case id column, defaults to XESFormatter.Parameters.CASE_ID
        :type case_id: str, optional
        :param activity_key: name of the activity column, defaults to XESFormatter.Parameters.ACTIVITY
        :type activity_key: str, optional
        :param timestamp_key: name of the timestamp column, defaults to XESFormatter.Parameters.TIMESTAMP
        :type timestamp_key: str, optional
        :param lifecycle_type: name of the event lifecycle column, defaults to XESFormatter.Parameters.TYPE
        :type lifecycle_type: str, optional
        :param timestamp_format: timestamp format, defaults to XESFormatter.Parameters.TIMESTAMP_FORMAT
        :type timestamp_format: str, optional

        Returns
        -------

        :return: Raw event data object
        :rtype: RawEventData

        Raises
        ---------
        ValueError: If the specified event log data is not in MXML format
        """        
        parameters = {}
        parameters[Constants.CASE_ID_KEY]=case_id
        parameters[Constants.ACTIVITY_KEY]=activity_key
        parameters[Constants.TIMESTAMP_KEY]=timestamp_key
        parameters[Constants.TIMESTAMP_FORMAT_KEY] = timestamp_format          
        parameters[Constants.TYPE_KEY] = lifecycle_type 
        formatter = MXMLFormatter(parameters)
        dataframe = formatter.extract_data(eventlog,lifecycleTypes)
        return dataframe
    

# def _format_log(dataframe: RawEventData) ->  DataFrame:     
#         event_log = dataframe.getData()   
#         formatted_log = pm4py.format_dataframe(event_log, case_id=dataframe.mandatory_properties[Constants.CASE_ID_KEY], activity_key=dataframe.mandatory_properties[Constants.ACTIVITY_KEY], timestamp_key=dataframe.mandatory_properties[Constants.TIMESTAMP_KEY])                                     
#         #return formatted_log     
#         return event_log


def discover_heuristics_net(dataframe: RawEventData) -> HeuristicsNet:        
        """
        Apply heuristic mining algorithm on the RawEventData event log object to discover heuristic net

        :param dataframe: event log
        :type dataframe: RawEventData
        :param lifecycleTypes: lifecycle event types to filter, defaults to None
        :type lifecycleTypes: List, optional
        :return: heuristic net
        :rtype: HeuristicsNet
        """
        event_log = dataframe                                               
        formatted_log = event_log.getLog()

        #log = log_converter.apply(formatted_log)
        map =  pm4py.discover_heuristics_net(formatted_log)
        return map

      
   
def view_heuristics_net(map: HeuristicsNet):
        """
        Create view of the heuristic net

        :param map: Heuristic net
        :type map: HeuristicsNet
        """        
        pm4py.view_heuristics_net(map)

def discover_dfg(dataframe: RawEventData):        
        """
        Apply dfg mining algorithm on the RawEventData event log object to discover heuristic net

        :param dataframe: event log
        :type dataframe: RawEventData
        :param lifecycleTypes: lifecycle event types to filter, defaults to None
        :type lifecycleTypes: List, optional
        :return: dfg
        :rtype: 
        """
        event_log = dataframe            
                                   
        formatted_log = event_log.getLog()
        dfg =  dfg_discovery.apply(formatted_log, variant=dfg_discovery.Variants.FREQUENCY)
        return dfg, formatted_log

def view_dfg(dfg: dict, formatted_log):
        """
        Create view of the dfg
        """
        gviz = dfg_visualization.apply(dfg, log=formatted_log, variant=dfg_visualization.Variants.FREQUENCY)
        dfg_visualization.view(gviz)

    
def discover_bpmn_model( dataframe: RawEventData) -> BPMN:    
        """
        Performs process mining on the event log data to discover bpmn model

        :param dataframe: event log
        :type dataframe: RawEventData
        :return: BPMN
        :rtype: BPMN
        """            
        process_tree = discover_process_tree(dataframe)
        bpmn_model = pm4py.convert_to_bpmn(process_tree)
        return bpmn_model

  
def view_bpmn_model(bpmn_model: BPMN):
        """
        Create a view of the BPMN model
        :param bpmn_model: BPMN
        :type bpmn_model: BPMN
        """        
        pm4py.view_bpmn(bpmn_model)

    
def discover_process_tree(dataframe: RawEventData) ->ProcessTree:
        """
        Perform process mining on the event log to discover process tree

        :param dataframe: _description_
        :type dataframe: RawEventData
        :param lifecycleTypes: _description_, defaults to None
        :type lifecycleTypes: _type_, optional
        :return: _description_
        :rtype: ProcessTree
        """        
        
        event_log = dataframe             
   
        formatted_log = event_log.getLog()

        #log = log_converter.apply(formatted_log)   
        
        process_tree = pm4py.discover_process_tree_inductive(formatted_log)
        return process_tree
    
   
def view_process_tree(process_tree: ProcessTree):
        """
        Create process tree view
        :param process_tree: prpocess tree
        :type process_tree: ProcessTree
        """        
        pm4py.view_process_tree(process_tree)


   
def discover_process_map( dataframe: RawEventData) -> Tuple[dict,dict,dict]:
        """
        Discover process map

        :param dataframe: event log
        :type dataframe: RawEventData
        :param lifecycleTypes: event lifecycle types to filter, defaults to None
        :type lifecycleTypes: List, optional
        :return: process map
        :rtype: Tuple[dict,dict,dict]
        """        
        event_log = dataframe         
          
        formatted_log = event_log.getLog()

        #log = log_converter.apply(formatted_log)
        
        dfg, start_activities, end_activities = pm4py.discover_dfg(formatted_log)
        return dfg, start_activities, end_activities
        
    
def view_process_map(dfg, start_activities, end_activities):
        """
        Create a view of process map
        
        :param dfg: dfg
        :type dfg: DFG
        :param start_activities: list of start activities
        :type start_activities: List
        :param end_activities: list of end activities
        :type end_activities: List
        """        
        pm4py.view_dfg(dfg, start_activities, end_activities)
          

def filter_start_activities(dataframe: RawEventData, activities, retain=True):
        """
        Filter cases having a start activity in the provided list

        :param activities: collection of start activities
        :type activities: List
        :param retain: if True, we retain the traces containing the given start activities, if false, we drop the traces
        :type retain: bool, optional
        :return: filtered dataframe
        :rtype: Union[EventLog, pd.DataFrame]
        """        
        filtered = pm4py.filter_start_activities(dataframe.getLog(), activities,retain)
        return filtered
    
def filter_end_activities(dataframe: RawEventData, activities, retain=True):
        """
        Filter cases having an end activity in the provided list

        :param activities: collection of end activities
        :type activities: List
        :param retain: if True, we retain the traces containing the given end activities, if false, we drop the traces
        :type retain: bool, optional
        :return: filtered dataframe
        :rtype: Union[EventLog, pd.DataFrame]
        """        
        filtered = pm4py.filter_end_activities(dataframe.getLog(), activities,retain)
        return filtered
    
def getStartActivities(dataframe: RawEventData):
        """
        Returns the start activities from a log object

        :return: Dictionary of start activities along with their count
        :rtype: dict
        """        
        return pm4py.get_start_activities(dataframe.getLog())
    
def getEndActivities(dataframe: RawEventData):       
        """
        Returns the end activities from a log object

        :return: Dictionary of end activities along with their count
        :rtype: dict
        """      
        return pm4py.get_end_activities(dataframe.getLog())

def getDataProcessRepresentation(dataframe: RawEventData):
        """
        The purpose of this function is to take a raw event log as input and output a dictionary representation of the process model discovered when mining this event log.
        :param dataframe: A pandas dataframe containing the raw event log data.
        :type dataframe: RawEventData
        :return: A dictionary representing the process model, where each key is a tuple representing a transition between two activities, and the value is the strength of that transition as determined by the frequency with which it occurs in the event log.
        :rtype: dict
        """        
        dfg,event_log = discover_dfg(dataframe)
        processRepresentation = getModelProcessRepresentation(dfg)
        return processRepresentation

def getModelProcessRepresentation(model):
        def _getPairsProcess(dfgModel):    
                result_dict = {}
                for pair, strength in dfgModel.items():
                        result_dict[pair] = strength
                return result_dict        
        processRepresentation = _getPairsProcess(model)
        return processRepresentation