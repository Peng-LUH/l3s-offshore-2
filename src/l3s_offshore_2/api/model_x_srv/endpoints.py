# src/l3s_offshore_2/api/model_x_srv/endpoints.py
# Martin Krause
"""
endpoints.py - API Endpoints for the Offshore Planning Service (Model X)

Provides endpoints for:
- POST /planning: Creates a new planning simulation job.
- PUT /planning: Updates parameters of the current conceptual plan (in-memory).
- GET /planning/defaults: Retrieves default parameters for a planning request.
- GET /planning: (Primarily for debugging) Retrieves the current in-memory plan state.

Uses the revised DTOs and calls placeholder logic functions.
"""

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

ns = Namespace("model_x", description="Offshore Wind Farm Installation Planning API", validate=True)

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


# In-memory storage for the *last submitted* planning request configuration.
# This is primarily for demonstration/debugging as per original implementation.

CURRENT_PLAN_CONFIG = {
    "scenario_definition": {},
    "simulation_config": {},
    "workforce_management": {}
}

@ns.route("/planning")
class PlanningResource(Resource):
    """Create or Update a Planning Scenario Simulation Job."""

    @ns.doc(description="Retrieve the configuration of the last submitted planning request (for debugging).")
    @ns.marshal_with(planning_request) # Use the request DTO to show the stored config structure
    def get(self):
        """
        Retrieve the configuration of the last submitted plan (In-Memory).
        """
        print("GET /planning called, returning CURRENT_PLAN_CONFIG")
        # This returns the *input* configuration, not the results.
        return CURRENT_PLAN_CONFIG, HTTPStatus.OK

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

        # Store the submitted configuration (overwrites previous)
        CURRENT_PLAN_CONFIG["scenario_definition"] = data.get("scenario_definition", {})
        CURRENT_PLAN_CONFIG["simulation_config"] = data.get("simulation_config", {})
        CURRENT_PLAN_CONFIG["workforce_management"] = data.get("workforce_management", {})

        # --- Call the business logic ---
        status_code, response_data = logic.process_planning_request(data)
        # --- End Logic Call ---

        return response_data, status_code

    @ns.doc(description="Update the current in-memory plan configuration by merging the provided data.")
    @ns.expect(planning_request, validate=True) # Expect the full model, but only parts might be provided
    @ns.response(HTTPStatus.OK, "In-memory plan configuration updated successfully (placeholder response).", planning_response)
    @ns.response(HTTPStatus.BAD_REQUEST, "Input validation failed.")
    @ns.marshal_with(planning_response)
    def put(self):
        """
        Update the current in-memory plan configuration (Merge).
        Note: This updates the stored *configuration*, the effect on a running/past simulation
        is handled by the (placeholder) logic.
        """
        data = request.json
        print("PUT /planning received data for update.")

        # Merge provided data into the current configuration
        # Use .get() to avoid errors if a section is missing in the input
        if data.get("scenario_definition"):
            CURRENT_PLAN_CONFIG["scenario_definition"].update(data["scenario_definition"])
        if data.get("simulation_config"):
            CURRENT_PLAN_CONFIG["simulation_config"].update(data["simulation_config"])
        if data.get("workforce_management"):
            # Ensure the target exists before updating
            if "workforce_management" not in CURRENT_PLAN_CONFIG:
                 CURRENT_PLAN_CONFIG["workforce_management"] = {}
            CURRENT_PLAN_CONFIG["workforce_management"].update(data["workforce_management"])

        print("Current config after PUT merge:", CURRENT_PLAN_CONFIG)

        # --- Call the business logic for update (placeholder) ---
        status_code, response_data = logic.update_planning_request(data)
        # --- End Logic Call ---

        # Add the current (merged) config to the response message for clarity? Or keep it clean?
        # response_data["message"] += f" Current Config: {CURRENT_PLAN_CONFIG}" # Optional debugging info

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