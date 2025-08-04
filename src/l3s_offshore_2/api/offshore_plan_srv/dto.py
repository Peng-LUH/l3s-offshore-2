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

dto_response_opt_schedule = Model("ResponseOptSchedule", {
    "status": fields.Integer(required=True, default=201),
    "schedule": fields.List(required=True, default=[])
})