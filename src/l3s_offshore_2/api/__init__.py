"""API blueprint configuration"""
from flask import Blueprint
from flask_restx import Api



api_bp = Blueprint("api", __name__, url_prefix="/l3s-offshore-2")
# authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}


api = Api(api_bp,
          version="0.0.0",
          title="L3S Offshore 2",
          description="Welcome to the Swagger UI documentation site for OffshorePlan2!",
        #   doc="/ui",
        #   authorizations=authorizations,
          )


from l3s_offshore_2.api.test.endpoints import ns_test
api.add_namespace(ns_test, path="/test")

# from l3s_offshore_2.api.random.endpoints import ns_random
# api.add_namespace(ns_random, path="/random")

