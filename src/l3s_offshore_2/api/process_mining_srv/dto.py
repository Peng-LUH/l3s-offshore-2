from flask_restx import Model, fields

random_request_model = Model("RandomRequest", {
    "num_of_rec": fields.Integer(required=True, default=10)
})

random_response_model = Model("RandomResponse", {
    "results": fields.List(fields.String, required=True)
})


# miner_request_model = Model("MinerRequestModel", {
#     'csv': fields.String(required=True, 
#                          description='The full CSV text of event log',
#                          example="case_id;activity;timestamp;costs;resource\n"
#                                  "1;r;2024-12-17 11:19:35+0000;100;Resource1\n"
#                                  "…"
#                         )
# })

# miner_response_model = Model("MinerResponseModel", {
#     'pnml': fields.String(required=True, 
#                          description='The full PNML text of Petri nets model')
# })