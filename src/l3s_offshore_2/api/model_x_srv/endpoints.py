# src/l3s_offshore_2/api/model_x_srv/endpoints.py

## Martin Krause

"""
endpoints.py - Provide GET/POST/PUT for the planning scenario

1) GET -> serves Dummy-Respone
2) POST -> creates new plan
3) PUT -> updates plan

We store the data temporarily in CURRENT_PLAN (In-Memory).
"""

from flask import request
from flask_restx import Namespace, Resource
from http import HTTPStatus

from .dto import planning_request, planning_response

ns = Namespace("model_x", description="Offshore Planning API")

# Registrierung der Modelle im Namespace
ns.models[planning_request.name] = planning_request
ns.models[planning_response.name] = planning_response

CURRENT_PLAN = {
    "workforce_management": {},
    "scenario": {},
    "petri_net": {}
}

@ns.route("/planning")
class PlanningResource(Resource):
    """Endpoints to create, retrieve or update the planning scenario."""

    @ns.marshal_with(planning_response)
    def get(self):
        """
        Hole den aktuellen (dummy) Plan.
        """
        return {
            "message": "Fetched current plan",
            "schedule": (
                "Dummy schedule with "
                f"WORKFORCE_MGMT={CURRENT_PLAN['workforce_management']} / "
                f"SCENARIO={CURRENT_PLAN['scenario']} / "
                f"PETRI_NET={CURRENT_PLAN['petri_net']}"
            )
        }, HTTPStatus.OK

    @ns.expect(planning_request)
    @ns.marshal_with(planning_response)
    def post(self):
        """
        Erstelle neuen Plan (Workforce Management + Scenario + Petri Net).

        1) Parameter sortieren & abspeichern
        2) Minimal-Validierung
        3) Weiterhin keine DB (nur In-Memory)
        """
        data = request.json or {}

        # hole Sub-Bereiche
        workforce_data = data.get("workforce_management", {})
        scenario_data = data.get("scenario", {})
        petri_net_data = data.get("petri_net", {})

        # speichere
        CURRENT_PLAN["workforce_management"] = workforce_data
        CURRENT_PLAN["scenario"] = scenario_data
        CURRENT_PLAN["petri_net"] = petri_net_data

        return {
            "message": "New planning scenario created",
            "schedule": "Scheduled result will appear here later"
        }, HTTPStatus.CREATED

    @ns.expect(planning_request)
    @ns.marshal_with(planning_response)
    def put(self):
        """
        Aktualisiert den existierenden Plan (Merge).
        """
        data = request.json or {}

        workforce_data = data.get("workforce_management")
        scenario_data = data.get("scenario")
        petri_net_data = data.get("petri_net")

        if workforce_data:
            CURRENT_PLAN["workforce_management"].update(workforce_data)
        if scenario_data:
            CURRENT_PLAN["scenario"].update(scenario_data)
        if petri_net_data:
            CURRENT_PLAN["petri_net"].update(petri_net_data)

        return {
            "message": "Plan updated",
            "schedule": (
                "Partial merges done. Current data: "
                f"WORKFORCE_MGMT={CURRENT_PLAN['workforce_management']}, "
                f"SCENARIO={CURRENT_PLAN['scenario']}, "
                f"PETRI_NET={CURRENT_PLAN['petri_net']}"
            )
        }, HTTPStatus.OK
