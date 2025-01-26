
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from PIL import Image
import time
import sax.core.synthesis.sax_explainability as ex
from sax.core.synthesis.llms.base_llm import ModelTypes
from sax.core.causal_process_discovery.causal_constants import Modality
import sax.core.synthesis.sax_explainability as sax_explainability
from functools import partial


from PIL import Image
im = Image.open('./images/sax4bpm_logo6_t.png')
st.html("""
  <style>
    [alt=Logo] {
      height: 7rem;
    }
  </style>
        """)
#st.logo(im, size="large", link=None)
st.logo(im, link=None)

st.title('XStudio')        

@st.cache_resource(show_spinner=True)
def create_retriever(path):
    try:
        print("Before instantiating RAG with path: ", path)
        docPath = path
        retreiver = sax_explainability.createDocumentContextRetriever(ModelTypes.OPENAI, "gpt-3.5-turbo", 1.5, docPath,"pdf")
        print("After instantiating RAG")
        return retreiver
    except Exception as e:
        print(f"Error in create_retriever: {str(e)}")
        raise e

def save_uploaded_file(uploaded_file):
    # Check if the file was uploaded
    if uploaded_file is not None:
        # Create a folder for storing uploaded files (if not exists)
        os.makedirs("uploads", exist_ok=True)
        # Save the uploaded file to disk
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None


session_state = st.session_state
if 'processModel' not in session_state:
    session_state.processModel = None
if 'causalModel' not in session_state:
    session_state.causal_model = None
if 'text_area_value' not in st.session_state:
    st.session_state.text_area_value = "Answer will appear here"


if (session_state is not None) and hasattr(session_state, "variant") and (session_state.variant is not None):
    variant= session_state.variant
    data = session_state.data
    retriever = None

    question = st.text_area('Query',placeholder = "Input your question here...")       
    process = st.checkbox('Process view')
    causal = st.checkbox('Causal view')
    xai = st.checkbox('XAI view')
    rag = st.checkbox('Content view')
    if (rag):        
        # st.header("Documentation Uploader")
        # uploaded_documentation = st.file_uploader("Choose a documentation file:")
        # if uploaded_documentation is not None:   
        #     file_path = save_uploaded_file(uploaded_documentation)
        #     uploaded_documentation = "C:/Data/Automation/SAX/Projects/AutoTwin/SKG/Croma/documents"
        #     retriever = create_retriever(file_path)
        st.header("Documentation")
        upload_type = st.radio("Select upload type:", ["File", "Directory"])
    
        if upload_type == "File":
            uploaded_documentation = st.file_uploader("Choose a documentation file:")
            if uploaded_documentation is not None:   
                file_path = save_uploaded_file(uploaded_documentation)
        else:
            doc_directory = st.text_input("Enter directory path:", 
                                    placeholder="e.g., C:/Documents/PDFs")
            if doc_directory and os.path.isdir(doc_directory):
                file_path = doc_directory
            elif doc_directory:
                st.error("Invalid directory path")
            
        if 'file_path' in locals() and file_path:
            retriever = create_retriever(file_path)
    model = ex.getModel(ModelTypes.OPENAI, "gpt-3.5-turbo", 1.5)
    

    def update_answer(data,variant,question,model,causal, process, xai, rag, retriver, modality, prior_knowledge, p_value_threshold):
        with st.spinner('Please wait...'):     
            print("in update_answer: answering query", question)   
            st.session_state.text_area_value = ex.getSyntethis(data, question, model,causal, process, xai, rag, retriver, modality, prior_knowledge, p_value_threshold,[variant])        
            st.session_state.button_pressed = True
            print("Button pressed inside update_answer, the answer was: ", st.session_state.text_area_value)

        return

    def analyze_callback():
        update_answer(
            data,
            variant,
            question,
            model,
            causal,
            process,
            xai,
            rag,
            retriever,
            Modality.CHAIN,
            True,
            None
        )


    button = st.button("Analyze!", on_click=analyze_callback)        

    if button:
        answer = st.text_area("Answer:", value=st.session_state.text_area_value, height=500,key='text_area')



