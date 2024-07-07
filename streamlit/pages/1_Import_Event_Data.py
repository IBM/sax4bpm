# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import os
import sys
from pathlib import Path

import streamlit as st

# # Get the current directory (where the notebook is located)
# notebook_dir = os.getcwd()
# # Get the parent directory
# parent_dir = os.path.abspath(os.path.join(notebook_dir, os.pardir))
# # Get two directories up
# #two_dirs_up = os.path.abspath(os.path.join(parent_dir, os.pardir))
# # Add the project directory to the Python path
#sys.path.append(parent_dir)
current_dir =  os.path.dirname(os.path.realpath(__file__))
#current_dir = os.getcwd()
print("Current",current_dir)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
root_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))
print("Parent", parent_dir)
print("root",root_dir)
sys.path.append(root_dir)

import sax.core.process_mining.process_mining as pm

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

@st.cache_data
def load_data(fileName,case_id, activity_key,timestamp_key,timestamp_format,start_timestamp_key=None,lifecycle_type=None):    
    dataframe = None    
    file_extension = Path(fileName).suffix.lower()    
    print(file_extension)
    print(fileName)
    # Check the file extension and invoke the appropriate parser
    params = {"eventlog":fileName,"case_id": case_id, "activity_key": activity_key, "timestamp_key": timestamp_key,"timestamp_format":timestamp_format}    
    if lifecycle_type is not None:
        params["lifecycle_type"]:lifecycle_type   
    if file_extension == '.csv':
        if start_timestamp_key is not None:
            params["starttime_column"]=start_timestamp_key
        dataframe = pm.import_csv(**params)
    elif file_extension == '.mxml':
        dataframe = pm.import_mxml(**params)
    elif file_extension == '.xes':
        dataframe = pm.import_xes(**params)
    else:
        st.warning("Unsupported file format. Please upload a .csv, .xml, or .xes file.")
    return dataframe

st.title('Import and analyze event log')



# File Uploader
# Create a session state object
session_state = st.session_state
if 'data' not in session_state:
    session_state.data = None

st.divider()    
st.header("Event Log Uploader")
uploaded_file = st.file_uploader("Choose an event log file:")
if uploaded_file is not None:     
    # Save the uploaded file to disk and get the file path
    file_path = save_uploaded_file(uploaded_file)     
    # Create a text element and let the reader know the data is loading.
    st.divider()
    st.header("Enter parameters for parsing the event log")
    case_id = st.text_input("CaseID column", value="case:concept:name")
    activity_key = st.text_input("Activity column", value="concept:name")
    timestamp_key = st.text_input("Timestamp column", value="time:timestamp")
    timestamp_format = st.text_input("Timestamp format", value="%Y-%m-%d %H:%M:%S.%f")

    relevant_input4 = st.checkbox("Does the event log has start time column?")
    if relevant_input4:
        start_timestamp_key = st.text_input("Start time column", value="start:timestamp")
    else:
        start_timestamp_key=None

    relevant_input5 = st.checkbox("Does the event log has lifecycle events?")
    if relevant_input5:
        lifecycle_type = st.text_input("Lifecycle column", value="lifecycle:transition")
    else:
        lifecycle_type=None
    if st.button("Perform analysis"):        
        data_load_state = st.text('Loading data...')        
        # Load 10,000 rows of data into the dataframe.
        try:   
            dataframe = load_data(file_path,case_id=case_id,activity_key=activity_key,timestamp_key=timestamp_key,timestamp_format=timestamp_format,start_timestamp_key=start_timestamp_key,lifecycle_type=lifecycle_type)
        except Exception as e:
            print(e)
            dataframe = None
            st.error(f"An error occurred: {str(e)}")
        
        if dataframe is not None:
            # Notify the reader that the data was successfully loaded.
            data_load_state.text("Done!")
            session_state.data = dataframe 
            session_state.variants = None
            session_state.net = None
            session_state.processImage=None           
            st.write(dataframe.getData())
            dataframe.getData()
            #st.experimental_rerun()

