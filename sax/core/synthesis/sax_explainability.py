# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from sax.core.causal_process_discovery import causal_discovery as cd
from sax.core.process_data.raw_event_data import RawEventData
from sax.core.process_mining import process_mining as pm
from sax.core.synthesis.llms.base_llm import BaseLLM, ModelTypes
from sax.core.synthesis.prompt import explanation_prompting
from sax.core.synthesis.rag.base_retrieval import BaseRetriever
from sax.core.synthesis.rag.documents_retrieval import DocumentRetrieverLLM



def createDocumentContextRetriever(modelType:ModelTypes, modelName: str, temperature: int, documentsPath:str,filter=None,chunk_size=None,chunk_overlap=None,retrieved_results=None,dbPath=None) -> BaseRetriever:
    model = BaseLLM.getModelLLM(modelType, modelName, temperature)
    retriever = DocumentRetrieverLLM(model,documentsPath,filter,chunk_size=chunk_size,chunk_overlap=chunk_overlap,retrieved_results=retrieved_results,dbPath=dbPath)
    return retriever

def createDocumentContextExplanation(query: str,retriever: DocumentRetrieverLLM):   
    context= retriever.getContext(query)    
    output = explanation_prompting.createExplanation(retriever.getModel(),query,context)
    return output
     

def getExplanations(data:RawEventData,modality,prior_knowledge = None, p_value_threshold=None ):
    dfg,event_log = pm.discover_dfg(data)  
    causalModel = cd.discover_causal_dependencies(dataObject=data,modality=modality,prior_knowledge=prior_knowledge)
    result = enumerateDisrepancies(dfg, causalModel,p_value_threshold=p_value_threshold)
    return result

    
def enumerateDisrepancies(processModel, causalModel,p_value_threshold=None):   
    addedEdge = ' Altering the \'{first_activity}\' completion time is likely to affect the lead time of \'{second_activity}\''
    removedEdge = 'Altering the \'{first_activity}\' completion time is not likely to affect lead time of \'{second_activity}\' '    

    explanations = []
    processRepresentation = _getPairsProcess(processModel)
    causalModel = _getPairsCausal(causalModel,p_value_threshold=p_value_threshold)
    #calculateDiff should return tuples of activities in correct order between which edges were added or removed
    addedEdges,removedEdges = _calculateDiff(processRepresentation,causalModel)
    for i, pair in enumerate(addedEdges):
        first_activity = pair[0]
        second_activity = pair[1]
        explanation = addedEdge.format(first_activity=first_activity, second_activity=second_activity)
        explanations.append(explanation)

    for i, pair in enumerate(removedEdges):
        first_activity = pair[0]
        second_activity = pair[1]
        explanation = removedEdge.format(first_activity=first_activity, second_activity=second_activity)
        explanations.append(explanation)
    
    return explanations

def _getPairsProcess(dfgModel):    
    result_dict = {}
    for pair, strength in dfgModel.items():
        result_dict[pair] = strength
    return result_dict

def _getPairsCausal(result,p_value_threshold=None):
    return cd.get_causal_graph_representation(result,p_value_threshold)
    

def _calculateDiff(processRepresentation,causalModel):   
    set1 = set(processRepresentation.keys())
    set2 = set(causalModel.keys())

    removed_edges = list(set1 - set2)
    addedEdges = list(set2 - set1)
    
    return addedEdges, removed_edges
        
