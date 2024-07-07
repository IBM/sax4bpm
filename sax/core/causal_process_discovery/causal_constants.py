# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from enum import Enum

   
class Algorithm(Enum):
    """
    Enum representing causal discovery algorithms
    
    - LINGAM: DirectLINGAM algorithm
    """ 
    LINGAM = "Lingam"


class Modality(Enum):
    """
    Enum representing causal discovery modalities

    - PARENT: Parent anchor modality, where the examined time relationship between activities A->B->C is B-A and C-A (A is the parent activity and we examine the duration of B after A, and the duration of C which is combined durations of B after A and C after B)
    - CHAIN: Chain anchor modality, where the examined time relationships are between time intervals of each activity timestamp to the initial first activity timestamp
    """          
    PARENT = "Parent"
    CHAIN = "Chain"

    @classmethod
    def from_string(cls, value):
        for modality in cls:
            if value.lower() == modality.value.lower():
                return modality
        raise ValueError(f"No such modality: {value}")

DEFAULT_VARIANT = Algorithm.LINGAM
DEFAULT_MODALITY = Modality.CHAIN
