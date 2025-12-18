# src/l3s_offshore_2/api/dto/endpoints.py
# Martin Krause
#
# =============================================================================
# ARCHITECTURAL NOTICE
# =============================================================================
# ACTIVE ENDPOINTS:
#   - GET /planning/defaults  -> Used by Frontend for parameter display
#   - GET /example/*          -> Example data (testing/documentation/benchmarking)
#
# PLACEHOLDER ENDPOINTS (not connected to actual simulation):
#   - POST /planning          -> Returns mock data only
#
# Actual simulation endpoints are in `offshore_plan_srv`:
#   - POST /offshore-plan/calc-opt-install-cycle-single-vessel
#   - POST /offshore-plan/calc-opt-schedule-single-vessel-to-horizon
#
# See: src/l3s_offshore_2/api/API_ARCHITECTURE.md for full documentation.
# =============================================================================

"""
endpoints.py - API Endpoints for the Offshore Planning Service (DTO)

Provides endpoints for:
- GET /planning/defaults: Retrieves default parameters for Frontend display.
- GET /example/*: Example data (testing/documentation/benchmarking purposes).
- POST /planning: PLACEHOLDER - returns mock data, not connected to simulation.

NOTE: For actual simulation, use offshore_plan_srv endpoints.
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
    




# =============================================================================
# EXAMPLE DATA ENDPOINTS
# =============================================================================
#
# PURPOSE:
# These endpoints serve static example data for API documentation, testing,
# and demonstration purposes. They provide sample inputs and outputs that
# illustrate the expected data formats.
#
# SUPERSEDED BY:
# The `/example/scenario` endpoint returns data in the FLAT format which is
# identical to what `offshore_plan_srv` expects. For actual simulation,
# use the production endpoints:
#   - POST /offshore-plan/calc-opt-install-cycle-single-vessel
#   - POST /offshore-plan/calc-opt-schedule-single-vessel-to-horizon
#
# The `/example/schedule` and `/example/operation-mapping` endpoints show
# the OUTPUT format that `offshore_plan_srv` returns after simulation.
#
# DATA SOURCES:
#   /example/scenario   -> examples/scenario.json (flat MATLAB-style params)
#   /example/descriptor -> examples/descriptor_dto.json (method metadata schema)
#   /example/schedule   -> Hardcoded sample simulation output
#   /example/operation-mapping -> Hardcoded operation ID to name mapping
# =============================================================================

@ns.route("/example/scenario")
class ExampleScenarioResource(Resource):
    """
    Returns an example scenario configuration in FLAT format.
    
    This is the same format expected by `offshore_plan_srv` simulation endpoints.
    Use this as a template for constructing simulation requests.
    
    Note: This returns FLAT format (MATLAB-style), NOT the nested format
    that `/planning/defaults` returns. The two formats are incompatible.
    """
    @ns.doc(description="Get an example scenario configuration (flat format, compatible with offshore_plan_srv).")
    @ns.response(HTTPStatus.OK, "Example scenario configuration retrieved successfully.")
    def get(self):
        """
        Get an example scenario configuration.
        
        Returns the contents of examples/scenario.json which contains
        a complete simulation scenario with:
        - Optimization parameters (optim_*)
        - Petri net parameters (pn_*)
        - Scenario definition (scenario_*, operation_*, vessel_*, etc.)
        - Initial state (state_*)
        - Cost parameters (cost_*)
        - Geographic coordinates
        """
        file_path = os.getcwd() + '/examples/scenario.json'
        with open(file_path, 'r') as file:
            example_scenario = json.load(file)
        return example_scenario, HTTPStatus.OK
        

@ns.route("/example/descriptor")
class ExampleDescriptorResource(Resource):
    """
    Returns a method descriptor schema template.
    
    This is a metadata structure for describing simulation methods,
    including model typology, performance characteristics, complexity,
    and viability information. Intended for method registration or
    benchmarking frameworks.
    
    Note: This is a TEMPLATE with empty values. Fill in the fields
    to describe your specific simulation method.
    """
    @ns.doc(description="Get a method descriptor template (metadata schema for simulation methods).")
    @ns.response(HTTPStatus.OK, "Example descriptor configuration retrieved successfully.")
    def get(self):
        """
        Get a method descriptor template.
        
        Returns the contents of examples/descriptor_dto.json which provides
        a schema for describing simulation methods with fields for:
        - modelID: Unique identifier
        - typology: Application context, formalism, structure, features
        - performance: Solution quality, robustness metrics
        - complexity: Hyperparameters, flexibility options
        - viability: Correctness verification, traceability
        """
        file_path = os.getcwd() + '/examples/descriptor_dto.json'
        with open(file_path, 'r') as file:
            example_descriptor = json.load(file)
        return example_descriptor, HTTPStatus.OK
        

@ns.route("/example/schedule")
class ExamplePlanResource(Resource):
    """
    Returns an example simulation output (schedule).
    
    This shows the format of results returned by offshore_plan_srv
    simulation endpoints. Use this to understand the output structure
    before running actual simulations.
    
    Output format:
    - op: Operation IDs per vessel [[vessel1_ops], [vessel2_ops]]
    - start: Start times for each operation
    - end: End times for each operation
    - restock: Port restock event times
    - optim_exitflag: Optimizer exit status (1 = success)
    - computation_time: Time taken for optimization (seconds)
    """
    @ns.doc(description="Get an example simulation output (schedule format from offshore_plan_srv).")
    @ns.response(HTTPStatus.OK, "Example plan configuration retrieved successfully.")
    def get(self):
        """
        Get an example schedule output.
        
        Returns a hardcoded sample that demonstrates the output format
        of the offshore_plan_srv simulation endpoints.
        """
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
    """
    Returns the operation ID to name mapping.
    
    Maps human-readable operation names to the numeric IDs used in
    schedule outputs. Required to interpret the 'op' arrays from
    simulation results.
    
    Mapping:
    - 0: install (OWT installation at site)
    - 1: sailing_back (return voyage to port)
    - 2: sailing_forth (voyage to installation site)  
    - 3: loading_owt (loading components at port)
    """
    @ns.doc(description="Get the operation ID mapping (numeric ID to operation name).")
    @ns.response(HTTPStatus.OK, "Example operation mapping configuration retrieved successfully.")
    def get(self):
        """
        Get operation ID to name mapping.
        
        Returns a dictionary mapping operation names to their numeric IDs
        as used in simulation schedule outputs.
        """
        example_operation_mapping = {
            "loading_owt": 3,
            "sailing_forth": 2,
            "sailing_back": 1,
            "install" : 0,   
        }
        return example_operation_mapping, HTTPStatus.OK