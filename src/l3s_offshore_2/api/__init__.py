# src/l3s_offshore_2/api/__init__.py
"""API blueprint configuration"""
from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint("api", __name__, url_prefix="/l3s-offshore-2")
# authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}


api = Api(api_bp,
          version="0.0.1", # Consider updating version
          title="L3S Offshore 2 Planning API", # Updated Title
          description="API for simulating and scheduling offshore wind farm installations.", # Updated Description
        #   doc="/ui", # Default is root, /ui is fine too
        #   authorizations=authorizations,
          )


# Remove or keep test/random namespaces as needed
# from l3s_offshore_2.api.test.endpoints import ns_test
# api.add_namespace(ns_test, path="/test")
# from l3s_offshore_2.api.random.endpoints import ns_random
# api.add_namespace(ns_random, path="/random")


# Register the planning namespace
from l3s_offshore_2.api.model_x_srv.endpoints import ns as model_x_ns
from l3s_offshore_2.api.simulation_srv.endpoints import ns_sim
from l3s_offshore_2.api.process_mining_srv.endpoints import ns_pm
from l3s_offshore_2.api.simulation_petri_nets import simulation_petri_nets_ns
api.add_namespace(model_x_ns, path="/model-x") # Path prefix for this specific service
api.add_namespace(ns_sim, path="/simulation-petri-nets")
api.add_namespace(ns_pm, path="/process-mining")
api.add_namespace(simulation_petri_nets_ns, path="/simulation-petri-nets")