# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Optional

import pandas as pd

from sax.core.utils.constants import Constants
from ...causal_process_discovery.algorithms.positive_lingam.positive_direct_lingam import PositiveDirectLiNGAM
from .base_anchor import BaseAnchor
from ...causal_process_discovery.algorithms.base_causal_alg import CausalResultInfo
from ...causal_process_discovery.algorithms.lingam import LingamImpl
from ...causal_process_discovery.algorithms.rcd import RcdImpl
from ...causal_process_discovery.causal_constants import DEFAULT_VARIANT, Algorithm
from ...causal_process_discovery.prior_knowledge import PriorKnowledge
from ...process_data.raw_event_data import RawEventData


class ChainAnchorTransformer(BaseAnchor):
    '''
    Causal chain modality transformer - transforms process data object from event log format to a tabular format which represents each activity
    as a column in the data frame, where the value of the column is the accumulated duration of this activity from trace start time.
    The chain modality is described here <>
    '''    

    def apply(self, dataObject: RawEventData,variant: Optional[Algorithm] = DEFAULT_VARIANT,prior_knowledge: Optional[bool]=False) -> CausalResultInfo:
        """
        Transform raw event log in tabular form (the provided event log) to row format, so that each trace is represented by a row and each activity column value holds the accimulated duration
        from trace start time. After the transformation, applies the chosen causal discovery algorithm variant to discover causal execution dependencies
        among chained durations.

        :param dataObject: event log
        :type dataObject: RawEventData
        :param variant: algorithm variant to apply, defaults to LINGAM
        :type variant: Optional[Algorithm], optional
        :param prior_knowledge: whether to apply prior knowledge, defaults to False
        :type prior_knowledge: Optional[bool], optional
        :raises TypeError: _description_
        :return: _description_
        :rtype: CausalResultInfo
        """
        if type(dataObject) not in [RawEventData]: raise TypeError("the method can be applied only to an object of type RawEventData!")
        
        dataObject = dataObject.transposeToTabular()      
        
          
        #get the main properties data - process id and activities columns from the dataframe
        df = dataObject.getCaseAndActivitiesData() #TODO can change only to getActivitiesData() and update the code      
        start_time_column_name = dataObject.getMandatoryProperties()[Constants.STARTTIME_COLUMN] 
        caseIdColumnName = dataObject.getCaseIdColumnName()              

        # Drop the 'Id' column to create activities_df       
        activities_df = df.drop(caseIdColumnName, axis=1).copy()          
        activities_df = activities_df.apply(pd.to_datetime, utc=True)     
        start_times = activities_df[start_time_column_name].copy()     
        activities_df= activities_df.drop(start_time_column_name,axis=1)

        first_activity_time = start_times.dt.to_period('Y').dt.to_timestamp()#.tz_localize(None)#.dt.floor(freq = 'MS')  
        first_activity_time = pd.to_datetime(first_activity_time, utc=True)                 
        print(type(first_activity_time))

        # Create a new DataFrame for storing time differences
        time_difference_df = activities_df.copy()
        for col in activities_df.columns:
             time_difference_df[col] = (activities_df[col] - first_activity_time).dt.total_seconds()
                     
        #time_difference_df = time_difference_df.sub(time_difference_df.min(axis=1), axis=0)
        time_difference_df.to_csv('full.csv')
        #create and run the algorithm        
        args = {"data": time_difference_df}
        if prior_knowledge:
            args["prior_knowledge"] = PriorKnowledge(time_difference_df)
        
        if variant == Algorithm.LINGAM:
            algorithm = LingamImpl(**args)
        elif variant == Algorithm.RCD:
            algorithm = RcdImpl(**args)
        elif variant == Algorithm.POSITIVE_LINGAM:
            algorithm = PositiveLingamImpl(**args)
        result  = algorithm.run()       

        return result  