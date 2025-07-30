from flask_restx import Model, fields


operation_duration_requirements = Model("Operation Duration Requirements", {
    "operation_duration": fields.Integer(required=True, default=5),
    "wind_limit": fields.Float(reuqired=True, default=10.0),
    "wave_limit": fields.Float(required=True, default=2.0)
})