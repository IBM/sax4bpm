# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from enum import Enum
from typing import Optional

import pandas as pd
import numpy as np

from sax.core.process_data.data import BaseProcessDataObject
from sax.core.process_data.raw_event_data import RawEventData
from sax.core.process_data.tabular_data import TabularEventData
from .constants import Constants


def unroll(value):
    if isinstance(value, Enum):
        return value.value
    return value


def get_param_value(p, parameters, default):
    if parameters is None:
        return unroll(default)
    unrolled_parameters = {}
    for p0 in parameters:
        unrolled_parameters[unroll(p0)] = parameters[p0]
    if p in parameters:
        val = parameters[p]
        return unroll(val)
    up = unroll(p)
    if up in unrolled_parameters:
        val = unrolled_parameters[up]
        return unroll(val)
    return unroll(default)

#Not sure need this
def get_properties(dataObject:BaseProcessDataObject, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", resource_key: str = "org:resource", group_key: Optional[str] = None,timestamp_format: Optional[str] = None, **kwargs):
    """
    Gets the properties from an event data object signifying the column names of the mandatory attributes, date formatter string, and additional attributes

    :param dataObject: data object
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param resource_key: (if provided) attribute to be used as resource
    :param group_key: (if provided) attribute to be used as group identifier
    :rtype: ``Dict``
    """
  

    if type(dataObject) not in [RawEventData, TabularEventData]: return {}

    from copy import copy
    parameters = copy(dataObject.properties) if hasattr(dataObject, 'properties') else copy(dataObject.attrs) if hasattr(dataObject,
                                                                                                    'attrs') else {}

    if activity_key is not None:
        parameters[Constants.ACTIVITY_KEY] = activity_key        

    if timestamp_key is not None:
        parameters[Constants.TIMESTAMP_KEY] = timestamp_key

    if case_id_key is not None:
        parameters[Constants.CASE_ID_KEY] = case_id_key

    if resource_key is not None:
        parameters[Constants.RESOURCE_KEY] = resource_key

    if group_key is not None:
        parameters[Constants.GROUP_KEY] = group_key
    
    if timestamp_format is not None:
        parameters[Constants.TIMESTAMP_FORMAT] = timestamp_format

    for k, v in kwargs.items():
        parameters[k] = v

    return parameters

def convert_timestamp_columns_in_df(df, timest_format=None, timest_columns=None):    
    for col in df.columns:
        if timest_columns is None or col in timest_columns:
            if "obj" in str(df[col].dtype) or "str" in str(df[col].dtype):
                try:
                    if timest_format is None:
                        # makes operations faster if non-ISO8601 but anyhow regular dates are provided
                        df[col] = pd.to_datetime(df[col], utc=True)
                    else:
                        df[col] = pd.to_datetime(df[col], format=timest_format)
                        df[col] = df[col].dt.tz_localize('UTC')
                except Exception as e:                    
                    try:
                        df[col] = pd.to_datetime(df[col], utc=True)
                    except:
                        pass
    return df

# Calculate start time of each trace and add it as separate column to each row event
def add_start_time(df,timestamp_column_name,id_column_name, start_column_name):    
    #TODO: do we want to impose 'start' lifecycle transition, or just go with the first timestamp?
    #start_events = df[df[lifecycle_event_column_name].str.lower() == start_timestamp_value]
    #if start_events.empty:
        #raise ValueError("The event log activities has no start lifecycle events, cannot proceed to calculate trace start times")

    # Step 2: Group the remaining data by 'id' and sort by 'timestamp'
    sorted_data = df.sort_values(by=[id_column_name, timestamp_column_name])

    # Step 3: For each group, get the first timestamp and create a new DataFrame
    start_times = sorted_data.groupby(id_column_name).first()[timestamp_column_name].reset_index()
    start_times.columns = [id_column_name, start_column_name]

    # Step 4: Merge the original DataFrame with the start_times DataFrame
    result_df = pd.merge(df, start_times, on=id_column_name, how='left')

    # Display the result
    return result_df


def get_uniformity(df):
    uniformity = np.eye(len(df.columns)) -1
    for ind1, column1 in enumerate(df.columns):
        for ind2, column2 in enumerate(df.columns):
            if column1!=column2 :
                residuals = df[column1] - df[column2]
                if (residuals >= 0).all():                        
                    uniformity[ind2][ind1] = 0
                else:
                    uniformity[ind2][ind1] = (residuals >= 0).sum()/ len(residuals)
    return uniformity
