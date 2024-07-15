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

def _getChain(model: BaseLLM,causal: bool, process:bool, xai:bool, rag:bool, retriever: DocumentRetrieverLLM =None):   
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
    chain = _getChain(model,causal, process, xai, rag, retriever)
    result = chain.invoke({"data":data,"query":query,"modality":modality,"prior_knowledge":prior_knowledge,"p_value_threshold":p_value_threshold})
    return result

def getModel(modelType:ModelTypes, modelName: str, temperature: int):
    return BaseLLM.getModelLLM(modelType, modelName, temperature)



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
        
