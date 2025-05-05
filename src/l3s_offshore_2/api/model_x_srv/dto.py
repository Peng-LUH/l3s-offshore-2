# src/l3s_offshore_2/api/model_x_srv/dto.py
# Martin Krause

"""
dto.py - Data Transfer Objects for Offshore Wind Farm Installation Planning

REVISED STRUCTURE based on analysis of paper, meetings, and parameter list.
Separates Scenario Definition, Simulation Configuration, and optional Workforce Management.
Focuses on configuring the simulation run, assuming the Petri Net model is provided externally (e.g., PNML).
Uses snake_case and full descriptive names.
Adheres to the ideal mental model derived from requirements.
"""

from flask_restx import Model, fields

# =============================================================================
# Base/Reusable DTOs
# =============================================================================

weather_limits_dto = Model("WeatherLimits", {
    "max_wind_speed_m_s": fields.Float(
        required=True,
        description="Maximum tolerable wind speed for the operation (in m/s).",
        example=12.0,
        # Paper: Sec 2.4; MATLAB: scenario.operation_wind
    ),
    "max_wave_height_m": fields.Float(
        required=True,
        description="Maximum tolerable significant wave height for the operation (in meters).",
        example=2.0,
        # Paper: Sec 2.4; MATLAB: scenario.operation_wave
    )
})

location_dto = Model("Location", {
    "type": fields.String(
        required=True,
        enum=["port", "vessel"],
        description="Specifies the location type.",
        example="vessel",
        # MATLAB: Implied by atVessel
    ),
    "id": fields.Integer(
        description="Identifier (e.g., vessel index) if type is 'vessel'. Use 0 or omit for port.",
        example=1,
        # MATLAB: Value of atVessel if > 0
    )
})

# =============================================================================
# Workforce Management (WFM) DTOs (Optional Module)
# =============================================================================

skill_definition_dto = Model("SkillDefinition", {
    "skill_id": fields.String(
        required=True,
        description="Unique identifier for the skill.",
        example="InstallSkill",
        # MATLAB: Elements in Skills
    ),
    "description": fields.String(description="Optional description.", example="Turbine Installation Expertise")
})

work_ruleset_definition_dto = Model("WorkRulesetDefinition", {
    "ruleset_id": fields.String(
        required=True,
        description="Unique identifier for this set of work rules.",
        example="OffshoreStandard",
        # MATLAB: Implied by index for maxHoursPerDay etc.
    ),
    "max_hours_per_day": fields.Float(required=True, description="Max working hours in 24h.", example=12.0), # MATLAB: maxHoursPerDay
    "max_hours_per_week": fields.Float(required=True, description="Max working hours in 7 days.", example=72.0), # MATLAB: maxHoursPerWeek
    "min_rest_period_hours": fields.Float(required=True, description="Min continuous rest between shifts.", example=11.0), # MATLAB: minPauseBlock
    "min_break_duration_hours": fields.Float(required=True, description="Duration of a mandatory short break.", example=1.0), # MATLAB: minSmallPause
    "min_break_interval_hours": fields.Float(required=True, description="Max work duration before a short break.", example=10.0) # MATLAB: minSmallPausePerHours
})

personnel_definition_dto = Model("PersonnelDefinition", {
    "person_id": fields.String(required=True, description="Unique identifier for the person/role instance.", example="Installer_A"), # MATLAB: Implicit instance
    "person_type": fields.String(description="Optional classification.", example="Installer"), # MATLAB: Element in Persons
    "skills": fields.List(fields.String, required=True, description="List of skill_ids possessed.", example=["InstallSkill"]), # MATLAB: PersonTypeSkills mapping
    "cost_per_hour": fields.Float(required=True, description="Hourly cost.", example=120.50), # MATLAB: costPerson
    "initial_location": fields.Nested(location_dto, required=True, description="Starting location."), # MATLAB: atVessel derived
    "work_ruleset_id": fields.String(required=True, description="Applicable work ruleset_id.", example="OffshoreStandard") # MATLAB: ruleset derived
})

wfm_optimization_params_dto = Model("WFMOptimizationParams", {
    "change_suppression_epsilon": fields.Float(
        default=10.0,
        description="Weight factor penalizing personnel changes (promotes continuity).",
        example=10.0
        # MATLAB: epsilon
    )
})

workforce_management_config_dto = Model("WorkforceManagementConfig", { # Renamed for clarity vs the old DTO
    "enable_wfm": fields.Boolean(
        required=True, # Explicitly require the flag to know if the section is intended
        default=False,
        description="Flag to enable workforce management constraints and resource allocation.",
        example=False
        # MATLAB: performWFM
    ),
    "skills": fields.List(fields.Nested(skill_definition_dto), description="Definitions of all available skills."), # MATLAB: Skills array
    "work_rulesets": fields.List(fields.Nested(work_ruleset_definition_dto), description="Definitions of work rulesets."), # MATLAB: Rules arrays
    "personnel": fields.List(fields.Nested(personnel_definition_dto), description="List defining personnel resources."), # MATLAB: Persons arrays
    "wfm_optimization_params": fields.Nested(wfm_optimization_params_dto, description="Parameters for WFM optimization.") # MATLAB: epsilon
    # Note: Validation that the lists are non-empty if enable_wfm is True should happen in logic.
})

# =============================================================================
# Scenario Definition DTOs (Describes the physical setup and base processes)
# =============================================================================

operation_definition_dto = Model("OperationDefinition", {
    "operation_id": fields.String(required=True, description="Unique technical ID for the operation.", example="Install_Nacelle"), # MATLAB: scenario.operation_name (by index)
    "description": fields.String(description="Human-readable name.", example="Install Nacelle Component"), # MATLAB: scenario.operation_name
    "base_duration_hours": fields.Float(required=True, description="Ideal duration without weather/WFM delays (hours).", example=3.0), # Paper: Table 3; MATLAB: scenario.operation_duration
    "weather_limits": fields.Nested(weather_limits_dto, required=True, description="Weather limits for this operation."), # Paper: Sec 2.4; MATLAB: scenario.operation_wind/wave
    "required_skills": fields.List(fields.String, description="List of skill_ids required (used if WFM enabled).", example=["InstallSkill"]) # MATLAB: JobTypeSkills derived
})

port_config_dto = Model("PortConfig", {
    "initial_owt_components": fields.Integer(required=True, min=0, description="Initial number of OWT component sets available at port.", example=12), # Paper: Initial Inventory; MATLAB: INI_STORAGE
    "max_owt_components": fields.Integer(required=True, min=0, description="Maximum storage capacity of the port for OWT component sets.", example=40), # MATLAB: STORAGE_MAX
    "min_owt_components_threshold": fields.Integer(default=0, min=0, description="Minimum component threshold triggering warning/replenishment logic.", example=5), # MATLAB: SOTRAGE_MIN derived
    # --- Optional future parameters based on MATLAB hints ---
    # "replenishment_cycle_time_hours": fields.Float(description="Time for component replenishment cycle."), # MATLAB: scenario.transport_cycleTime
    # "replenishment_amount_owt": fields.Integer(description="Number of OWT sets per replenishment cycle.") # MATLAB: scenario.transport_amountPerCycle
})

vessel_config_dto = Model("VesselConfig", {
    "num_installation_vessels": fields.Integer(required=True, min=1, default=1, description="Number of (identical) installation vessels.", example=2), # MATLAB: NUM_AGENT
    "capacity_owt": fields.Integer(required=True, min=1, default=4, description="Max OWT sets a vessel can carry per trip.", example=4), # Paper: n_L^OWT domain; MATLAB: CAPACITY_IV
    # --- Could become a list for heterogeneous fleets in the future ---
    # "vessels": fields.List(fields.Nested(individual_vessel_dto), description="List defining individual vessel properties if fleet is heterogeneous.")
})

scenario_definition_dto = Model("ScenarioDefinition", { # Renamed for clarity
    "scenario_id": fields.String(description="Optional user-defined identifier for this scenario setup.", example="Baseline_Scenario_2Vessels"),
    "owf_target_size": fields.Integer(required=True, min=1, description="Total number of OWTs to be installed.", example=40), # Paper: OWF Size; MATLAB: OWF_SIZE
    "port_config": fields.Nested(port_config_dto, required=True, description="Base port configuration."),
    "vessel_config": fields.Nested(vessel_config_dto, required=True, description="Installation vessel fleet configuration."),
    "operations": fields.List(fields.Nested(operation_definition_dto), required=True, min_items=1, description="Definitions of all possible granular operations.") # Paper: Table 3; MATLAB: scenario.operation_* arrays
})

# =============================================================================
# Simulation Configuration DTOs (Describes how to run the simulation)
# =============================================================================

weather_data_source_dto = Model("WeatherDataSource", {
    "source_type": fields.String(
        required=True,
        enum=["file", "url", "inline"], # Add more as needed (e.g., database)
        default="file",
        description="Specifies the source of the weather data.",
        example="file"
    ),
    "source_location": fields.String(
        required=True,
        description="Path to the file, URL, or the inline data string itself.",
        example="./datasets/weather/wind_data_2000.csv"
    ),
    "format_options": fields.Raw( # Use Raw for flexibility, actual parsing depends on backend logic
        description="Dictionary specifying parsing options (e.g., column names, time format, units).",
        example={"time_column": "timestamp_utc", "value_column": "wind_speed_10m", "time_format": "%Y-%m-%d %H:%M:%S", "delimiter": ","}
    )
})

log_wind_profile_config_dto = Model("LogWindProfileConfig", {
    "apply_log_profile": fields.Boolean(
        default=True,
        description="Whether to apply the log wind profile adjustment to wind data."
        # Paper: Sec 3.3 Implicitly applied
    ),
    "measurement_height_m": fields.Float(
        default=10.0,
        description="Height (m) at which the source wind data was measured.",
        example=10.0
        # Paper: Sec 3.3 (10m)
    ),
    "target_height_m": fields.Float(
        default=100.0,
        description="Target height (m) for wind speed calculation (e.g., hub height).",
        example=100.0
        # Paper: Sec 3.3 (100m)
    ),
    "surface_roughness_z0": fields.Float(
        default=0.0002,
        description="Surface roughness length (m) for log wind profile.",
        example=0.0002
        # Paper: Sec 3.3 (0.0002m for open sea)
    ),
    "zero_plane_displacement_d": fields.Float(
        default=0.0,
        description="Zero plane displacement (m) (typically 0 for open sea).",
        example=0.0
        # Paper: Sec 3.3 (d=0 assumed)
    )
})

dtmc_config_dto = Model("DTMCConfig", {
    "use_dtmc_for_weather_impact": fields.Boolean(
        default=True, # Assuming this is the primary mode based on paper
        description="Use Discrete-Time Markov Chain approach for weather integrated operation times."
        # Paper: Core methodology (Sec 3.2, Sec 4.3) Implicit
    ),
    "historical_data_start": fields.String(
        description="Start date (ISO 8601) of historical weather data used for DTMC model.",
        example="1958-01-01T00:00:00Z"
        # Paper: Sec 5 (1958 mentioned)
    ),
    "historical_data_end": fields.String(
        description="End date (ISO 8601) of historical weather data used for DTMC model.",
        example="1999-12-31T23:59:59Z"
        # Paper: Sec 5 (1999 mentioned)
    )
})

scheduling_strategy_params_dto = Model("SchedulingStrategyParams", {
    "strategy_name": fields.String(
        default="RecursiveOperabilityOptimized", # Based on Paper's description
        enum = ["RecursiveOperabilityOptimized", "SimpleGreedy", "UserDefined"], # Example options
        description="Identifier for the high-level scheduling strategy.",
        example="RecursiveOperabilityOptimized"
        # Paper: Sec 4.3.1 implicitly describes this strategy
    ),
    "planning_batch_size_owt": fields.Integer(
        required=True, # Critical parameter from paper
        min=1,
        description="Number of OWTs considered in each recursive planning step (Np from paper).",
        example=4
        # Paper: Np (Sec 4.3.1)
    ),
    "max_port_waiting_time_hours": fields.Integer(
        required=True, # Critical parameter from paper
        min=0,
        description="Maximum time (hours) vessel waits in port for weather window (tw,max from paper).",
        example=5
        # Paper: t_w,max (Sec 4.1); MATLAB: WAIT_MAX
    ),
    "fair_mode": fields.Integer(
        default=1,
        description="Parameter influencing resource allocation fairness (0: none, 1: absolute...). Interpretation depends on strategy.",
        example=1
        # MATLAB: FAIR_MODE
    )
    # Add other strategy-specific parameters here if needed
})

pruning_config_dto = Model("PruningConfig", {
    "mode": fields.Integer(
        default=0, # Default to No Pruning unless specified
        description="Controls state-space pruning method (0: None, 1: Basic...).",
        example=2
        # MATLAB: PRUNING_FLAG
    ),
    "tolerance": fields.Float(
        default=0.01,
        description="Tolerance parameter used by the pruning algorithm.",
        example=0.01
        # MATLAB: TAU
    )
})

search_config_dto = Model("SearchConfig", {
    "algorithm": fields.String(
        enum=["BFS", "DFS", "BestFirst", "Heuristic"],
        default="BestFirst",
        description="Search algorithm for state space or decision tree exploration.",
        example="BestFirst"
        # MATLAB: SEARCH_SPACE? (unclear mapping)
    ),
    "depth_limit": fields.Integer(
        description="Maximum search depth or number of simulation loops/steps.",
        example=1000
        # MATLAB: MAX_LOOP?
    )
})

simulation_config_dto = Model("SimulationConfig", { # Renamed from PetriNetDTO
    "simulation_start_datetime": fields.String(
        required=True,
        description="Simulation start (ISO 8601 format, UTC recommended).",
        example="2000-04-01T00:00:00Z"
        # Paper: t_start; MATLAB: START_DATE
    ),
    "simulation_end_datetime": fields.String(
        required=True,
        description="Simulation end (ISO 8601 format, UTC recommended).",
        example="2000-10-01T00:00:00Z"
        # Paper: t_end = t_start + t_span; MATLAB: END_DATE
    ),
    "time_step_hours": fields.Integer(
        default=1,
        min=1,
        description="Duration of simulation discrete time step (hours).",
        example=1
        # Paper: Δt; MATLAB: DELTA_TIME
    ),
    "wind_data": fields.Nested(
        weather_data_source_dto,
        required=True,
        description="Wind data source specification."
        # MATLAB: WIND_DATA variable reference
    ),
    "wave_data": fields.Nested(
        weather_data_source_dto,
        required=True,
        description="Wave data source specification."
        # MATLAB: WAVE_DATA variable reference
    ),
    "log_wind_profile": fields.Nested(
        log_wind_profile_config_dto,
        description="Configuration for adjusting wind speed based on height (optional, defaults apply if omitted).",
        required=False
        # Paper: Sec 3.3
    ),
    "dtmc_config": fields.Nested(
        dtmc_config_dto,
        description="Configuration for DTMC weather impact model (optional, defaults apply if omitted).",
        required=False
        # Paper: Sec 3.2
    ),
    "scheduling_strategy_params": fields.Nested(
        scheduling_strategy_params_dto,
        required=True, # Core parameters are here
        description="Parameters specific to the chosen high-level scheduling strategy (includes Np, tw_max)."
        # Paper: Sec 4.3.1; MATLAB: FAIR_MODE, WAIT_MAX etc.
    ),
    "pruning_config": fields.Nested(
        pruning_config_dto,
        description="State-space pruning configuration (optional).",
        required=False
        # MATLAB: PRUNING_FLAG, TAU
    ),
    "search_config": fields.Nested(
        search_config_dto,
        description="Search algorithm configuration (optional).",
        required=False
        # MATLAB: SEARCH_SPACE, MAX_LOOP
    ),
    "random_seed": fields.Integer(
        description="Optional seed for RNG for reproducibility.",
        example=42
    ),
    "output_options": fields.List(
        fields.String,
        description="Specify desired results (e.g., 'gantt', 'kpis', 'operability_score').",
        example=["gantt", "kpis"],
        default=["gantt", "kpis"]
    ),
    "logging_level": fields.String(
        enum=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        description="Verbosity level for simulation logging."
        # MATLAB: PRINT_LOOP_NUMBER (less flexible)
    )
})

# =============================================================================
# Top-Level Request and Response DTOs
# =============================================================================

planning_request = Model("PlanningRequest", {
    "scenario_definition": fields.Nested(
        scenario_definition_dto,
        required=True,
        description="Defines the physical setup, goals, and possible base operations."
    ),
    "simulation_config": fields.Nested(
        simulation_config_dto,
        required=True,
        description="Defines how the simulation should be run (time, weather, algorithms, strategy etc.)."
    ),
    "workforce_management": fields.Nested( # Top-level WFM block is optional
        workforce_management_config_dto,
        description="Optional configuration for workforce management. Required only if 'enable_wfm' inside this block is True.",
        required=False
    )
})

# --- Response DTOs (Example Structure - Adjust based on actual simulation output) ---

gantt_entry_dto = Model("GanttEntry", {
    "task_id": fields.String(required=True, description="Unique ID for the task instance (e.g., Load_Vessel1_Trip3)"),
    "resource_id": fields.String(required=True, description="ID of the primary resource (e.g., Vessel_1)"),
    "secondary_resource_ids": fields.List(fields.String, description="IDs of secondary resources (e.g., Personnel IDs if WFM enabled)"),
    "operation_id": fields.String(required=True, description="ID of the operation type being performed (e.g., Install_Nacelle)"),
    "start_time": fields.String(required=True, description="Start time of the task (ISO 8601 UTC)"),
    "end_time": fields.String(required=True, description="End time of the task (ISO 8601 UTC)"),
    "status": fields.String(enum=["PLANNED", "IN_PROGRESS", "COMPLETED", "FAILED", "WEATHER_DELAY"], description="Status of the task."),
    "label": fields.String(description="Display label for the Gantt chart entry")
})

kpi_set_dto = Model("KPISet", {
    "total_duration_days": fields.Float(description="Total project duration in days."),
    "total_cost": fields.Float(description="Total estimated cost (requires cost inputs)."),
    "operability_score": fields.Float(description="Calculated operability score (Paper Sec 4.3)."),
    "vessel_utilization_percent": fields.Float(description="Average utilization percentage of installation vessels."),
    "average_owt_installation_time_days": fields.Float(description="Average time per OWT installation cycle."),
    "num_owt_installed": fields.Integer(description="Number of OWTs successfully installed."),
    "weather_downtime_percent": fields.Float(description="Percentage of time lost due to weather constraints.")
    # Add more relevant KPIs as needed
})

planning_result_dto = Model("PlanningResult", {
    "schedule_gantt": fields.List(
        fields.Nested(gantt_entry_dto),
        description="Data suitable for generating a Gantt chart visualization of the schedule."
    ),
    "kpis": fields.Nested(
        kpi_set_dto,
        description="Key Performance Indicators summarizing the plan's performance."
    ),
    "raw_event_log_url": fields.String( # Provide URL instead of embedding potentially large logs
        description="URL to download the detailed simulation event log, if requested."
    ),
    "summary_report_url": fields.String( # Optional summary report
        description="URL to download a summary report document."
    )
    # Add other result types based on output_options
})

planning_response = Model("PlanningResponse", {
    "status": fields.String(
        required=True,
        enum=["SUCCESS", "FAILURE", "PENDING", "VALIDATION_ERROR"],
        description="Overall status of the planning request processing."
    ),
    "message": fields.String(
        description="Human-readable status message, providing context or error details."
    ),
    "job_id": fields.String(
        description="Identifier for the planning task, useful for asynchronous processing or tracking."
    ),
    "results": fields.Nested(
        planning_result_dto,
        description="Contains the detailed planning results if the status is 'SUCCESS'.",
        required=False # Only present on success
    )
})