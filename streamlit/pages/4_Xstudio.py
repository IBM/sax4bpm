
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
st.logo(im, size="large", link=None)

st.title('XStudio')        



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

    question = st.text_area('Query',placeholder = "Input your question here...")       
    process = st.checkbox('Process view')
    causal = st.checkbox('Causal view')
    xai = st.checkbox('XAI view')
    model = ex.getModel(ModelTypes.OPENAI, "gpt-3.5-turbo", 1.5)

    def update_answer(data,variant,question,model,causal, process, xai, rag, retriver, modality, prior_knowledge, p_value_threshold):
        with st.spinner('Please wait...'):     
            print("in update_answer:")   
            st.session_state.text_area_value = ex.getSyntethis(data, question, model,causal, process, xai, False, None, modality, prior_knowledge, p_value_threshold,[variant])        
            st.session_state.button_pressed = True
            print("Button pressed inside update_answer")

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
            False,
            None,
            Modality.CHAIN,
            True,
            None
        )


    button = st.button("Analyze!", on_click=analyze_callback)        

    if button:
        answer = st.text_area("Answer:", value=st.session_state.text_area_value, height=500,key='text_area')



