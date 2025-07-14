from http import HTTPStatus
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import json
from pprint import pprint
import pm4py
import tempfile
# import flask
from flask import request, url_for

# import flask-restx
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser

from .logic import simple_sim_run
from .logic import timed_sim_run


## import dto
from .dto import test_model

ns_sim = Namespace("Simulation", validate=True)

## dto registration
ns_sim.models[test_model.name] = test_model

pnml_upload_parser = ns_sim.parser()
pnml_upload_parser.add_argument(
    'pnml_model', location='files', type=FileStorage, required=True,
    help='PNML Petri net file'
)

pndf_upload_parser = ns_sim.parser()
pndf_upload_parser.add_argument(
    'pndf_model', location='files', type=FileStorage, required=True,
    help='Petri Net Definition File in Json format'
)


@ns_sim.route("/simple-sim", endpoint="simple-sim")
@ns_sim.doc(
    description=(
        "Simulation of Convential Petri Nets.\n"
        "File: Upload a Petri net in .pnml format.\n"
    )
)
class SimpleSimulation(Resource):
    @ns_sim.response(int(HTTPStatus.CREATED), "Success")
    @ns_sim.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
    @ns_sim.expect(pnml_upload_parser)
    def post(self):
        try:
            args = pnml_upload_parser.parse_args()
            pnml_file: FileStorage = args['pnml_model'] # FileStorage instance for PNML
            pnml_filename = secure_filename(pnml_file.filename)
            pnml_file_extension = pnml_filename.rsplit('.', 1)[-1].lower()
            if not pnml_file_extension == 'pnml':
                raise TypeError("Not a pnml file.")
            
            # create a temp file on disk
            temp_pnml = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
            temp_pnml_path = temp_pnml.name
            temp_pnml.close()
            # write the uploaded data into the temp file
            pnml_file.save(temp_pnml_path)
            
            sim_results = simple_sim_run(pnml_path=temp_pnml_path)
            
            
            return {"results": sim_results}, HTTPStatus.CREATED
            
        except TypeError as e:
            return {"message": e.args}, HTTPStatus.BAD_REQUEST

# @ns_sim.route("/test-get", endpoint="test-get")
# class RecsysTest(Resource):
#     @ns_sim.marshal_with(test_model)
#     def get(self):
#         return {"message": "success"}, HTTPStatus.OK
    
# @ns_sim.route("/test-post", endpoint="test-post")
# class RecsysTest(Resource):
#     @ns_sim.expect(test_model)
#     @ns_sim.marshal_with(test_model)
#     def post(self):
#         msg = ns_sim.payload
#         return msg, HTTPStatus.CREATED


@ns_sim.route("/timed-sim/pnml", endpoint="timed-sim-pnml")
@ns_sim.doc(
    description=(
        "Simulation of Timed Petri Nets.\n"
        "File: Upload a Petri net in .pnml format.\n"
    )
)

class TimedSimulationPNML(Resource):
    @ns_sim.response(int(HTTPStatus.CREATED), "Success")
    @ns_sim.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
    @ns_sim.expect(pnml_upload_parser)
    def post(self):
        try:
            args = pnml_upload_parser.parse_args()
            pnml_file: FileStorage = args['pnml_model'] # FileStorage instance for PNML
            pnml_filename = secure_filename(pnml_file.filename)
            pnml_file_extension = pnml_filename.rsplit('.', 1)[-1].lower()
            if not pnml_file_extension == 'pnml':
                raise TypeError("Not a pnml file.")
            
            # create a temp file on disk
            temp_pnml = tempfile.NamedTemporaryFile(delete=False, suffix='.pnml')
            temp_pnml_path = temp_pnml.name
            temp_pnml.close()
            # write the uploaded data into the temp file
            pnml_file.save(temp_pnml_path)
            
            sim_results = timed_sim_run(pnml_path=temp_pnml_path)
            
            
            
            return {"results": sim_results}, HTTPStatus.CREATED
            
        except TypeError as e:
            return {"message": e.args}, HTTPStatus.BAD_REQUEST
        



@ns_sim.route("/timed-sim/pndf", endpoint="timed-sim-pndf")
@ns_sim.doc(
    description=(
        "Simulation of Timed Petri Nets.\n"
        "File: Upload a Petri net in .json format.\n"
    )
)
class TimedSimulationPNDF(Resource):
    @ns_sim.response(int(HTTPStatus.CREATED), "Success")
    @ns_sim.response(int(HTTPStatus.BAD_REQUEST), "Type Error")
    @ns_sim.expect(pndf_upload_parser)
    def post(self):
        try:
            args = pndf_upload_parser.parse_args()
            pndf_file: FileStorage = args['pndf_model'] # FileStorage instance for pndf
            pndf_filename = secure_filename(pndf_file.filename)
            pndf_file_extension = pndf_filename.rsplit('.', 1)[-1].lower()
            if not pndf_file_extension == 'json':
                raise TypeError("Not a json file.")
            
            # create a temp file on disk
            temp_pndf = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
            temp_pndf_path = temp_pndf.name
            temp_pndf.close()
            # write the uploaded data into the temp file
            pndf_file.save(temp_pndf_path)
            # with open(temp_pndf_path, 'r') as f:
            #     pndf = json.load(f)
            
            # pprint(pndf)
            sim_results = timed_sim_run(model_path=temp_pndf_path)
            
            return {"results": sim_results}, HTTPStatus.CREATED
            
        except TypeError as e:
            return {"message": e.args}, HTTPStatus.BAD_REQUEST