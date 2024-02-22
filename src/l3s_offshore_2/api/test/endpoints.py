from http import HTTPStatus

# import flask
from flask import request, url_for

# import flask-restx
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser

# from l3s_offshore_2.api.test import ns_test

## import dto
from .dto import test_model

ns_test = Namespace("test", validate=True)

## dto registration
ns_test.models[test_model.name] = test_model

@ns_test.route("/test-get", endpoint="test-get")
class RecsysTest(Resource):
    @ns_test.marshal_with(test_model)
    def get(self):
        return {"message": "success"}, HTTPStatus.OK
    
@ns_test.route("/test-post", endpoint="test-post")
class RecsysTest(Resource):
    @ns_test.expect(test_model)
    @ns_test.marshal_with(test_model)
    def post(self):
        msg = ns_test.payload
        return msg, HTTPStatus.CREATED