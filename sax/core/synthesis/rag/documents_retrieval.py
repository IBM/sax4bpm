# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.directory import DirectoryLoader
from langchain_community.document_loaders.text import TextLoader
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.vectorstores.chroma import Chroma
from sax.core.synthesis.exceptions.validation import ValidationException
from sax.core.synthesis.llms.base_llm import BaseLLM
from sax.core.synthesis.rag.base_retrieval import BaseRetriever


CHROMA_PATH = "db/"

class DocumentRetrieverLLM(BaseRetriever):    

    def __init__(self,modelClass: BaseLLM,docLocation,filterFiles=None, chunk_size=None, chunk_overlap=None,retrieved_results=None, dbPath=None):
        self._model = modelClass
        self._retriever = self._indexDocuments(modelClass,docLocation,filterFiles,chunk_size,chunk_overlap,retrieved_results,dbPath)

    def _getDocuments(self,docPath,glob = None):
        documents = []
        if docPath.endswith('.csv'):
            loader =  CSVLoader(docPath)
            documents = loader.load()
        elif docPath.endswith('.pdf'):
            loader =  PyPDFLoader(docPath)
            documents = loader.load()
        elif docPath.endswith('.txt'):             
            loader = TextLoader(docPath)
            documents = loader.load()
        elif os.path.isdir(docPath) and glob:
            if glob == "pdf":
                for file in os.listdir(docPath):
                    if file.endswith('.pdf'):
                        pdf_path = os.path.join(docPath, file)
                        loader = PyPDFLoader(pdf_path)
                        documents.extend(loader.load())
            elif glob == "csv":
               for file in os.listdir(docPath):
                    if file.endswith('.csv'):
                        csv_path = os.path.join(docPath, file)
                        loader = CSVLoader(csv_path)
                        documents.extend(loader.load())                
            elif glob =="txt": 
               for file in os.listdir(docPath):
                    if file.endswith('.txt'):
                        txt_path = os.path.join(docPath, file)
                        loader = TextLoader(txt_path)                        
                        documents.extend(loader.load())                         
        else: raise ValidationException("ValidationError: no appropriate loader for doc: ",docPath)
        return documents


    def _indexDocuments(self, model: BaseLLM,docLocation,filterFiles=None,chunk_size=None,chunk_overlap=None,retrieved_results=None,dbPath=None):
        # load the doc/docs
        pages = self._getDocuments(docLocation,filterFiles)        

        # split the doc into smaller chunks i.e. chunk_size=500
        chunk_size_to_pass = chunk_size if chunk_size is not None else 500
        chunk_overlap_to_pass = chunk_overlap if chunk_overlap is not None else 50
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size_to_pass, chunk_overlap=chunk_overlap_to_pass)
        chunks = text_splitter.split_documents(pages)

        # get embedding model
        embeddings = model.getEmbeddingModel()

        # embed the chunks as vectors and load them into the database
        dbpath_to_pass = dbPath if dbPath is not None else CHROMA_PATH
        db= Chroma.from_documents(chunks, embeddings, persist_directory=dbpath_to_pass)
        # expose this index in a retriever interface
        kwargs_to_pass= retrieved_results if retrieved_results is not None else 10
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":kwargs_to_pass})

        # create a chain to answer questions 
        qa = RetrievalQA.from_chain_type(
            llm=model.getModel(), chain_type="map_reduce", retriever=retriever, return_source_documents=True)
        return qa
    

    # ----- Retrieval and Generation Process -----

    def get_context(self, query):        
        result = self._retriever({"query": query})
        return result
 
    def getModel(self)-> BaseLLM:      
        return self._model
