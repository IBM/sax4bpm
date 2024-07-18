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
    GENAI_KEY=os.getenv("GENAI_KEY")
    GENAI_API=os.getenv("GENAI_API")

    def __init__(self, model, temperature):
        
        super().__init__(model,temperature)     
        credentials = Credentials(api_key=WatsonXLLM.GENAI_KEY, api_endpoint=WatsonXLLM.GENAI_API)
        client = Client(credentials=credentials)     
        self._model = LangChainInterface(model_id=model, client=client)            
        self._embeddingModel =LangChainEmbeddingsInterface(client=client, model_id="sentence-transformers/all-minilm-l6-v2",parameters=TextEmbeddingParameters(truncate_input_tokens=True))