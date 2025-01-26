# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import traceback
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
    """A document retrieval imeplementation based on Chroma vector store

    """

    def __init__(self,modelClass: BaseLLM,docLocation,filterFiles=None, chunk_size=None, chunk_overlap=None,retrieved_results=None, dbPath=None):
        self._model = modelClass
        self._retriever = self._indexDocuments(modelClass,docLocation,filterFiles,chunk_size,chunk_overlap,retrieved_results,dbPath)        

    def _getDocuments(self,docPath,glob = None):
        """Load all the documents in the given path with the given type and return the loaded docs as array
    
        :param docPath: path to the document/folder
        :type docPath: str
        :param glob: type of documents to embed (txt,pdf,csv), defaults to None
        :type glob: str, optional
        :raises ValidationException: unknown document types in the specified path
        :return: array of loaded documents
        :rtype: array
        """
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
        """Load the documents in the given location , index and store in the Chroma vector store for later contextual retrieval.
        
        :param model: the wrapper for the chosen model provider for embedding model
        :type model: BaseLLM
        :param docLocation: path to the document/documents folder
        :type docLocation: str
        :param filterFiles: extension type of the files to load if any
        :type filterFiles: str, optional
        :param chunk_size: the size of the chunk in text splitter, defaults to None
        :type chunk_size: int, optional
        :param chunk_overlap: the overlap of chunks in text splitter, defaults to None
        :type chunk_overlap: int, optional
        :param retrieved_results: the number of results to retrieve, defaults to None
        :type retrieved_results: int, optional
        :param dbPath: path to the Chroma db, defaults to None
        :type dbPath: str, optional
        :return: retriever wrapper to use for later retreivals agains the specified docs
        :rtype: BaseRetriever
        """
        # load the doc/docs
        try:
            pages = self._getDocuments(docLocation,filterFiles)        

            # split the doc into smaller chunks i.e. chunk_size=500
            chunk_size_to_pass = chunk_size if chunk_size is not None else 500
            chunk_overlap_to_pass = chunk_overlap if chunk_overlap is not None else 50
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size_to_pass, chunk_overlap=chunk_overlap_to_pass)            
            chunks = text_splitter.split_documents(pages)
            import chromadb
            # get embedding model
            embeddings = model.getEmbeddingModel()

            # embed the chunks as vectors and load them into the database
            dbpath_to_pass = dbPath if dbPath is not None else CHROMA_PATH                                                
            db= Chroma.from_documents(chunks, embeddings, persist_directory=dbpath_to_pass,
                    client_settings=chromadb.config.Settings(
                    anonymized_telemetry=False,
                    is_persistent=True,
                    persist_directory=dbpath_to_pass
                ))
            db.persist()  # Add explicit persist        
            # expose this index in a retriever interface
            kwargs_to_pass= retrieved_results if retrieved_results is not None else 10
            retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":kwargs_to_pass})        

            # create a chain to answer questions 
            return retriever
        except Exception as e:
            print(f"Stack trace: ", traceback.format_exc())
            raise e
    

    # ----- Retrieval and Generation Process -----

    def get_retriever(self):
        """Return the embedded retriever stored in this wrapper"""
        return self._retriever
 
   