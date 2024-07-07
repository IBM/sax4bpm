# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from enum import Enum

class ModelTypes(Enum):
    OPENAI = "openai"
    BAM = "bam"    

class BaseLLM:         
    def __init__(self,model_name, temperature):
       self._model_name = model_name
       self._temperature = temperature
       self._model= None
       self._embeddingModel = None

    
    def getModel(self):
        return self._model
    
    def getEmbeddingModel(self):
        return self._embeddingModel
    
    @staticmethod
    def getModelLLM(modelType: ModelTypes, modelName, temperature)-> 'BaseLLM':
        if modelType == ModelTypes.OPENAI:
            from sax.core.synthesis.llms.openai import OpenAILLM
            return OpenAILLM(modelName,temperature)
        elif modelType == ModelTypes.BAM:
            from sax.core.synthesis.llms.watsonx import WatsonXLLM
            return WatsonXLLM(modelName,temperature)
        else:
            raise ValueError("Invalid type of model: ",modelType)
    