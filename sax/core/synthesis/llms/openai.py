# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import os
from langchain_openai import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

from sax.core.synthesis.llms.base_llm import BaseLLM

class OpenAILLM(BaseLLM):
    api_key = os.getenv("OPENAI_KEY")

    def __init__(self, model, temperature):  
        super().__init__(model,temperature)         
        self._model = ChatOpenAI(             
            model_name=model,
            openai_api_key=OpenAILLM.api_key,
            temperature=temperature
        ) 
        self._embeddingModel = OpenAIEmbeddings(openai_api_key=OpenAILLM.api_key) 

    
