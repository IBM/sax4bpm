# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from abc import abstractmethod
from typing import Optional

from ...causal_process_discovery.algorithms.base_causal_alg import CausalResultInfo
from ...causal_process_discovery.causal_constants import DEFAULT_VARIANT, Algorithm
from ...process_data.raw_event_data import RawEventData


class BaseAnchor:
    """
    Parent class for all causal discovery modalities. Please extend this class to add more modalities. Different modalities are described here <>
    """    
 
    @abstractmethod
    def apply(self, dataObject: RawEventData,variant: Optional[Algorithm] = DEFAULT_VARIANT,prior_knowledge: Optional[bool]=False, threshold: Optional[float]=0.5) -> CausalResultInfo:
        """
        Apply the chosen algorithm variant with the current modality on the process data object.

        :param dataObject:  event log
        :type dataObject: RawEventData
        :param variant: the chosen algorithm variant to apply, defaults to LINGAM
        :type variant: Optional[Algorithm], optional
        :return: causal discovery result
        :rtype: CausalResultInfo
        """    
        return NotImplementedError
        