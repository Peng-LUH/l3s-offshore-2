from flask_restx import Model, fields


dto_request_job_duration = Model("RequestJobDuration", {
    "current_date": fields.String(required=True, default="2000-04-01-08"),
    "job_duration": fields.Integer(required=True, default=5),
    "wind_limit": fields.Float(reuqired=True, default=10.0),
    "wave_limit": fields.Float(required=True, default=2.0)
})

dto_request_opt_schedule_immediate = Model("RequestOptScheduleImmediate", {
    "current_date": fields.String(required=True, default="2000-04-01-08", description="Start of installation process."),
    "num_owts": fields.String(required=True, default=12, description="Number of OWTs to build."),
    "base_port_storage": fields.String(required=True, default=32)
})

dto_request_opt_schedule_horizon = Model("RequestOptScheduleHorizon", {
    "horizon": fields.Integer(required=True, default=86, description="Maximal horizon in the future."),
    "current_date": fields.String(required=True, default="2000-04-01-08", description="Start of installation process."),
    "num_owts": fields.String(required=True, default=12, description="Number of OWTs to build."),
    "base_port_storage": fields.String(required=True, default=32)
})

# dto_response_opt_schedule = Model("ResponseOptSchedule", {
#     "status": fields.Integer(required=True, default=201),
#     "schedule": fields.List(required=True, default=[])
# })



dto_request_offshore_scenario = Model("RequestOffshoreScenario",{
    "sim_scenario_decisionMode": fields.Integer(required=True, default=0),
    "optim_pathGUROBI": fields.String(required=True, default="C:/gurobi1201/win64/matlab"),
    "optim_maxOptimTime": fields.Integer(required=True, default=43200),
    "optim_useHistoricSolutions": fields.Integer(required=True, default=1),
    "optim_useHistoricTillIteration": fields.Integer(required=True, default=9999),
    "optim_useInitialPoint": fields.Integer(required=True, default=1),
    "optim_useForecasts": fields.Integer(required=True, default=1),
    "optim_applyWithRealWeatherData": fields.Integer(required=True, default=1),
    "optim_stepWidth": fields.Integer(required=True, default=168),
    "optim_planningHorizons": fields.Integer(required=True, default=2),
    "alorithm_waitIfNoPlanFound": fields.Integer(required=True, default=24),
    "alorithm_maxIterations": fields.Integer(required=True, default=9999),
    "pn_deltaTime": fields.Integer(required=True, default=1),
    "pn_maxWaitTime": fields.Integer(required=True, default=96),
    "pn_fairMode": fields.Integer(required=True, default=1),
    "pn_pruningFlag": fields.Integer(required=True, default=2),
    "pn_tau": fields.Float(required=True, default=0.01),
    "pn_searchSpace": fields.Integer(required=True, default=0),
    "scenario_simulationStartDate": fields.String(required=True, default="15-Jun-2000-00", description="Start of simulation."),
    "scenario_targetPlanTime": fields.Integer(required=True, default=999999),
    "scenario_OWTsToBuild": fields.Integer(required=True, default=50),
    "operation_name": fields.List(fields.String, required=True, default=[ "Install Tower", "Install Nacelle", "Install Blade 1", "Install Blade 2", "Install Blade 3", "Install Hub", "Move", "Reposition in Field", "Jack-up", "Jack-Down", "Load OWT Components" ]),
    "operation_duration": fields.List(fields.Integer, required=True, default=[ 3, 3, 2, 2, 2, 2, 4, 1, 2, 2, 12 ]),
    "operation_wind": fields.List(fields.Float, required=True, default=[ 12, 12, 10, 10, 10, 12, 21, 14, 14, 14, 99 ]),
    "operation_wave": fields.List(fields.Float, required=True, default=[ 99, 99, 99, 99, 99, 99, 2.5, 2, 1.8, 1.8, 99 ]),
    "processChain_install": fields.List(fields.Integer, required=True, default=[ 8, 9, 1, 2, 3, 4, 5, 6, 10 ]),
    "processChain_move": fields.Integer(required=True, default=7),
    "processChain_load": fields.Integer(required=True, default=11),
    "basePort_numLoadingBays": fields.Integer(required=True, default=1),
    "basePort_storageCapacity": fields.Integer(required=True, default=32),
    "transport_amountPerCycle": fields.Integer(required=True, default=8),
    "transport_cycleTime": fields.Integer(required=True, default=312),
    "vessel_numInstallationVessels": fields.Integer(required=True, default=2),
    "vessel_capacity": fields.List(fields.Integer, required=True, default=[4, 4]),
    "cost_offshore": fields.List(fields.Integer, required=True, default=[1800, 1800]),
    "cost_portOp": fields.Integer(required=True, default=1200),
    "cost_Fuel": fields.List(fields.Integer, required=True, default=[600, 600]),
    "cost_benefitForFinishingAnOWT": fields.Integer(required=True, default=135000),
    "cost_maxBenefitForFinishingEarly": fields.Integer(required=True, default=8100),
    "cost_storagePenalty": fields.Integer(required=True, default=-10),
    "cost_waitingPenalty": fields.Integer(required=True, default=-900),
    "basePort_Latitude": fields.Float(required=True, default=53.454399),
    "basePort_Longitude": fields.Float(required=True, default=6.838584),
    "installationSite_Latitude": fields.Float(required=True, default=54.5),
    "installationSite_Longitude": fields.Float(required=True, default=6.4),
    "prodPortTower_Latitude": fields.Float(required=True, default=53.865448),
    "prodPortTower_Longitude": fields.Float(required=True, default=8.72604),
    "prodPortBlade_Latitude": fields.Float(required=True, default=53.543192),
    "prodPortBlade_Longitude": fields.Float(required=True, default=8.567501),
    "prodPortNacelle_Latitude": fields.Float(required=True, default=53.543192),
    "prodPortNacelle_Longitude": fields.Float(required=True, default=8.567501),
    "transport_vesselspeed": fields.Float(required=True, default=9.5),
    "transport_maxSpace": fields.Integer(required=True, default=2646),
    "transport_maxWeight": fields.Integer(required=True, default=8900),
    "transport_componentSpace": fields.List(fields.Integer, required=True, default=[650, 300, 263]),
    "transport_componentWeight": fields.List(fields.Integer, required=True, default=[600, 120, 500]),
    "transport_componentSetUpTime": fields.List(fields.Integer, required=True, default=[0, 0, 0]),
    "transport_componentLoadingTime": fields.List(fields.Integer, required=True, default=[2, 8, 10]),
    "transport_unloadFactor": fields.Float(required=True, default=0.6),
    "transport_route": fields.List(fields.Integer, required=True, default=[-1]),
    "state_OWTsFinished": fields.Integer(required=True, default=0),
    "state_currentDate": fields.String(required=True, default="15-Jun-2000"),
    "state_vessel_location": fields.List(fields.Integer, required=True, default=[0, 0]),
    "state_vessel_currentStorage": fields.List(fields.Integer, required=True, default=[0, 0]),
    "state_vessel_availabeFromDate": fields.List(fields.String, required=True, default=["15-Jun-2000","15-Jun-2000"]),
    "state_basePort_currentStorage": fields.Integer(required=True, default=20),
    "state_basePort_totalComponentSetsDelivered": fields.Integer(required=True, default=20),
    "state_portRestockEarliest": fields.Integer(required=True, default=312),
    "state_currentPlans_ops": fields.List(fields.List(fields.Integer), required=True, default=[[-1], [-1]]),
    "state_currentPlans_start": fields.List(fields.List(fields.Integer), required=True, default=[[-1], [-1]]),
    "state_currentPlans_end": fields.List(fields.List(fields.Integer), required=True, default=[[-1], [-1]]),
    "state_currentlyBuiltOWTs": fields.Integer(required=True, default=0),
    "state_basePort_currentlyUsedLoadingBays": fields.Integer(required=True, default=0),
    "state_vessel_speed": fields.List(fields.Integer, required=True, default=[16, 16, 16])
})


dto_response_offshore_plan = Model("ResponseOffshorePlan", {
    "planned_operationsId": fields.List(fields.Integer, default=[[-1], [-1]]),
    "planned_operationsStart": fields.List(fields.List(fields.Integer), default= [[-1], [-1]]),
    "planned_operationsEnd": fields.List(fields.List(fields.Integer), default=[[-1], [-1]]),
    "planned_restockOperations": fields.List(fields.Integer, default=[-1])
})


dto_request_display_schedule = Model("RequestDisplaySchedule", {
    "planned_operationsId":    fields.List(fields.List(fields.Integer),
                                           required=True,
                                           default=[[-1], [3, 3, 3, 3, 2, 0, 0, 0, 0, 1, 3, 3, 3, 3, 2, 0, 0, 0, 0, 1]],
                                           description="List of lists of operation IDs or [-1]"),
    "planned_operationsStart": fields.List(fields.List(fields.Integer), 
                                           required=True,
                                           default=[[-1], [0, 12, 24, 36, 48, 52, 72, 92, 112, 132, 136, 148, 160, 172, 184, 188, 312, 332, 352, 372]], 
                                           description="List of lists of start times or [-1]"),
    "planned_operationsEnd":   fields.List(fields.List(fields.Integer), 
                                           required=True,
                                           default=[[-1], [12, 24, 36, 48, 52, 72, 92, 112, 132, 136, 148, 160, 172, 184, 188, 312, 332, 352, 372, 376]],
                                           description="List of lists of stop times or [-1]"),
    "planned_restockOperations": fields.List(fields.Integer,
                                             required=False,
                                             default=[-1],
                                             description="List (or list of lists) of restock marks or [-1]"),
    "title": fields.String(required=False, default="Single Vessel Schedule", description="Plot title"),
    "xlabel": fields.String(required=False, default="Time", description="X axis label"),
})