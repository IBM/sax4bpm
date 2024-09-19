# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import graphviz
import numpy as np
import streamlit as st
from PIL import Image
from lingam.utils import make_dot
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from sax.core.causal_process_discovery.algorithms.base_causal_alg import CausalResultInfo

import sax.core.causal_process_discovery.causal_discovery as cd
import sax.core.process_mining.process_mining as pm
import sax.core.synthesis.sax_explainability as ex



def view_heuristic_net(heu_net: HeuristicsNet, format: str = "png", bgcolor: str = "white"):
    format = str(format).lower()
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format, "bgcolor": bgcolor}) 
              
    return gviz

def view_causal_dependencies(dependencies: CausalResultInfo, p_value_threshold: float=0.3):
    """
    View the causal dependency model graph

    :param dependencies: causal dependency model representation
    :type dependencies: CausalResultInfo
    :param p_value_threshold: threshold for displaying causal relationships, no edges with coefficients less than specified will be displayed, defaults to None
    :type p_value_threshold: float, optional
    :return: graph
    :rtype: graphviz.Digraph
    """        
    # Convert the input matrix to a NumPy array for easier manipulation
    np_matrix = dependencies.getAdjacencyMatrix()
    if p_value_threshold is not None:
        np_matrix = np.array(np_matrix)

        # Create a boolean mask where True indicates that the value is below the p-value threshold
        mask = np_matrix < p_value_threshold 
        
        # Replace values below the p-value threshold with zeros
        np_matrix[mask] = 0
        
    dot= make_dot(np_matrix, labels = dependencies.getColumns())        
    return dot

st.title('Analysis view')
session_state = st.session_state
if 'processModel' not in session_state:
    session_state.processModel = None
if 'causalModel' not in session_state:
    session_state.causal_model = None

if (session_state is not None) and hasattr(session_state, "variant") and (session_state.variant is not None):
    with st.spinner('Please wait...'):
        #display both process model and causal model alongside        
        variant= session_state.variant
        print("Starting process mining: variant",variant)
        data = session_state.data
        net = pm.discover_heuristics_net(data,[variant])
        dfg, event_log = pm.discover_dfg(data,[variant])
        variant_image_file = view_heuristic_net(net)
        variant_image = Image.open(variant_image_file.name)
        session_state.processModel=dfg
        print("Process Model:",session_state.processModel)
        
        try:
            print("Starting causal discovery: variant",variant)
            causal_model=cd.discover_causal_dependencies(data,[variant],prior_knowledge=True)            
            print("Causal model:")
            print(causal_model.adjacencyMatrix)
            print(causal_model.columns)
            if causal_model.columns:
                session_state.causalModel=causal_model
                causal_image_grapth = view_causal_dependencies(causal_model)
                causal_image_grapth.format = 'png'
                causal_image_grapth.render('causal_image', cleanup=True)  # Save the PNG image            
                causal_graph_image = Image.open('causal_image.png')
            else:
                session_state.causalModel=None
                st.error("Causal model is empty: mostly likely due to the fact that you chose variant with too few instances to analyze")            
        except Exception as e:
            st.error("An error occurred: {}".format(str(e)))
            print(e)
            session_state.causalModel=None
        


    #display the process model alongside the causal model
    if (session_state.processModel) is not None and (session_state.causalModel) is not None:      
        col1, col2 = st.columns(2)

        desired_width = 600
        desired_height = 700

        scale_factor_image1 = max(desired_width / variant_image.width, desired_height / variant_image.height)
        scale_factor_image2 = max(desired_width / causal_graph_image.width, desired_height / causal_graph_image.height)

        image1 = variant_image.resize((int(variant_image.width * scale_factor_image1), int(variant_image.height * scale_factor_image1)))
        image2 = causal_graph_image.resize((int(causal_graph_image.width * scale_factor_image2), int(causal_graph_image.height * scale_factor_image2)))

        
        st.image(image1, caption='Process Model', use_column_width=False, width=desired_width, output_format='JPEG')
        st.write(
            f'<style>div.row-widget.stHorizontal {{"flex-direction": "row";}}</style>',
            unsafe_allow_html=True,
        )
        st.image(image2, caption='Causal Model', use_column_width=False, width=desired_width, output_format='JPEG')

        st.subheader('Explanations')
        explainaiblity=ex.enumerateDisrepancies(session_state.processModel,session_state.causalModel,0.3)
        st.table({"Guidance": explainaiblity})
        