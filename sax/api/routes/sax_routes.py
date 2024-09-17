# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
import os
import tempfile
from pathlib import Path

from flask import Blueprint, current_app, jsonify, make_response, request

from sax.api.exceptions.validation import ValidationException
from sax.core.causal_process_discovery import causal_discovery as cd
from sax.core.causal_process_discovery.causal_constants import Modality
from sax.core.process_mining import process_mining as pm
from sax.core.synthesis import sax_explainability as sx

sax_routes = Blueprint("sax", __name__, url_prefix="/sax")

def import_event_log_file(file,case_id,activity_key,timestamp_key,timestamp_format,lifecycle_type=None, start_timestamp_key=None,):          
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, file.filename)
    file.save(temp_file_path)

    # Call the third-party method with the file path
    file_extension = Path(file.filename).suffix.lower()
    params = {"eventlog":temp_file_path,"case_id": case_id, "activity_key": activity_key, "timestamp_key": timestamp_key,"timestamp_format":timestamp_format}    
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
        raise ValidationException("ValidationError: Incorrect file type, sax4bpm supports .xes, .mxml, .csv file types","Incorrect file type, sax4bpm supports .xes, .mxml, .csv file types")

    # Clean up the temporary file
    os.remove(temp_file_path)
    current_app.state.update_state(dataframe)

    return f"Finished importing event log file"

def get_variants():        
    imported_data = current_app.state.get_state_copy()   
    if not imported_data:
         raise ValidationException("ValidationError: No data imported yet. Call importEventLogFile first","No data imported yet. Call importEventLogFile first")        
    return imported_data.getVariants()

def get_process_model(variant_names, model_type):
    imported_data = current_app.state.get_state_copy()   
    if not imported_data:
         raise ValidationException("ValidationError: No data imported yet. Call importEventLogFile first","No data imported yet. Call importEventLogFile first")
     
    dfg = None
    if model_type == 'DFG':
        dfg,event_log = pm.discover_dfg(dataframe=imported_data,variants=variant_names)        
    elif model_type == 'HEURISTIC':
        heuristic_net= pm.discover_heuristics_net(dataframe=imported_data,variants=variant_names)       
        dfg = heuristic_net.dfg               
    else:
        raise ValidationException("ValidationError: Unsupported process model for discovery, use DFG or HEURISTIC"," Unsupported process model for discovery, use DFG or HEURISTIC")
    result_list =  [{"from": pair[0], "to": pair[1], "items": count} for pair, count in dfg.items()]
    return result_list

def get_causal_graph(variant_names, modality, prior_knowledge = False, p_value_threshold = None):
    imported_data = current_app.state.get_state_copy()   
    if not imported_data:
         raise ValidationException("ValidationError: No data imported yet. Call importEventLogFile first","No data imported yet. Call importEventLogFile first")
    
    modality = Modality.from_string(modality)     

    causal_graph = cd.getDataCausalRepresentation(dataframe=imported_data,modality=modality,prior_knowledge=prior_knowledge,p_value_threshold=p_value_threshold,variants=variant_names)
    result_list =  [{"from": pair[0], "to": pair[1], "items": count} for pair, count in causal_graph.items()]
    return result_list

def get_explanations(variant_names,modality,prior_knowledge,p_threshold=None):   
    imported_data = current_app.state.get_state_copy()   
    if not imported_data:
         raise ValidationException("ValidationError: No data imported yet. Call importEventLogFile first","No data imported yet. Call importEventLogFile first")
       
    modality = Modality.from_string(modality)     
    return sx.getExplanations(data=imported_data,modality=modality,variants=variant_names,prior_knowledge=prior_knowledge,p_value_threshold=p_threshold)

@sax_routes.route("/test_response")
def test_repsonse():
    return make_response(
        'Test worked!',
        200
    )


@sax_routes.route('/importEventLogFile', methods=['POST'])
def import_event_log_file_route():
    """
    Endpoint to import event log file.

    ---
    parameters:
    - name: file
      in: formData
      type: file
      required: true
      description: The event log file to import
    - name: case_id
      in: query
      type: string
      required: true
      description: Case ID column or attribute name
    - name: activity_key
      in: query
      type: string
      required: true
      description: Activity column or attribute name
    - name: timestamp_key
      in: query
      type: string
      required: true
      description: Timestamp column or attribute name
    - name: timestamp_format
      in: query
      type: string
      required: true
      description: Timestamp column or attribute name
    - name: lifecycle_type
      in: query
      type: string
      required: false
      description: Lifecycle column or attribute name if present in the event log
    - name: start_timestamp_key
      in: query
      type: string
      required: false
      description: Start Timestamp column or attribute name if present in the event log

    responses:
      200:
        description: Successfully imported event log file
      400:
        description: No event log part
      500:
        description: Internal Server Error
    """    
    case_id = request.args.get('case_id')
    activity_key = request.args.get('activity_key')
    timestamp_key = request.args.get('timestamp_key')
    timestamp_format = request.args.get('timestamp_format')
    lifecycle_type = request.args.get('lifecycle_type', None)
    start_timestamp_key = request.args.get('start_timestamp_key', None)
    
    if 'file' not in request.files:
        raise ValidationException("ValidationError:No event log attached to the request","No event log attached to the request")        
    
    file = request.files['file']
    
    if file.filename == '':
        raise ValidationException("ValidationError:No event log attached to the request","No event log attached to the request") 
    
    try:
      result = import_event_log_file(file,case_id,activity_key,timestamp_key,timestamp_format,lifecycle_type, start_timestamp_key)    
    except Exception as e:
      error = str(e)
      raise ValidationException(error,"Application exception") from e
    return jsonify({"result": result})


@sax_routes.route('/variants', methods=['GET'])
def get_variants_route():
    """
    Endpoint to get variants and their instance counts.

    ---
    responses:
      200:
        description: A dictionary containing variant names and their instance counts.
        content:
          application/json:
            schema:
              type: object
              example:
                variant1: 100
                variant2: 50
                variant3: 75
      500:
        description: Internal Server Error
    """    
    try:
      variants = get_variants()    
    except Exception as e:
      error = str(e)
      raise ValidationException(error,"Application exception") from e
    return jsonify(variants)

@sax_routes.route('/processModel', methods=['GET'])
def get_process_model_route():
    """
    Endpoint to get the process model for a given variant. To invoke for all variants, use 'GET /processModel?variant_names=ALL&model_type=DFG'. To invoke for one or more particular variant, use 'GET /processModel?variant_names=A,B,C,D&variant_names=C,E,D,F&variant_names=M,A,B,D,L&model_type=DFG'



    ---
    parameters:
      - name: variant_names
        in: query
        type: string
        required: true
        description: The names of the variants (or ALL for all the variants)
      - name: model_type
        in: query
        type: string
        required: true
        description: The type of process model (e.g., DFG or HEURISTIC)

    responses:
      200:
        description: A JSON array containing the process model.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  from:
                    type: string
                    description: The starting node of the transition.
                  to:
                    type: string
                    description: The ending node of the transition.
                  items:
                    type: integer
                    description: The number of occurrences of the transition.
      500:
        description: Internal Server Error        
    """    
    variant_names = request.args.getlist('variant_names')    
    model_type = request.args.get('model_type')    

    if not variant_names or not model_type:
        return jsonify({"error": "variant_names and model_type are required"}), 400
    
    if len(variant_names) == 1 and variant_names[0] == 'ALL':
        variant_names = None
    
    try:
      process_model = get_process_model(variant_names, model_type)    
    except Exception as e:
      error = str(e)
      raise ValidationException(error,"Application exception") from e
    return jsonify(process_model)

@sax_routes.route('/causalGraph', methods=['GET'])
def get_causal_graph_route():
    """
    Endpoint to get the causal graph for a given variant and modality.

    ---
    parameters:
      - name: variant_names
        in: query
        type: string
        required: true
        description: The name of the variant (or ALL for all the variants)
      - name: modality
        in: query
        type: string
        required: true
        description: The modality of causal graph ('Chain' or 'Parent')
      - name: prior_knowledge
        in: query
        type: boolean
        required: false
        description: Flag indicating whether prior knowledge should be used in the discovery process
      - name: p_value_threshold
        in: query
        type: number
        required: false
        description: The threshold value for p-value

    responses:
      200:
        description: A JSON array containing the causal graph.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  from:
                    type: string
                    description: The starting node of the causal relationship.
                  to:
                    type: string
                    description: The ending node of the causal relationship.
                  items:
                    type: number
                    description: The strength of the causal relationship.
      500:
        description: Internal Server Error
    """

    variant_names = request.args.getlist('variant_names')
    modality = request.args.get('modality')
    prior_knowledge = request.args.get('prior_knowledge', None)
    p_value_threshold = request.args.get('p_value_threshold', None)

    if not variant_names or not modality:
        return jsonify({"error": "variant_names and modality are required"}), 400
    
    if len(variant_names) == 1 and variant_names[0] == 'ALL':
        variant_names = None

    try:
      causal_graph = get_causal_graph(variant_names, modality,prior_knowledge,p_value_threshold)            
    except Exception as e:
      error = str(e)
      raise ValidationException(error,"Application exception") from e
    return jsonify(causal_graph)

@sax_routes.route('/explanations', methods=['GET'])
def get_explanations_route():
    """
    Endpoint to get explanations for discrepancies between process and causal views in a given variant and modality.

    ---
    parameters:
      - name: variant_names
        in: query
        type: string
        required: true
        description: The name of the variant or ALL for the whole event log
      - name: modality
        in: query
        type: string
        required: true
        description: The modality for causal discovery ('Chain' or 'Parent')
      - name: prior_knowledge
        in: query
        type: boolean
        required: false
        description: Flag indicating whether prior knowledge should be used in the explanation process
      - name: p_value_threshold
        in: query
        type: number
        required: false
        description: The threshold value for p-value

    responses:
      200:
        description: A JSON array containing explanations for discrepancies.
        content:
          application/json:
            schema:
              type: array
              items:
                type: string
                description: Explanation for a discrepancy
      500:
        description: Internal Server Error
    """    
    variant_names = request.args.getlist('variant_names')
    modality = request.args.get('modality')
    prior_knowledge = request.args.get('prior_knowledge', None)
    p_threshold = request.args.get('p_value_threshold', None)    

    if not variant_names or not modality:
        return jsonify({"error": "variant_names and modality are required"}), 400
    
    if len(variant_names) == 1 and variant_names[0] == 'ALL':
        variant_names = None

    try:
      discrepancies = get_explanations(variant_names,modality,prior_knowledge,p_threshold)    
    except Exception as e:
      error = str(e)
      raise ValidationException(error,"Application exception") from e
    return jsonify(discrepancies)
