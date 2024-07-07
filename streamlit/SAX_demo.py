# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import streamlit as st

st.set_page_config(
    page_title="SAX4BPM",
    page_icon="👋",
)

st.write("# Welcome to SAX4BPM! 👋")

st.sidebar.success("Import an event log and select a desired view.")

st.markdown(
    """
    ``SAX4BPM`` is a high-level OO Python package which aims to provide an easy and intuitive way of exploring various perspectives into your business-process.
    
    It can allow you to mine and view the process model, which in turns drives causal-execution dependency discovery of causal relationships between process activities. 
    This can provide the user more elaborate picture into which activities actually affect execution of the other activities in the process. 

    Additionally the causal execution dependency model can drive the explainability of various outcomes of decisions made within the scope of the business processes 
    and provide more precise view on feature dependency of those decisions.
    
    To bring it all together we will integrate all perspectives together using LLMs (Large Language Model) to construct single human-interpretable view into explainations of various process decision
    and outcomes.

    
     **👈 Import an event log file and go step by step through views in the sidebar**  
"""
)