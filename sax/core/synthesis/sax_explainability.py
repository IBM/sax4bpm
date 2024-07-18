# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel
from sax.core.causal_process_discovery import causal_discovery as cd
from sax.core.causal_process_discovery.causal_constants import Modality
from sax.core.process_data.raw_event_data import RawEventData
from sax.core.process_mining import process_mining as pm
from sax.core.synthesis.llms.base_llm import BaseLLM, ModelTypes
from sax.core.synthesis.rag.base_retrieval import BaseRetriever
from sax.core.synthesis.rag.documents_retrieval import DocumentRetrieverLLM
from operator import itemgetter

def createDocumentContextRetriever(modelType:ModelTypes, modelName: str, temperature: int, documentsPath:str,filter=None,chunk_size=None,chunk_overlap=None,retrieved_results=None,dbPath=None) -> BaseRetriever:
    """Create a document context retriever to use later for retreiving query-appropriate context.

    :param modelType: the model provider type to use
    :type modelType: ModelTypes
    :param modelName: the name of the model by the model provider to use as generative model
    :type modelName: str
    :param temperature: the temperature to use with the generative model
    :type temperature: int
    :param documentsPath: the path to the document/documents' folder
    :type documentsPath: str
    :param filter: file extension of the files to be considered, defaults to None
    :type filter: str, optional
    :param chunk_size: chunk_size for document splitting, defaults to None
    :type chunk_size: int, optional
    :param chunk_overlap: chunk overlap for document splitting, defaults to None
    :type chunk_overlap: int, optional
    :param retrieved_results: number of results to retrieve, defaults to None
    :type retrieved_results: int, optional
    :param dbPath: path to the vectore store db, defaults to None
    :type dbPath: str, optional
    :return: document retriever to be used later in rag-enhanced syntethis
    :rtype: BaseRetriever
    """
    model = BaseLLM.getModelLLM(modelType, modelName, temperature)
    retriever = DocumentRetrieverLLM(model,documentsPath,filter,chunk_size=chunk_size,chunk_overlap=chunk_overlap,retrieved_results=retrieved_results,dbPath=dbPath)
    return retriever

def _getChain(model: BaseLLM,causal: bool, process:bool, xai:bool, rag:bool, retriever: DocumentRetrieverLLM =None):   
    """
    Based on the chosen perspectives, builds and returns Langchain chain to invoke later with the user-supplied query for explanation based on thoe chosen perspectives
    :param model: model wrapper
    :type model: BaseLLM
    :param causal: indication whether to use causal perspective
    :type causal: bool
    :param process: indication whether to use process perspective
    :type process: bool
    :param xai: indication whether to use xai perspective
    :type xai: bool
    :param rag: indicatin whether to use document context
    :type rag: bool
    :param retriever: in case rag is chosen, need to provide previously created retreiver, defaults to None
    :type retriever: DocumentRetrieverLLM, optional
    :return: Langchain chain
    :rtype: chain
    """
    print(f"_getChain: process: {process}, causal: {causal}, xai: {xai}, rag: {rag}, retriever: {retriever}")
    def getCausalPerspective(data, modality, prior_knowledge,p_value_threshold):
        result = cd.getDataCausalRepresentation(data,modality=modality,prior_knowledge=prior_knowledge,p_value_threshold=p_value_threshold) 
        print("Causal: ",result)
        return result
    
    def getProcessPerspective(data):
        result =  pm.getDataProcessRepresentation(data)
        print("Process:" , result)
        return result 
    
    def getXAIPerspective(data):
        #TODO
        result = ""
        print("XAI", result)
        return result
    
    def getDocuments(retriever):
        def format_docs(docs):
            return "\n\n ------------".join(doc.page_content for doc in docs)
        retriver = retriever.get_retriever()
        return retriver | format_docs
    
    causal_runnable = RunnableLambda(lambda x: {"causal": getCausalPerspective(x["data"],x["modality"],x["prior_knowledge"],x["p_value_threshold"])})
    process_runnable = RunnableLambda(lambda x: {"process": getProcessPerspective(x["data"])})
    xai_runnable= RunnableLambda(lambda x: {"xai": getXAIPerspective(x["data"])})
    if rag:
        rag_retriever = getDocuments(retriever)
    else:
        rag_retriever=None

    if (not process and not causal and not xai and rag ):
        print("Method for combination (False, False, False, True)")
        prompt = ChatPromptTemplate.from_template(
        """We have some relevant documentation for a particular business process. Given the query {query} regarding this business process please answer the query based on the documentation: {documentation}
        Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), documentation=RunnableLambda(lambda inputs: inputs["query"])|rag_retriever) | chain3
        )
        
        return combined_chain

    if (not process and not causal and xai and not rag ):
        print("Method for combination (False, False, True, False)")        
        prompt = ChatPromptTemplate.from_template(
        """We have aמ XAI explainability view for a particular business process. Given the query {query} regarding this business process please answer the query based on the following information:             
            XAI explainability view: {xai} It is a dictionary, the key in which is a string, representing an activity, and the value is another dictionary, where the key is a string, representing an attribute of the activity, and the value is a float, representing the importance of that attribute in explaining the query.            
            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """)
        chain3 = prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), xai=xai_runnable) | chain3
        )
        
        return combined_chain        

    if (not process and not causal and  xai and rag ):
        print("Method for combination (False, False, True, True)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have an XAI explainability view for a particular business process. We also have some relevant documentation for this business process. Given the query {query} regarding this business process please answer the query based on the following information:             
            XAI explainability view: {xai} It is a dictionary, the key in which is a string, representing an activity, and the value is another dictionary, where the key is a string, representing an attribute of the activity, and the value is a float, representing the importance of that attribute in explaining the query.
            Relevant documentation about the business process: {documentation}

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), documentation=RunnableLambda(lambda inputs: inputs["query"])|rag_retriever,xai=xai_runnable) | chain3    
        )
        return combined_chain

    if (not process and causal and not xai and not rag ):
        print("Method for combination (False, True, False, False)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a causal-dependency model for a particular business process. Given the query {query} regarding this business process please answer the query based on the following information:             
            Causal-dependency model  for this business process: {causal}. It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A causes B, and the value is the connection strength between them.            
            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), causal =causal_runnable) | chain3
        )
        return combined_chain

    if (not process and causal and not xai and rag ):
        print("Method for combination (False, True, False, True)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a causal-dependency model. We also have some relevant documentation for this business process. Given the query {query} regarding this business process please answer the query based on the following information:            
            Causal-dependency model  for this business process: {causal}. It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A causes B, and the value is the connection strength between them.            
            Relevant documentation about the business process: {documentation}

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), documentation=RunnableLambda(lambda inputs: inputs["query"])|rag_retriever, causal =causal_runnable) | chain3
        )
        return combined_chain

    if (not process and causal and  xai and not rag ):
        print("Method for combination (False, True, True, False)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a causal-dependency model and XAI explainability view for a particular business process. Given the query {query} regarding this business process please answer the query based on the following information:             
            Causal-dependency model  for this business process: {causal}. It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A causes B, and the value is the connection strength between them.
            XAI explainability view: {xai} It is a dictionary, the key in which is a string, representing an activity, and the value is another dictionary, where the key is a string, representing an attribute of the activity, and the value is a float, representing the importance of that attribute in explaining the query.

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), causal =causal_runnable, xai=xai_runnable) | chain3
        )
        return combined_chain
        

    if (not process and causal and  xai and rag ):
        print("Method for combination (False, True, True, True)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a causal-dependency model and XAI explainability view for a particular business process. We also have some relevant documentation for this business process. Given the query {query} regarding this business process please answer the query based on the following information:             
            Causal-dependency model  for this business process: {causal}. It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A causes B, and the value is the connection strength between them.
            XAI explainability view: {xai} It is a dictionary, the key in which is a string, representing an activity, and the value is another dictionary, where the key is a string, representing an attribute of the activity, and the value is a float, representing the importance of that attribute in explaining the query.
            Relevant documentation about the business process: {documentation}

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), documentation=RunnableLambda(lambda inputs: inputs["query"])|rag_retriever, causal =causal_runnable, xai=xai_runnable) | chain3
        )
        return combined_chain

    if (process and not causal and not xai and not rag ):
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a process model for a particular business process. Given the query {query} regarding this business process please answer the query based on the following information: 
            Process Model for this business process: {process} . It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A occurs before B, and the value is the connection strength (number of process traces where B follows A) between them.            

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), process=process_runnable) | chain3)

        return combined_chain

    if (process and not causal and not xai and rag ):
        print("Method for combination (True, False, False, True)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a process model for a particular business process. We also have some relevant documentation for this business process. Given the query {query} regarding this business process please answer the query based on the following information: 
            Process Model for this business process: {process} . It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A occurs before B, and the value is the connection strength (number of process traces where B follows A) between them.            
            Relevant documentation about the business process: {documentation}

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), documentation=RunnableLambda(lambda inputs: inputs["query"])|rag_retriever,  process=process_runnable) | chain3)
        return combined_chain

    if (process and not causal and xai and not rag ):
        print("Method for combination (True, False, True, False)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a process model, and XAI explainability view for a particular business process. Given the query {query} regarding this business process please answer the query based on the following information: 
            Process Model for this business process: {process} . It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A occurs before B, and the value is the connection strength (number of process traces where B follows A) between them.           
            XAI explainability view: {xai} It is a dictionary, the key in which is a string, representing an activity, and the value is another dictionary, where the key is a string, representing an attribute of the activity, and the value is a float, representing the importance of that attribute in explaining the query.

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), process=process_runnable,xai=xai_runnable) | chain3
        )
        
        return combined_chain

    if (process and not causal and  xai and rag ):
        print("Method for combination (True, False, True, True)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a process model and XAI explainability view for a particular business process. We also have some relevant documentation for this business process. Given the query {query} regarding this business process please answer the query based on the following information: 
            Process Model for this business process: {process} . It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A occurs before B, and the value is the connection strength (number of process traces where B follows A) between them.            
            XAI explainability view: {xai} It is a dictionary, the key in which is a string, representing an activity, and the value is another dictionary, where the key is a string, representing an attribute of the activity, and the value is a float, representing the importance of that attribute in explaining the query.
            Relevant documentation about the business process: {documentation}

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), documentation=RunnableLambda(lambda inputs: inputs["query"])|rag_retriever, process=process_runnable,xai=xai_runnable) | chain3
        )
        return combined_chain

    if (process and causal and not xai and not rag ):
        print("Method for combination (True, True, False, False)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a process model and causal-dependency model for a particular business process.Given the query {query} regarding this business process please answer the query based on the following information: 
            Process Model for this business process: {process} . It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A occurs before B, and the value is the connection strength (number of process traces where B follows A) between them.
            Causal-dependency model  for this business process: {causal}. It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A causes B, and the value is the connection strength between them.                        

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), causal =causal_runnable, process=process_runnable) | chain3)

        return combined_chain

    if (process and causal and not xai and rag ):
        print("Method for combination (True, True, False, True)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a process model and causal-dependency model  for a particular business process. We also have some relevant documentation for this business process. Given the query {query} regarding this business process please answer the query based on the following information: 
            Process Model for this business process: {process} . It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A occurs before B, and the value is the connection strength (number of process traces where B follows A) between them.
            Causal-dependency model  for this business process: {causal}. It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A causes B, and the value is the connection strength between them.            
            Relevant documentation about the business process: {documentation}

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), documentation=RunnableLambda(lambda inputs: inputs["query"])|rag_retriever, causal =causal_runnable, process=process_runnable) | chain3)
        return combined_chain

    if (process and causal and  xai and not rag ):
        print("Method for combination (True, True, True, False)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a process model, causal-dependency model and XAI explainability view for a particular business process.  Given the query {query} regarding this business process please answer the query based on the following information: 
            Process Model for this business process: {process} . It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A occurs before B, and the value is the connection strength (number of process traces where B follows A) between them.
            Causal-dependency model  for this business process: {causal}. It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A causes B, and the value is the connection strength between them. Tuples for activities which appear in process model but do not appear in causal dependency model might mean that there is precedence relationship between the activities in the tuple, but no causal relationship.
            XAI explainability view: {xai} It is a dictionary, the key in which is a string, representing an activity, and the value is another dictionary, where the key is a string, representing an attribute of the activity, and the value is a float, representing the importance of that attribute in explaining the query.            

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), causal =causal_runnable, process=process_runnable,xai=xai_runnable) | chain3)
        return combined_chain

    if (process and causal and  xai and rag ):
        print("Method for combination (True, True, True, True)")
        combine_answers_prompt = ChatPromptTemplate.from_template(
        """We have a process model, causal-dependency model and XAI explainability view for a particular business process. We also have some relevant documentation for this business process. Given the query {query} regarding this business process please answer the query based on the following information: 
            Process Model for this business process: {process} . It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A occurs before B, and the value is the connection strength (number of process traces where B follows A) between them.
            Causal-dependency model  for this business process: {causal}. It is a dictionary, the key in which is a tuple with two strings, representing two activities A and B , so that A causes B, and the value is the connection strength between them.
            XAI explainability view: {xai} It is a dictionary, the key in which is a string, representing an activity, and the value is another dictionary, where the key is a string, representing an attribute of the activity, and the value is a float, representing the importance of that attribute in explaining the query.
            Relevant documentation about the business process: {documentation}

            Please answer the query in light of this information about the business process. Provide a detailed answer.                        
        """        
        )
        chain3 = combine_answers_prompt | model.getModel() | StrOutputParser()

        combined_chain = (
            RunnableParallel(query=itemgetter("query"), documentation=RunnableLambda(lambda inputs: inputs["query"])|rag_retriever, causal =causal_runnable, process=process_runnable,xai=xai_runnable) | chain3)
        return combined_chain    

    

def getSyntethis(data:RawEventData, query:str, model: BaseLLM,causal: bool, process:bool, xai:bool, rag:bool, retriever: DocumentRetrieverLLM =None, modality =Modality.PARENT, prior_knowledge=True, p_value_threshold=None):
    """Get blended answer based on the user-chosen perspectives for the user provided query

    :param data: event log data
    :type data: RawEventData
    :param query: user query
    :type query: str
    :param model: LLM model wrapper
    :type model: BaseLLM
    :param causal: indication whether to use causal perspective
    :type causal: bool
    :param process: indication whether to use process perspective
    :type process: bool
    :param xai: indication whether to use xai perspective
    :type xai: bool
    :param rag: indicatin whether to use document context
    :type rag: bool
    :param retriever: in case rag is chosen, need to provide previously created retreiver, defaults to None
    :type retriever: DocumentRetrieverLLM, optional
    :param modality: in case causal perspective is chosen, the desired analysis modality, defaults to Modality.PARENT
    :type modality: Modality, optional
    :param prior_knowledge: in case causal perspective is chosen, whether to use prior knowledge or not, defaults to True
    :type prior_knowledge: bool, optional
    :param p_value_threshold: in case causal perspective is chosen, whether to filter causal connections below specified threshold, defaults to None
    :type p_value_threshold: float, optional
    :return: Blended anwer to the query based on all chosen perspectives
    :rtype: str
    """
    chain = _getChain(model,causal, process, xai, rag, retriever)
    result = chain.invoke({"data":data,"query":query,"modality":modality,"prior_knowledge":prior_knowledge,"p_value_threshold":p_value_threshold})
    return result

def getModel(modelType:ModelTypes, modelName: str, temperature: int):
    """Retrieve desired model wrapper based on the specified model provider, model name and temperature

    :param modelType: model provider type
    :type modelType: ModelTypes
    :param modelName: the name of the generative model provided by chosen provider
    :type modelName: str
    :param temperature: temperature to use for generation
    :type temperature: int
    :return: Chosen model wrapper
    :rtype: BaseLLM
    """

    return BaseLLM.getModelLLM(modelType, modelName, temperature)



def getExplanations(data:RawEventData,modality,prior_knowledge = None, p_value_threshold=None ):
    """Return an array of semantic explanations for all process-causal disrepancies 

    :param data: event log data
    :type data: RawEventData
    :param modality: chosen modality for causal discovery
    :type modality: Modality
    :param prior_knowledge: whether to use prior knowledge in causal discovery, defaults to None
    :type prior_knowledge: boolean, optional
    :param p_value_threshold: a filter for causal connections, connections with strength below the specified threshold will be disregarded, defaults to None
    :type p_value_threshold: int, optional
    :return: array of disrepancies
    :rtype: array[str]
    """
    dfg,event_log = pm.discover_dfg(data)  
    causalModel = cd.discover_causal_dependencies(dataObject=data,modality=modality,prior_knowledge=prior_knowledge)
    result = enumerateDisrepancies(dfg, causalModel,p_value_threshold=p_value_threshold)
    return result
      
def enumerateDisrepancies(processModel, causalModel,p_value_threshold=None):   
    """Enumerate the disrepancies between provided process and causal models

    :param processModel: process model as dfg dictionary
    :type processModel: dict
    :param causalModel: causal model as dictionary
    :type causalModel: dict
    :param p_value_threshold: filtering threshold for causal connections
    :type p_value_threshold: int, optional
    :return: array of disrepancies
    :rtype: array[str]
    """
    def _calculateDiff(processRepresentation,causalModel):   
        set1 = set(processRepresentation.keys())
        set2 = set(causalModel.keys())

        removed_edges = list(set1 - set2)
        addedEdges = list(set2 - set1)
        
        return addedEdges, removed_edges
    addedEdge = ' Altering the \'{first_activity}\' completion time is likely to affect the lead time of \'{second_activity}\''
    removedEdge = 'Altering the \'{first_activity}\' completion time is not likely to affect lead time of \'{second_activity}\' '    

    explanations = []
    processRepresentation = pm.getModelProcessRepresentation(processModel)
    causalModel = cd.getModelCausalRepresentation(causalModel,p_value_threshold=p_value_threshold)
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
