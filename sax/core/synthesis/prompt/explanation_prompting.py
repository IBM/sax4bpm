# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_not_exception_type
from sax.core.synthesis.exceptions.validation import ValidationException
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

from sax.core.synthesis.llms.base_llm import BaseLLM




@retry(
    retry = retry_if_not_exception_type((ValidationException)),
    # Function to add random exponential backoff to a request
    wait = wait_random_exponential(multiplier = 1, max = 60),
    stop = stop_after_attempt(10)
)
def _run_llm_chain(hub_chain,query,contextText,phenomena, instruction):
    if not phenomena and contextText:        
         output = hub_chain.run(context=contextText,question=query)
    elif phenomena and instruction and contextText:
        output = hub_chain.run(context=contextText,question=query, phenomena=phenomena,instruction = instruction)
    elif phenomena and instruction: 
        output = hub_chain.run(question=query, phenomena=phenomena,instruction = instruction)
    elif phenomena and contextText:
        output = hub_chain.run(question=query, phenomena=phenomena,context = contextText)
    elif phenomena:
        output = hub_chain.run(question=query, phenomena=phenomena)
    else:
        raise ValidationException("Validation error on function parameters","Not all parameters provided for the required LLM query")
    return output

# def _run_llm_chain(hub_chain,query,contextText,disrepancies):
#     if not contextText:
#         if disrepancies:
#             output = hub_chain.run(disrepancies=disrepancies,question=query)
#         else:
#             output = hub_chain.run(question=query)
#     elif not disrepancies:
#         output = hub_chain.run(context=contextText,question=query)
#     else:
#         output =hub_chain.run(context=contextText,question=query,disrepancies=disrepancies)       
#     return output

def createExplanation(model:BaseLLM,query: str,contextText: Optional[str] = None, phenomena: Optional[str] = None,instruction: Optional[str] = None):  
    prefix = """You are a very insightful assistant, with great analytic capabilities, capable to injest information from multiple different data sources and
            crunching them all together to get higher level picture integrating all this information.
            You are capable to answer questions based on this higher level view into the data.""" 
    suffix = None
    if phenomena is not None:
        if contextText is not None:
            if instruction is not None:
                suffix = """ This is the phenomena which you are trying to explain: {phenomena}. This is how you interpret this information: {instruction}. Answer the following question regarding this phenomena based on the following context:  {context}
                Question: {question}.
                Provide a detailed answer.
                Don't justify your answers.
                Don't give information not mentioned in the CONTEXT or not related to the given phenomena.
                Do not say "according to the context" or "mentioned in the context" or similar."""
            else:
                suffix = """ This is the phenomena which you are trying to explain: {phenomena}. Answer the following question regarding this phenomena based on the following context:  {context}
                Question: {question}.
                Provide a detailed answer.
                Don't justify your answers.
                Don't give information not mentioned in the CONTEXT or not related to the given phenomena.
                Do not say "according to the context" or "mentioned in the context" or similar."""
        else:  #no context
            if instruction is not None:
                suffix = """ This is the phenomena which you are trying to explain: {phenomena}. This is how you interpret this information: {instruction}. Answer the following question regarding this phenomena:
                Question: {question}.
                Provide a detailed answer.
                Don't justify your answers.
                Don't give information not related to the given phenomena.
                """ 
            else: 
                suffix = """ This is the phenomena which you are trying to explain: {phenomena}. Answer the following question regarding this phenomena:
                Question: {question}.
                Provide a detailed answer.
                Don't justify your answers.
                Don't give information not related to the given phenomena."""
    else: #no phenomena to explain, general question based on context 
        if contextText is not None:
            suffix = """ Answer the following question based on the following context:  {context}
                Question: {question}.
                Provide a detailed answer.
                Don't justify your answers.
                Don't give information not mentioned in the CONTEXT or not related to the given phenomena and don't make things up if it is not explicitly mentioned in the CONTEXT.
                Do not say "according to the context" or "mentioned in the context" or similar."""
    if suffix is None:  raise ValidationException("Validation error on function parameters","Not all parameters provided for the required LLM query")
    PROMPT_TEMPLATE = prefix+suffix    
    llm  = model.getModel()
    # load retrieved context and user query in the prompt template
    prompt_template = PromptTemplate.from_template(PROMPT_TEMPLATE)      
    hub_chain = LLMChain(prompt=prompt_template,llm=llm,verbose=True)              
    output  = _run_llm_chain(hub_chain,query, contextText,phenomena,instruction)                          
    return output    
    
# def createExplanation(model:BaseLLM,query: str,contextText: Optional[str] = None, disrepancies: Optional[str] = None):    
#     if contextText == None:
#         if disrepancies == None:
#             PROMPT_TEMPLATE = """            
#             Please answer the following question based on your general knowledge: {question}.
#             Provide a detailed answer.        
#             """
#         else:
#             PROMPT_TEMPLATE = """
#             Those are the disrepancies you are trying to explain: {disrepancies}.
#             Please answer the question based on the provided disrepancies and your general knowledge: {question}.
#             Provide a detailed answer.        
#             """
#     elif disrepancies == None:
#         PROMPT_TEMPLATE = """
#         Answer the question based ONLY on the following context:
#         {context}
#         This is the question to answer based on the above context: {question}.
#         Provide a detailed answer.
#         Don’t justify your answers.
#         Don’t give information not mentioned in the CONTEXT.
#         But screen out the information in the CONTEXT and do not include information irrelevant to  the question in your answer.
#         Do not say "according to the context" or "mentioned in the context" or similar.
#         """
#     else:
#         PROMPT_TEMPLATE = """
#         Those are the disrepancies you are trying to explain: {disrepancies}. Answer the question regarding those disrepancies based on the following context:  
#         {context}
#         This is the question to answer based on the above context: {question}.
#         Provide a detailed answer.
#         Don’t justify your answers.
#         Don’t give information not mentioned in the CONTEXT or not related to the provided disrepancies.
#         Do not say "according to the context" or "mentioned in the context" or similar.
#         """

#     llm  = model.getModel()
#     # load retrieved context and user query in the prompt template
#     prompt_template = PromptTemplate.from_template(PROMPT_TEMPLATE)      
#     hub_chain = LLMChain(prompt=prompt_template,llm=llm,verbose=True)              
#     output  = _run_llm_chain(hub_chain,query, contextText,disrepancies)                          
#     return output    
