# src/l3s_offshore_2/api/model_x_srv/dto.py
"""
dto.py - Data Transfer Objects for Workforce Management, Scenario & Petri Net parameters

We sort the parameters into three main models:  
- WorkforceManagementDTO  
- ScenarioDTO  
- PetriNetDTO  

Additionally, there is a PlanningRequest that combines all three models,  
and a PlanningResponse in which we can, for example, transmit a "schedule" or result status.
"""

from flask_restx import Model, fields

###################################
# Workforce Management (WFM) DTO
###################################
workforce_management_dto = Model("WorkforceManagement", {
    "perform_workforce_management": fields.Boolean(
        default=True,
        description="Toggle workforce management on/off"
    ),
    "epsilon": fields.Integer(
        default=10,
        description="Weight factor to suppress frequent changing of assigned persons"
    ),
    "max_hours_per_day": fields.List(
        fields.Float,
        default=[14, 12, 10],
        description="Max hours per day for each crew/ruleset"
    ),
    "max_hours_per_week": fields.List(
        fields.Float,
        default=[72, 48, 40],
        description="Max hours per week for each crew/ruleset"
    ),
    "min_pause_block": fields.List(
        fields.Float,
        default=[6, 11, 11],
        description="Minimum rest block between shifts"
    ),
    "min_small_pause": fields.List(
        fields.Float,
        default=[1, 1, 1],
        description="Short break time for each ruleset"
    ),
    "min_small_pause_per_hours": fields.List(
        fields.Float,
        default=[10, 10, 8],
        description="After how many hours a short break is needed"
    ),
    "skills": fields.List(
        fields.String,
        default=["Install", "Vessel", "Port", "Agency"],
        description="List of skill identifiers"
    ),
    "job_type_skills": fields.List(
        fields.List(fields.Integer),
        default=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
        description="Job-skill mapping"
    ),
    "person_type_skills": fields.List(
        fields.List(fields.Integer),
        default=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
        description="Person-skill mapping"
    ),
    "persons": fields.List(
        fields.String,
        default=["Install", "Install", "Install", "Vessel", "Vessel", "Port", "Port", "Port", "Agency"],
        description="All persons or roles in scenario"
    ),
    "cost_per_person": fields.List(
        fields.Float,
        default=[100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 999999.0, 999999.0],
        description="Cost per person"
    ),
    "person_location": fields.List(
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
# Scenario DTO
###################################
scenario_dto = Model("Scenario", {
    "operation_names": fields.List(
        fields.String,
        default=["Install Tower", "Install Nacelle", "Install Blade 1", "Move", "Reposition"],
        description="High-level names of operations"
    ),
    "operation_durations": fields.List(
        fields.Float,
        default=[3, 3, 2, 4, 1],
        description="Duration for each operation"
    ),
    "operation_wind": fields.List(
        fields.Float,
        default=[12.0, 12.0, 10.0, 21.0, 14.0],
        description="Wind threshold for each operation"
    ),
    "operation_wave": fields.List(
        fields.Float,
        default=[99.0, 99.0, 99.0, 2.5, 2.0],
        description="Wave threshold for each operation"
    ),
    "process_chain_install": fields.List(
        fields.Integer,
        default=[1, 2, 3],
        description="Indices referencing operation_names for an 'install' chain"
    ),
    "process_chain_move": fields.List(
        fields.Integer,
        default=[4],
        description="Indices referencing operation_names for a 'move' chain"
    ),
    "process_chain_load": fields.List(
        fields.Integer,
        default=[],
        description="Indices referencing operation_names for a 'load' chain"
    ),
    "owts_to_build": fields.Integer(
        default=32,
        description="Number of OWT (Offshore Wind Turbine) units to build"
    ),
    "vessel_num_installation_vessels": fields.Integer(
        default=2,
        description="Number of installation vessels"
    ),
    "vessel_capacity": fields.Integer(
        default=4,
        description="Capacity of each vessel"
    )
})

###################################
# Petri Net (PN) DTO
###################################
petri_net_dto = Model("PetriNet", {
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
    "initial_storage": fields.Integer(
        default=32,
        description="Initial storage capacity at the base port"
    ),
    "max_storage": fields.Integer(
        default=40,
        description="Maximum possible storage at the base port"
    ),
    "min_storage": fields.Float(
        default=0.4,
        description="Minimum storage threshold"
    ),
    "number_of_agents": fields.Integer(
        default=2,
        description="Number of installation vessels (agents)"
    ),
    "installation_vessel_capacity": fields.Integer(
        default=4,
        description="Capacity of each installation vessel"
    ),
    "operation_durations": fields.List(
        fields.Float,
        default=[12, 4, 2, 14, 2],
        description="Durations for [Load, Move, JackUp, Install, Reposition] etc."
    ),
    "weather_limits": fields.List(
        fields.List(fields.Float),
        default=[[99, 99], [21, 2.5], [14, 1.8], [10.2, 99], [14, 2]],
        description="Weather (wind, wave) constraints per operation step"
    ),
    "fair_mode": fields.Integer(
        default=1,
        description="(0=no fair, 1=absolute fair, 2=cycle-based, 3=relaxed fair)"
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
    "wind_data_file": fields.String(
        default="wind.csv",
        description="CSV file path for wind data"
    ),
    "wave_data_file": fields.String(
        default="wave.csv",
        description="CSV file path for wave data"
    ),
})

###################################
# Kombinierte Anfrage & Antwort
###################################
planning_request = Model("PlanningRequest", {
    "workforce_management": fields.Nested(
        workforce_management_dto,
        description="All parameters relevant to Workforce Management"
    ),
    "scenario": fields.Nested(
        scenario_dto,
        description="All parameters relevant to the scenario definition"
    ),
    "petri_net": fields.Nested(
        petri_net_dto,
        description="All parameters relevant to the Petri-Net-based simulation"
    )
})

planning_response = Model("PlanningResponse", {
    "message": fields.String(description="Status/info message"),
    "schedule": fields.String(description="Placeholder for now")
})
