# src/l3s_offshore_2/api/model_x_srv/endpoints.py
"""
endpoints.py - Provide GET/POST/PUT for the planning scenario

1) GET -> liefert Dummy-Antwort
2) POST -> legt neuen Plan an
3) PUT -> aktualisiert Plan

Wir halten die Daten in CURRENT_PLAN (In-Memory).
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
    "wfm": {},
    "pn": {}
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
            "schedule": f"Dummy schedule with WFM={CURRENT_PLAN['wfm']} + PN={CURRENT_PLAN['pn']}"
        }, HTTPStatus.OK

    @ns.expect(planning_request)
    @ns.marshal_with(planning_response)
    def post(self):
        """
        Erstelle neuen Plan (WFM + PN).

        1) Parameter sortieren & abspeichern
        2) Minimal-Validierung
        3) Noch keine DB-Anbindung
        """
        data = request.json or {}
        wfm_data = data.get("wfm", {})
        pn_data = data.get("pn", {})

        CURRENT_PLAN["wfm"] = wfm_data
        CURRENT_PLAN["pn"] = pn_data

        # Hier könnte z. B. die PN-Logik oder WFM-Logik angebunden werden
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
        wfm_data = data.get("wfm")
        pn_data = data.get("pn")

        if wfm_data:
            CURRENT_PLAN["wfm"].update(wfm_data)
        if pn_data:
            CURRENT_PLAN["pn"].update(pn_data)

        return {
            "message": "Plan updated",
            "schedule": f"New partial merges done"
        }, HTTPStatus.OK
