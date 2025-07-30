from http import HTTPStatus
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import json
from pprint import pprint
import pm4py
import tempfile
# import flask
from flask import request, url_for, send_file, abort, Response, jsonify
import os
import numpy as np

# import flask-restx
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser

# import logic
from .logic import (
    get_expected_operation_duration,
    get_operation_prabability
)


## define Namespace
ns_offshore_plan = Namespace("Offshore Plan", validate=True)

## import dto
from .dto import operation_duration_requirements

## register dto to Namespace
ns_offshore_plan.models[operation_duration_requirements.name] = operation_duration_requirements

@ns_offshore_plan.route('/get-weather-data')
class GetWeatherData(Resource):
    def get(self):
        """Load historical weather data."""
        
        
        return {"response": 200, "results": "okay"}, 200


@ns_offshore_plan.route('/get-operation-duration')
@ns_offshore_plan.expect(operation_duration_requirements)
class GetOperationDuration(Resource):
    def post(self):
        data = request.json
        operation_duration = data["operation_duration"]
        wind_limit = data["wind_limit"]
        wave_limit = data["wave_limit"]
        
        # expected_operation_duration = get_expected_operation_duration(job_duration=operation_duration,
        #                                                               job_requirement=[[wind_limit, wave_limit]])
        operation_prob = get_operation_prabability(job_requirements=[wind_limit, wave_limit])
        return {"results": operation_prob}
        
