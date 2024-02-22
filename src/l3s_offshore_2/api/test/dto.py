from flask_restx import Model, fields

test_model = Model("test", {
    "message": fields.String(required=True, default="success")
})

# test_response_model = Model("test", {
#     "message": fields.String(required=True)
# })