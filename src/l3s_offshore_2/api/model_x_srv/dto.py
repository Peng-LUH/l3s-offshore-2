# src/l3s_offshore_2/api/model_x_srv/dto.py

"""
dto.py - Data Transfer Objects for WFM & Petri Net parameters

Wir sortieren die Parameter in zwei große Hauptmodelle:
- WorkforceManagementDTO
- PetriNetDTO

Zusätzlich gibt es ein PlanningRequest, das beide Modelle kombiniert,
und ein PlanningResponse, in dem wir z.B. ein "schedule" oder
Ergebnis-Status transportieren können.
"""

from flask_restx import Model, fields

###################################
# Workforce Management (WFM) DTO
###################################
wfm_dto = Model("WorkforceManagement", {
    "performWFM": fields.Boolean(
        default=True,
        description="Toggle workforce management on/off"
    ),
    "epsilon": fields.Integer(
        default=10,
        description="Weight factor to suppress changing of persons"
    ),
    "maxHoursPerDay": fields.List(
        fields.Float,
        default=[14, 12, 10],
        description="Max hours per day for each crew/ruleset"
    ),
    "maxHoursPerWeek": fields.List(
        fields.Float,
        default=[72, 48, 40],
        description="Max hours per week for each crew/ruleset"
    ),
    "minPauseBlock": fields.List(
        fields.Float,
        default=[6, 11, 11],
        description="Min rest block between shifts"
    ),
    "minSmallPause": fields.List(
        fields.Float,
        default=[1, 1, 1],
        description="Small break time for each ruleset"
    ),
    "minSmallPausePerHours": fields.List(
        fields.Float,
        default=[10, 10, 8],
        description="After how many hours a small break is needed"
    ),
    "skills": fields.List(
        fields.String,
        default=["Install", "Vessel", "Port", "Agency"],
        description="List of skill identifiers"
    ),
    "jobTypeSkills": fields.List(
        fields.List(fields.Integer),
        default=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
        description="Job-skill mapping"
    ),
    "personTypeSkills": fields.List(
        fields.List(fields.Integer),
        default=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
        description="Person-skill mapping"
    ),
    "persons": fields.List(
        fields.String,
        default=["Install", "Install", "Install", "Vessel", "Vessel", "Port", "Port", "Port", "Agency"],
        description="All persons or roles in scenario"
    ),
    "costPerson": fields.List(
        fields.Float,
        default=[100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 999999.0, 999999.0],
        description="Cost per person"
    ),
    "location": fields.List(
        fields.Integer,
        default=[1, 1, 1, 1, 1, 0, 0, 0, 0],
        description="Location (vessel=1..N, port=0) for each person"
    ),
    "ruleset": fields.List(
        fields.Integer,
        default=[2, 2, 2, 1, 1, 3, 3, 3, 4],
        description="Ruleset index for each person"
    )
})

###################################
# Petri Net (PN) DTO
###################################
pn_dto = Model("PetriNet", {
    "start_date": fields.String(
        required=True,
        example="2025-03-17",
        description="Simulation start date"
    ),
    "end_date": fields.String(
        required=True,
        example="2025-03-27",
        description="Simulation end date"
    ),
    "delta_time": fields.Integer(
        default=1,
        description="Time increment per simulation step"
    ),
    "max_loop": fields.Integer(
        default=15,
        description="Max PN iteration loops"
    ),
    "print_loop_number": fields.Boolean(
        default=False,
        description="Whether to log loop numbers"
    ),
    "owf_size": fields.Integer(
        default=40,
        description="Offshore wind farm size (number of turbines)"
    ),
    "ini_storage": fields.Integer(
        default=32,
        description="Initial storage capacity"
    ),
    "storage_max": fields.Integer(
        default=40,
        description="Maximum storage"
    ),
    "sotrage_min": fields.Float(
        default=0.4,
        description="Minimum storage threshold"
    ),
    "num_agent": fields.Integer(
        default=2,
        description="Number of installation vessels"
    ),
    "capacity_iv": fields.Integer(
        default=4,
        description="Capacity of each installation vessel"
    ),
    "operation_duration": fields.List(
        fields.Float,
        default=[12, 4, 2, 14, 2],
        description="Durations for operations [Load, Move, JackUp, Install, Reposition] etc."
    ),
    "lim_weather": fields.List(
        fields.List(fields.Float),
        default=[[99, 99], [21, 2.5], [14, 1.8], [10.2, 99], [14, 2]],
        description="Weather (wind, wave) constraints per operation step"
    ),
    "fair_mode": fields.Integer(
        default=1,
        description="0=no fair,1=abs fair,2=cycle-based,3=relaxed"
    ),
    "pruning_flag": fields.Integer(
        default=2,
        description="How aggressively to prune the state-space"
    ),
    "tau": fields.Float(
        default=0.01,
        description="Tolerance param for pruning"
    ),
    "search_space": fields.Integer(
        default=0,
        description="Possible BFS/DFS or search limit"
    ),
    "windDataFile": fields.String(
        default="wind.csv",
        description="CSV with wind data"
    ),
    "waveDataFile": fields.String(
        default="wave.csv",
        description="CSV with wave data"
    ),
})

###################################
# Kombinierte Anfrage & Antwort
###################################
planning_request = Model("PlanningRequest", {
    "wfm": fields.Nested(wfm_dto, description="Workforce Management parameters"),
    "pn": fields.Nested(pn_dto, description="Petri Net parameters")
})

planning_response = Model("PlanningResponse", {
    "message": fields.String(description="Status/info message"),
    "schedule": fields.String(description="Just a placeholder for now")
})
