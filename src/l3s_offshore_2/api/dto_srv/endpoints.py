# src/l3s_offshore_2/api/dto/endpoints.py
# Martin Krause
"""
endpoints.py - API Endpoints for the Offshore Planning Service (DTO)

Provides endpoints for:
- POST /planning: Creates a new planning simulation job.
- GET /planning/defaults: Retrieves default parameters for a planning request.


Uses the revised DTOs and calls placeholder logic functions.
"""
import json, os, pathlib
from flask import request
from flask_restx import Namespace, Resource
from http import HTTPStatus

# Import the revised DTOs
from .dto import (
    planning_request, planning_response, scenario_definition_dto,
    simulation_config_dto, workforce_management_config_dto,
    # Import base DTOs if needed elsewhere, or rely on nesting
    weather_limits_dto, location_dto, skill_definition_dto,
    work_ruleset_definition_dto, personnel_definition_dto,
    wfm_optimization_params_dto, operation_definition_dto, port_config_dto,
    vessel_config_dto, weather_data_source_dto, log_wind_profile_config_dto,
    dtmc_config_dto, scheduling_strategy_params_dto, pruning_config_dto,
    search_config_dto, gantt_entry_dto, kpi_set_dto, planning_result_dto
)
# Import the placeholder logic module
from . import logic

ns = Namespace("Data Transfer Objects", validate=True)

# --- Register ALL defined models with the namespace for Swagger ---
# Top Level Request/Response
ns.models[planning_request.name] = planning_request
ns.models[planning_response.name] = planning_response
# Main Configuration Blocks
ns.models[scenario_definition_dto.name] = scenario_definition_dto
ns.models[simulation_config_dto.name] = simulation_config_dto
ns.models[workforce_management_config_dto.name] = workforce_management_config_dto
# Nested DTOs within Scenario Definition
ns.models[port_config_dto.name] = port_config_dto
ns.models[vessel_config_dto.name] = vessel_config_dto
ns.models[operation_definition_dto.name] = operation_definition_dto
# Nested DTOs within Simulation Config
ns.models[weather_data_source_dto.name] = weather_data_source_dto
ns.models[log_wind_profile_config_dto.name] = log_wind_profile_config_dto
ns.models[dtmc_config_dto.name] = dtmc_config_dto
ns.models[scheduling_strategy_params_dto.name] = scheduling_strategy_params_dto
ns.models[pruning_config_dto.name] = pruning_config_dto
ns.models[search_config_dto.name] = search_config_dto
# Nested DTOs within WFM Config
ns.models[skill_definition_dto.name] = skill_definition_dto
ns.models[work_ruleset_definition_dto.name] = work_ruleset_definition_dto
ns.models[personnel_definition_dto.name] = personnel_definition_dto
ns.models[wfm_optimization_params_dto.name] = wfm_optimization_params_dto
# Nested DTOs within Results
ns.models[planning_result_dto.name] = planning_result_dto
ns.models[gantt_entry_dto.name] = gantt_entry_dto
ns.models[kpi_set_dto.name] = kpi_set_dto
# Base/Reusable DTOs (if not already covered by nesting)
ns.models[weather_limits_dto.name] = weather_limits_dto
ns.models[location_dto.name] = location_dto
# --- End Model Registration ---

@ns.route("/planning")
class PlanningResource(Resource):
    """Create a Planning Scenario Simulation Job."""

    @ns.doc(description="Submit a new planning request to run a simulation.")
    @ns.expect(planning_request, validate=True)
    @ns.response(HTTPStatus.CREATED, "Planning job successfully created (placeholder response).", planning_response)
    @ns.response(HTTPStatus.BAD_REQUEST, "Input validation failed.")
    @ns.response(HTTPStatus.INTERNAL_SERVER_ERROR, "Simulation execution failed.")
    @ns.marshal_with(planning_response) # Use the standard response DTO
    def post(self):
        """
        Create and execute a new planning simulation based on the provided configuration.
        """
        data = request.json
        print("POST /planning received data.")

        # --- Call the business logic ---
        status_code, response_data = logic.process_planning_request(data)
        # --- End Logic Call ---

        return response_data, status_code


@ns.route("/planning/defaults")
class PlanningDefaultsResource(Resource):
    """Provides default parameters for a planning request."""

    @ns.doc(description="Get a default structure and values for a planning request payload.")
    @ns.response(HTTPStatus.OK, "Default planning parameters retrieved successfully.", planning_request) # Marshal with request DTO
    @ns.marshal_with(planning_request) # Use the request DTO as the response structure for defaults
    def get(self):
        """
        Get default planning parameters.
        """
        print("GET /planning/defaults called.")
        defaults = logic.get_default_planning_parameters()
        return defaults, HTTPStatus.OK
    




##################################################
# Example data structure for valuetools2025
##################################################

@ns.route("/example/scenario")
class ExampleScenarioResource(Resource):
    """Provides an example scenario configuration for testing and demonstration."""
    @ns.doc(description="Get an example scenario configuration.")
    @ns.response(HTTPStatus.OK, "Example scenario configuration retrieved successfully.")
    def get(self):
        """
        Get an example scenario configuration.
        """
        file_path = os.getcwd() + '/examples/scenario.json'
        with open(file_path, 'r') as file:
            example_scenario = json.load(file)
        return example_scenario, HTTPStatus.OK
        

@ns.route("/example/descriptor")
class ExampleDescriptorResource(Resource):
    """Provides an example descriptor configuration for testing and demonstration."""

    @ns.doc(description="Get an example descriptor for method registration.")
    @ns.response(HTTPStatus.OK, "Example descriptor configuration retrieved successfully.")
    def get(self):
        """
        Get an example descriptor configuration.
        """
        file_path = os.getcwd() + '/examples/descriptor_dto.json'
        with open(file_path, 'r') as file:
            example_descriptor = json.load(file)
        return example_descriptor, HTTPStatus.OK
        

@ns.route("/example/schedule")
class ExamplePlanResource(Resource):
    """Provides an example plan configuration for testing and demonstration."""

    @ns.doc(description="Get an example plan for the OWF installation.")
    @ns.response(HTTPStatus.OK, "Example plan configuration retrieved successfully.")
    def get(self):
        """
        Get an example plan configuration.
        """
        # print("GET /example/plan called.")
        example_plan = {
            'op': [[0,0,0,1,3,3,3,3,2]],
            'start': [[0,19,38,57,61,73,85,97,109]],
            'end': [[18,37,56,60,72,84,96,108,112]],
            'restrock': [8, 320],
            'optim_exitflag': 1,
            'computation_time': 584.9417314529419
        }
        return example_plan, HTTPStatus.OK
        

@ns.route("/example/operation-mapping")
class ExampleOperationMappingResource(Resource):
    """Provides an example operation mapping configuration for testing and demonstration."""

    @ns.doc(description="Get an example operation mapping.")
    @ns.response(HTTPStatus.OK, "Example operation mapping configuration retrieved successfully.")
    def get(self):
        """
        Get an example operation mapping configuration.
        """
        # print("GET /example/operation-mapping called.")
        example_operation_mapping = {
            "loading_owt": 3,
            "sailing_forth": 2,
            "sailing_back": 1,
            "install" : 0,   
        }
        return example_operation_mapping, HTTPStatus.OK