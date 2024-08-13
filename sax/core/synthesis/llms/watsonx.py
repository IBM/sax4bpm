# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import os
from genai import Client, Credentials
from genai.extensions.langchain import LangChainInterface
from genai.extensions.langchain import LangChainEmbeddingsInterface
from genai.schema import TextEmbeddingParameters
from sax.core.synthesis.llms.base_llm import BaseLLM

class WatsonXLLM(BaseLLM):
    """WatsonX LLM wrapper, implementation of BaseLLM
    """
    def __init__(self, model, temperature): 
        self.genai_key = os.getenv("GENAI_KEY")                
        self.genai_api= os.getenv("GENAI_API")       
        if not self.genai_key:
            raise ValueError("The API key for GenAI is not set. Please set the GENAI_KEY environment variable.")
        if not self.genai_api:
            raise ValueError("The API URL for GenAI is not set. Please set the GENAI_API environment variable.")
        super().__init__(model,temperature) 
        
        credentials = Credentials(api_key=self.genai_key, api_endpoint=self.genai_api)
        client = Client(credentials=credentials)
        client = Client(credentials=Credentials.from_env())
        self._model = LangChainInterface(model_id=model, client=client)                
        self._embeddingModel =LangChainEmbeddingsInterface(client=client,model_id="sentence-transformers/all-minilm-l6-v2",parameters=TextEmbeddingParameters(truncate_input_tokens=True))