# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import pandas as pd
import streamlit as st
from PIL import Image
from pm4py.objects.heuristics_net.obj import HeuristicsNet

import sax.core.process_mining.process_mining as pm


# Function to get the key for a given value
def get_key_for_value(df, value):
    key_series = df[df['Num. Traces'] == value]['Variant']
    if not key_series.empty:
        return key_series.iloc[0]
    else:
        return None
    
def view_heuristic_net(heu_net: HeuristicsNet, format: str = "png", bgcolor: str = "white"):
    format = str(format).lower()
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format, "bgcolor": bgcolor}) 
              
    return gviz

def getProcessModelImage(net: HeuristicsNet) -> Image:
    file = view_heuristic_net(net)      
    full_pm_image = Image.open(file.name)
    return full_pm_image

def getProcessModelAndVariants(dataframe):
    variants = dataframe.getVariants()
    net = pm.discover_heuristics_net(dataframe)
    return variants,net

session_state = st.session_state
if 'variant' not in session_state:
    session_state.variant = None
if 'variants' not in session_state:
    session_state.variants = None
if 'net' not in session_state:
    session_state.net = None
if 'processImage' not in session_state:
    session_state.processImage = None

st.title('Process view')

dataframe= None
net = None
variants = None
if (session_state is not None) and hasattr(session_state, "data") and (session_state.data is not None):
    with st.spinner('Please wait...'):
        dataframe =session_state.data
        if session_state.variants is None and session_state.net is None:
            variants, net= getProcessModelAndVariants(dataframe)
            session_state.variants = variants
            session_state.net = net

if dataframe is not None:  
    if session_state.processImage is  None:          
        full_pm_image = getProcessModelImage(session_state.net)
        session_state.processImage=full_pm_image
    st.image(session_state.processImage)

    df = pd.DataFrame(list(session_state.variants.items()), columns=['Variant', 'Num. Traces'])
    df

    
    if df is not None:
        option = st.selectbox(
        'Which variant would you like to examine?',
        df['Num. Traces'])

        'You selected: ', get_key_for_value(df,option)
        if option:
            st.subheader('Variant view')
            variant = dataframe.getVariant(get_key_for_value(df,option))
            net = pm.discover_heuristics_net(variant)
            variant_image_file = view_heuristic_net(net)
            variant_image = Image.open(variant_image_file.name)
            st.image(variant_image)            
            session_state.variant = variant
 
       

