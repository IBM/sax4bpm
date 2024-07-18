# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from enum import Enum

class ModelTypes(Enum):
    """Enum for supported model providers. Currently supported types are OPENAI and BAM (IBM WatsonX)
    """
    OPENAI = "openai"
    BAM = "bam"    

class BaseLLM:         
    """BaseLLM is a base class for all LLMs wrappers. It provides basic functionality such as setting the model name and temperature and returning the wrapper for the chosen model provider.
    After creating the wrapper can use it to get the pre-configured models for different tasks (generation/embedding)
  
    """
    def __init__(self,model_name, temperature):
       self._model_name = model_name
       self._temperature = temperature
       self._model= None
       self._embeddingModel = None

    
    def getModel(self):
        """Get the preconfigured generation model

        :return: generation model
        :rtype: Langchain generation model
        """
        return self._model
    
    def getEmbeddingModel(self):
        """Get the preconfigured embedding model

        :return: embdedding model
        :rtype: Langchain embedding model
        """
        return self._embeddingModel
    
    @staticmethod
    def getModelLLM(modelType: ModelTypes, modelName, temperature)-> 'BaseLLM':
        """
        Return the LLM wrapper of the chosen model provider type, with the chosen model name and temperature
        :param modelType: model provider type
        :type modelType: ModelTypes
        :param modelName: the fully qualified name of the generation model which will be supplied by this wrapper
        :type modelName: str
        :param temperature: the temperature for the generation model
        :type temperature: int
        :raises ValueError: incorrect model type specified
        :return: Exception
        :rtype: BaseLLM
        """
        if modelType == ModelTypes.OPENAI:
            from sax.core.synthesis.llms.openai import OpenAILLM
            return OpenAILLM(modelName,temperature)
        elif modelType == ModelTypes.BAM:
            from sax.core.synthesis.llms.watsonx import WatsonXLLM
            return WatsonXLLM(modelName,temperature)
        else:
            raise ValueError("Invalid type of model: ",modelType)
    