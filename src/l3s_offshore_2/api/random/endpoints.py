from http import HTTPStatus
import os, json
import random
from dotenv import load_dotenv
load_dotenv()

# import flask
from flask import request, url_for

# import flask-restx
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser

## import dto
from .dto import random_request_model, random_response_model

ns_random = Namespace("random", validate=True)

## dto registration
ns_random.models[random_request_model.name] = random_request_model
ns_random.models[random_response_model.name] = random_response_model


@ns_random.route("/get-random-recommendation", endpoint="random")
class RandomRecommendation(Resource):
    @ns_random.response(int(HTTPStatus.CREATED), "Success")
    @ns_random.response(int(HTTPStatus.BAD_REQUEST), "Number of recommendation is either negative or exceed the number of existing contents")
    @ns_random.expect(random_request_model)
    @ns_random.marshal_with(random_response_model)
    def post(self):
        request_data = ns_random.payload
        num_of_rec = request_data.get("num_of_rec")
        
        # print(os.environ["BASE_DATASETS_PATH"])
        json_file_dir = os.path.join(os.getenv('BASE_DATASETS_PATH'), 'mls-tasks-full/json/data.json')
        print(json_file_dir)
        with open(json_file_dir) as f:
            data_arr = json.load(f)

        len_of_data = len(data_arr)
        
        try: 
            if num_of_rec > len_of_data:
                raise ValueError("Number of recommendation requested cannot be larger than the number of contents existing.")

            if num_of_rec < 0:
                raise ValueError("Number of recommendation cannot be negativ")
            
            random_elements = random.sample(data_arr, num_of_rec)
            print(type(random_elements))
            ids = []
            for e in random_elements:
                print(e['@id'])
                ids.append(e["@id"])
            
            print(type(ids))
            response = {"results": ids}
            
            return response, HTTPStatus.CREATED
        
        except ValueError as e:
            return e.args, HTTPStatus.BAD_REQUEST
        except TypeError as e:
            return e.args, HTTPStatus.CONFLICT