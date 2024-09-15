# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from enum import Enum


class ConstantsMeta(type):
    def __call__(cls, *args, **kwargs):
        raise TypeError("Cannot instantiate Constants class")
    def __setattr__(cls, name, value):
        raise AttributeError("Cannot modify constant values")

class LifecycleTypes(Enum):
    START = "start"
    ASSIGN = "assign"
    COMPLETE = "complete"  
    
class Constants(metaclass=ConstantsMeta):
    ACTIVITY_KEY = "concept:name"
    CASE_ID_KEY = "case:concept:name"
    TYPE_KEY = "lifecycle:transition"
    GROUP_KEY="Group"
    TIMESTAMP_KEY = "time:timestamp"
    TIMESTAMP_FORMAT_KEY = "TimestampFormat"
    RESOURCE_KEY = "org:resource"
    STARTTIME_COLUMN="start:timestamp"
    START_BASE_COLUMN="start"

    CSV_SEPARATOR=","    
