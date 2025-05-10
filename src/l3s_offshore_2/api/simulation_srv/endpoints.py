from http import HTTPStatus
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

import pm4py
import tempfile
# import flask
from flask import request, url_for

# import flask-restx
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser

# from l3s_offshore_2.api.test import ns_sim
from l3s_offshore_2.petri_net_sim.simplepn import SimplePN, SimpleSimulator

## import dto
from .dto import test_model

ns_sim = Namespace("Simulation", validate=True)

## dto registration
ns_sim.models[test_model.name] = test_model

sim_upload_parser = ns_sim.parser()
sim_upload_parser.add_argument(
    'pnml_model', location='files', type=FileStorage, required=True,
    help='PNML Petri net file'
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
    @ns_sim.expect(sim_upload_parser)
    def post(self):
        try:
            args = sim_upload_parser.parse_args()
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
            
            
            pn, im, fm = pm4py.read_pnml(file_path=temp_pnml_path)
            
            simple_pn = SimplePN.convert_to_simple_pn(pn=pn, initial_marking=im)
            
            sim = SimpleSimulator(net=simple_pn, initial_marking=im)
            
            sim.run()
            
            return {"results": sim.get_firing_sequence()}, HTTPStatus.CREATED
            
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