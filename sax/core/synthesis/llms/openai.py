# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import os
from langchain_openai import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

from sax.core.synthesis.llms.base_llm import BaseLLM

class OpenAILLM(BaseLLM):
    """OpenAI LLM wrapper, implementation of BaseLLM
    """
    def __init__(self, model, temperature):
        self.api_key = os.getenv("OPENAI_KEY")
        if not self.api_key:
            raise ValueError("The API key for OpenAI is not set. Please set the OPENAI_KEY environment variable.")  
        super().__init__(model,temperature)         
        self._model = ChatOpenAI(             
            model_name=model,
            openai_api_key=self.api_key,
            temperature=temperature
        ) 
        self._embeddingModel = OpenAIEmbeddings(openai_api_key=self.api_key) 

    
