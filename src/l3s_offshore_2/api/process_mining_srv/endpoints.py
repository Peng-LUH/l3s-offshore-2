from http import HTTPStatus
import os, io, json
import random
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import tempfile

# import werkzeug
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# import flask
# from flask import request, url_for

# import flask-restx
from flask_restx import Namespace, Resource, abort
# from flask_restx.reqparse import RequestParser
import pm4py

## import dto
from .dto import (random_request_model, random_response_model)

## import logic
from .logic import (allowed_file_extension, inductive_miner, event_log_processer)

ns_pm = Namespace("Process Mining", validate=True)

## dto registration
ns_pm.models[random_request_model.name] = random_request_model
ns_pm.models[random_response_model.name] = random_response_model
# ns_pm.models[miner_request_model.name] = miner_request_model
# ns_pm.models[miner_response_model.name] = miner_response_model

# Define a parser on this namespace for file uploads
discovery_upload_parser = ns_pm.parser()
discovery_upload_parser.add_argument(
    'file',
    location='files',                # multipart/form-data
    type=FileStorage,                # yields a FileStorage instance
    required=True,
    help='CSV file to upload'
)

analysis_upload_parser = ns_pm.parser()
analysis_upload_parser.add_argument(
    'event_log', location='files', type=FileStorage, required=True,
    help='CSV event log file'
)
analysis_upload_parser.add_argument(
    'pnml_model', location='files', type=FileStorage, required=True,
    help='PNML Petri net file'
)



@ns_pm.route("/inductive-miner", endpoint="inductive-miner")
@ns_pm.doc(
    description=(
        "Petri net discovery based on inductive miner."
        "Upload an event_log.csv. **Example:**\n\n"
        "```\n"
        "case_id;activity;timestamp;costs;resource\n"
        "1;r;2024-12-17 11:19:35+0000;100;Resource1\n"
        "1;s;2024-12-23 18:05:37+0000;200;Resource2\n"
        "2;r;2024-12-23 17:05:37+0000;100;Resource1\n"
        "2;sb;2024-12-23 18:05:37+0000;200;Resource2\n"
        "```\n"
        "Upload an event_log.xes. **Example: https:// ** \n\n"
        
        "Note: A wrapper of PM4PY Inductive Minder.\n\n"
    )
)
class InductiveMiner(Resource):
    @ns_pm.response(int(HTTPStatus.CREATED), "Success")
    @ns_pm.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
    @ns_pm.expect(discovery_upload_parser)
    def post(self):
        try:
            # retrive the data
            args = discovery_upload_parser.parse_args()
            uploaded_file: FileStorage = args['file']
            filename = secure_filename(uploaded_file.filename)
            
            # 1. Extension
            if not allowed_file_extension(filename):
                raise TypeError("Only .csv or .xes files are allowed.")
            
            file_type = uploaded_file.filename.rsplit('.', 1)[1].lower()
            
            pnml_file_path = inductive_miner(uploaded_event_log=uploaded_file)


            # Read into memory
            with open(pnml_file_path, 'r', encoding='utf-8') as f:
                pnml_data = f.read()
            
            # Return as JSON with 201 Created
            response = {
                'filename': os.path.basename(pnml_file_path.rsplit('/', 1)[-1].lower()),
                'results': pnml_data
            }
            
            # Delete the file immediately
            os.remove(pnml_file_path)
            
            return response, HTTPStatus.CREATED
        except TypeError as e:
            return {"message": e.args}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            return {"message": e.args}, HTTPStatus.INTERNAL_SERVER_ERROR



@ns_pm.route("/analysis/fitness-token-play", endpoint="fitness-token-play")
@ns_pm.doc(
    description=(
        "Fitness analysis based on token-play.\n"
        "File 1: Upload an event log in .csv or in .xes format.\n"
        "File 2: Upload a Petri net in .pnml format.\n"
    )
)
class AnalysisFitnessTokenPlay(Resource):
    @ns_pm.response(int(HTTPStatus.CREATED), "Success")
    @ns_pm.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
    @ns_pm.expect(analysis_upload_parser)
    def post(self):
        
        args = analysis_upload_parser.parse_args()
        event_log_file: FileStorage = args['event_log'] # FileStorage instance for CSV
        pnml_file: FileStorage = args['pnml_model'] # FileStorage instance for PNML
        
        try:
            event_log_filename = secure_filename(event_log_file.filename)
            pnml_filename = secure_filename(pnml_file.filename)
            
            if not allowed_file_extension(event_log_filename):
                raise TypeError("Invalid format of event log. Allowed: csv or xes")
            
            
            event_log = event_log_processer(uploaded_event_log=event_log_file)
            
            pnml_file_extension = pnml_filename.rsplit('.', 1)[-1].lower()
            if not pnml_file_extension == 'pnml':
                raise TypeError("Not a pnml file.")
            
            # create a temp file on disk
            temp_pnml = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
            temp_pnml_path = temp_pnml.name
            temp_pnml.close()
            
            # write the uploaded data into the temp file
            pnml_file.save(temp_pnml_path)
            
            
            pn, im, fm = pm4py.read_pnml(file_path=temp_pnml_path)
            
            
            results = pm4py.fitness_token_based_replay(log=event_log, petri_net=pn, initial_marking=im, final_marking=fm)
            
            print(results)
            
            return {"result": results}, HTTPStatus.ACCEPTED
        except TypeError as e:
            return {"message": e.args}, HTTPStatus.BAD_REQUEST
    

@ns_pm.route("/analysis/fitness-alignment", endpoint="fitness-alignment")
@ns_pm.doc(
    description=(
        "Fitness analysis based on alignment.\n"
        "File 1: Upload an event log in .csv or in .xes format.\n"
        "File 2: Upload a Petri net in .pnml format.\n"
    )
)
class AnalysisFitnessAlignment(Resource):
    @ns_pm.response(int(HTTPStatus.CREATED), "Success")
    @ns_pm.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
    @ns_pm.expect(analysis_upload_parser)
    def post(self):
        
        args = analysis_upload_parser.parse_args()
        event_log_file: FileStorage = args['event_log'] # FileStorage instance for CSV
        pnml_file: FileStorage = args['pnml_model'] # FileStorage instance for PNML
        
        try:
            event_log_filename = secure_filename(event_log_file.filename)
            pnml_filename = secure_filename(pnml_file.filename)
            
            if not allowed_file_extension(event_log_filename):
                raise TypeError("Invalid format of event log. Allowed: csv or xes")
            
            
            event_log = event_log_processer(uploaded_event_log=event_log_file)
            
            pnml_file_extension = pnml_filename.rsplit('.', 1)[-1].lower()
            if not pnml_file_extension == 'pnml':
                raise TypeError("Not a .pnml file.")
            
            # create a temp file on disk
            temp_pnml = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
            temp_pnml_path = temp_pnml.name
            temp_pnml.close()
            
            # write the uploaded data into the temp file
            pnml_file.save(temp_pnml_path)
            
            
            pn, im, fm = pm4py.read_pnml(file_path=temp_pnml_path)
            
            
            results = pm4py.fitness_alignments(log=event_log, petri_net=pn, initial_marking=im, final_marking=fm)
            
            print(results)
            
            return {"result": results}, HTTPStatus.ACCEPTED
        except TypeError as e:
            return {"message": e.args}, HTTPStatus.BAD_REQUEST
    


# @ns_pm.route("/analysis/fitness-footprint", endpoint="fitness-footprint")
# @ns_pm.doc(
#     description=(
#         "Fitness analysis based on footprint.\n"
#         "File 1: Upload an event log in .csv or in .xes format.\n"
#         "File 2: Upload a Petri net in .pnml format.\n"
#     )
# )
# class AnalysisFitnessFootprint(Resource):
#     @ns_pm.response(int(HTTPStatus.CREATED), "Success")
#     @ns_pm.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
#     @ns_pm.expect(analysis_upload_parser)
#     def post(self):
        
#         args = analysis_upload_parser.parse_args()
#         event_log_file: FileStorage = args['event_log'] # FileStorage instance for CSV
#         pnml_file: FileStorage = args['pnml_model'] # FileStorage instance for PNML
        
#         try:
#             event_log_filename = secure_filename(event_log_file.filename)
#             pnml_filename = secure_filename(pnml_file.filename)
            
#             if not allowed_file_extension(event_log_filename):
#                 raise TypeError("Invalid format of event log. Allowed: csv or xes")
            
            
#             event_log = event_log_processer(uploaded_event_log=event_log_file)
            
#             pnml_file_extension = pnml_filename.rsplit('.', 1)[-1].lower()
#             if not pnml_file_extension == 'pnml':
#                 raise TypeError()
            
#             # create a temp file on disk
#             temp_pnml = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
#             temp_pnml_path = temp_pnml.name
#             temp_pnml.close()
            
#             # write the uploaded data into the temp file
#             pnml_file.save(temp_pnml_path)
            
            
#             pn, im, fm = pm4py.read_pnml(file_path=temp_pnml_path)
            
            
#             results = pm4py.fitness_footprints(dataframe=event_log, petri_net=pn, initial_marking=im, final_marking=fm)
            
#             print(results)
            
#             return {"result": results}, HTTPStatus.ACCEPTED
#         except TypeError as e:
#             return {"message": e.args}, HTTPStatus.BAD_REQUEST
        

       
@ns_pm.route("/analysis/precision-token-play", endpoint="precision-token-play")
@ns_pm.doc(
    description=(
        "Precision analysis based on token-play.\n"
        "File 1: Upload an event log in .csv or in .xes format.\n"
        "File 2: Upload a Petri net in .pnml format.\n"
    )
)
class AnalysisPrecisionTokenPlay(Resource):
    @ns_pm.response(int(HTTPStatus.CREATED), "Success")
    @ns_pm.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
    @ns_pm.expect(analysis_upload_parser)
    def post(self):
        
        args = analysis_upload_parser.parse_args()
        event_log_file: FileStorage = args['event_log'] # FileStorage instance for CSV
        pnml_file: FileStorage = args['pnml_model'] # FileStorage instance for PNML
        
        try:
            event_log_filename = secure_filename(event_log_file.filename)
            pnml_filename = secure_filename(pnml_file.filename)
            
            if not allowed_file_extension(event_log_filename):
                raise TypeError("Invalid format of event log. Allowed: csv or xes")
            
            
            event_log = event_log_processer(uploaded_event_log=event_log_file)
            
            pnml_file_extension = pnml_filename.rsplit('.', 1)[-1].lower()
            if not pnml_file_extension == 'pnml':
                raise TypeError()
            
            # create a temp file on disk
            temp_pnml = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
            temp_pnml_path = temp_pnml.name
            temp_pnml.close()
            
            # write the uploaded data into the temp file
            pnml_file.save(temp_pnml_path)
            
            
            
            pn, im, fm = pm4py.read_pnml(file_path=temp_pnml_path)
            
            
            results = pm4py.precision_token_based_replay(log=event_log, 
                                                       petri_net=pn, 
                                                       initial_marking=im, 
                                                       final_marking=fm)
            
            print(results)
            
            return {"result": results}, HTTPStatus.ACCEPTED
        except TypeError as e:
            return {"message": e.args}, HTTPStatus.BAD_REQUEST
        
        
@ns_pm.route("/analysis/precision-alignment", endpoint="precision-alignment")
@ns_pm.doc(
    description=(
        "Precision analysis based on alignment.\n"
        
        "File 1: Upload an event log in .csv or in .xes format.\n"
        "File 2: Upload a Petri net in .pnml format.\n"
        
    )
)
class AnalysisPrecisionAlignment(Resource):
    @ns_pm.response(int(HTTPStatus.CREATED), "Success")
    @ns_pm.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
    @ns_pm.expect(analysis_upload_parser)
    def post(self):
        
        args = analysis_upload_parser.parse_args()
        event_log_file: FileStorage = args['event_log'] # FileStorage instance for CSV
        pnml_file: FileStorage = args['pnml_model'] # FileStorage instance for PNML
        
        try:
            event_log_filename = secure_filename(event_log_file.filename)
            pnml_filename = secure_filename(pnml_file.filename)
            
            if not allowed_file_extension(event_log_filename):
                raise TypeError("Invalid format of event log. Allowed: csv or xes")
            
            
            event_log = event_log_processer(uploaded_event_log=event_log_file)
            
            pnml_file_extension = pnml_filename.rsplit('.', 1)[-1].lower()
            if not pnml_file_extension == 'pnml':
                raise TypeError()
            
            # create a temp file on disk
            temp_pnml = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
            temp_pnml_path = temp_pnml.name
            temp_pnml.close()
            
            # write the uploaded data into the temp file
            pnml_file.save(temp_pnml_path)
            
            
            pn, im, fm = pm4py.read_pnml(file_path=temp_pnml_path)
            
            
            results = pm4py.precision_alignments(log=event_log,
                                                petri_net=pn,
                                                initial_marking=im,
                                                final_marking=fm)
            
            
            return {"result": results}, HTTPStatus.ACCEPTED
        except TypeError as e:
            return {"message": e.args}, HTTPStatus.BAD_REQUEST
        


# @ns_pm.route("/analysis/precision-footprint", endpoint="precision-footprint")
# @ns_pm.doc(
#     description=(
#         "Precision analysis based on alignment.\n"
        
#         "File 1: Upload an event log in .csv or in .xes format.\n"
#         "File 2: Upload a Petri net in .pnml format.\n"
        
#     )
# )
# class AnalysisPrecisionFootprint(Resource):
#     @ns_pm.response(int(HTTPStatus.CREATED), "Success")
#     @ns_pm.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
#     @ns_pm.expect(analysis_upload_parser)
#     def post(self):
        
#         args = analysis_upload_parser.parse_args()
#         event_log_file: FileStorage = args['event_log'] # FileStorage instance for CSV
#         pnml_file: FileStorage = args['pnml_model'] # FileStorage instance for PNML
        
#         try:
#             event_log_filename = secure_filename(event_log_file.filename)
#             pnml_filename = secure_filename(pnml_file.filename)
            
#             if not allowed_file_extension(event_log_filename):
#                 raise TypeError("Invalid format of event log. Allowed: csv or xes")
            
            
#             event_log = event_log_processer(uploaded_event_log=event_log_file)
            
#             pnml_file_extension = pnml_filename.rsplit('.', 1)[-1].lower()
#             if not pnml_file_extension == 'pnml':
#                 raise TypeError()
            
#             # create a temp file on disk
#             temp_pnml = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
#             temp_pnml_path = temp_pnml.name
#             temp_pnml.close()
            
#             # write the uploaded data into the temp file
#             pnml_file.save(temp_pnml_path)
            
            
#             pn, im, fm = pm4py.read_pnml(file_path=temp_pnml_path)
            
            
#             results = pm4py.precision_footprints(log=event_log, 
#                                                 petri_net=pn, 
#                                                 initial_marking=im, 
#                                                 final_marking=fm)
            
            
#             return {"result": results}, HTTPStatus.ACCEPTED
#         except TypeError as e:
#             return {"message": e.args}, HTTPStatus.BAD_REQUEST


                    
# @ns_pm.route("/get-random-recommendation", endpoint="random")
# class RandomRecommendation(Resource):
#     @ns_pm.response(int(HTTPStatus.CREATED), "Success")
#     @ns_pm.response(int(HTTPStatus.BAD_REQUEST), "Number of recommendation is either negative or exceed the number of existing contents")
#     @ns_pm.expect(random_request_model)
#     @ns_pm.marshal_with(random_response_model)
#     def post(self):
#         request_data = ns_pm.payload
#         num_of_rec = request_data.get("num_of_rec")
        
#         # print(os.environ["BASE_DATASETS_PATH"])
#         json_file_dir = os.path.join(os.getenv('BASE_DATASETS_PATH'), 'mls-tasks-full/json/data.json')
#         print(json_file_dir)
#         with open(json_file_dir) as f:
#             data_arr = json.load(f)

#         len_of_data = len(data_arr)
        
#         try: 
#             if num_of_rec > len_of_data:
#                 raise ValueError("Number of recommendation requested cannot be larger than the number of contents existing.")

#             if num_of_rec < 0:
#                 raise ValueError("Number of recommendation cannot be negativ")
            
#             random_elements = random.sample(data_arr, num_of_rec)
#             print(type(random_elements))
#             ids = []
#             for e in random_elements:
#                 print(e['@id'])
#                 ids.append(e["@id"])
            
#             print(type(ids))
#             response = {"results": ids}
            
#             return response, HTTPStatus.CREATED
        
#         except ValueError as e:
#             return e.args, HTTPStatus.BAD_REQUEST
#         except TypeError as e:
#             return e.args, HTTPStatus.CONFLICT