from http import HTTPStatus
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import json
from pprint import pprint
import time
import pm4py
import tempfile
# import flask
from flask import request, url_for, send_file, abort, Response, jsonify
import os
import numpy as np

# import flask-restx
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser

# import gspn4py
from gspn4py.utils import import_pndf_from_json


# import logic
from .logic import (
    get_expected_operation_duration,
    calc_opt_install_cycle_single_vessel,
    convert_sim_results_to_response,
    calc_opt_schedule_single_vessel_to_horizon
)


## define Namespace
ns_offshore_plan = Namespace("Offshore Plan", validate=True)

## import dto
from .dto import (dto_request_job_duration,
                  dto_request_opt_schedule_immediate,
                  dto_request_opt_schedule_horizon,
                #   dto_response_opt_schedule,
                  dto_request_offshore_scenario,
                  dto_response_offshore_plan,
                  dto_request_display_schedule
                )

## register dto to Namespace
ns_offshore_plan.models[dto_request_job_duration.name] = dto_request_job_duration
ns_offshore_plan.models[dto_request_opt_schedule_immediate.name] = dto_request_opt_schedule_immediate
ns_offshore_plan.models[dto_request_opt_schedule_horizon.name] = dto_request_opt_schedule_horizon
# ns_offshore_plan.models[dto_response_opt_schedule.name] = dto_response_opt_schedule
ns_offshore_plan.models[dto_request_offshore_scenario.name] = dto_request_offshore_scenario
ns_offshore_plan.models[dto_response_offshore_plan.name] = dto_response_offshore_plan
ns_offshore_plan.models[dto_request_display_schedule.name] = dto_request_display_schedule


@ns_offshore_plan.route('/get-tpn-cyclic-model')
@ns_offshore_plan.expect()
class GetTpnCyclicModel(Resource):
    def get(self):
        
        # load pndf
        pndf = import_pndf_from_json(json_file_path=f"{os.getcwd()}/models/offshore_models/full_cyclic_model.json")
        
        return {"results": pndf}, 200


@ns_offshore_plan.route('/calc-operation-duration')
@ns_offshore_plan.expect(dto_request_job_duration)
class CalcOperationDuration(Resource):
    def post(self):
        data = request.json
        
        job_duration = data["job_duration"]
        current_date = data["current_date"]
        wind_limit = data["wind_limit"]
        wave_limit = data["wave_limit"]
        
        expected_operation_duration = get_expected_operation_duration(current_date=current_date,
                                                                      job_duration=job_duration,
                                                                      job_requirements=[wind_limit, wave_limit])
        json_str = json.dumps(expected_operation_duration.tolist())

        return {"results": json_str}, 200


        
@ns_offshore_plan.route('/calc-opt-install-cycle-single-vessel')
@ns_offshore_plan.expect(dto_request_offshore_scenario)
# @ns_offshore_plan.marshal_list_with(dto_response_offshore_plan)
class CalcOptScheduleSingleVesselSingleInstallCycle(Resource):
    def post(self):
        """
        calculate the optimal schedule for single vessel in single installtion cycle
        """
        
        scenario = request.get_json(force=True, silent=False)
        
        # start = time.perf_counter()
        sim_results = calc_opt_install_cycle_single_vessel(scenario=scenario)
        # elapsed = time.perf_counter() - start
        
        
        results = convert_sim_results_to_response(sim_results)
        print("Results:", results)
        # results["elapsed_time"] = elapsed
        
        if results is None:
            results = {
                "planned_operationsId": [[-1], [-1]],
                "planned_operationsStart": [[-1], [-1]],
                "planned_operationsEnd": [[-1], [-1]],
                "planned_restockOperations": [-1],
                "elapsed_time": 0
            }
        
        return results, 200


@ns_offshore_plan.route('/calc-opt-schedule-single-vessel-to-horizon')
@ns_offshore_plan.expect(dto_request_offshore_scenario)
class CalcOptScheduleSingleVesselToHorizon(Resource):
    def post(self):
        '''
        Calculate optimal schedule starting from given date with defined horizon.
        '''
        scenario = request.get_json(force=True, silent=False)
        
        # start = time.perf_counter()
        sim_results = calc_opt_schedule_single_vessel_to_horizon(scenario=scenario)
        # elapsed = time.perf_counter() - start
        
        results = convert_sim_results_to_response(sim_results)
        
        if results is None:
            results = {
                "planned_operationsId": [[-1], [-1]],
                "planned_operationsStart": [[-1], [-1]],
                "planned_operationsEnd": [[-1], [-1]],
                "planned_restockOperations": [-1],
                "elapsed_time": 0
            }
        
        return results, 200
    
    

@ns_offshore_plan.route('/display-single-vessel-schedule')
class DiplaySIngleVesselSchedule(Resource):
    @ns_offshore_plan.expect(dto_request_display_schedule)
    @ns_offshore_plan.produces(['application/pdf'])
    def post(self):
        """
        Display the schedule for single vessel.
        """
        # This endpoint is for demonstration purposes, it can be used to visualize the schedule.
        # In a real application, you might want to return a more complex visualization or data structure.
        
        # For now, we will return a simple message.
        
        payload = request.get_json(force=True)
        
        title   = payload.get("title", "Operation Schedule")
        xlabel  = payload.get("xlabel", "Time")
        
        mapping_operationId = {
                                "Loading OWT": 3,   # load
                                "Sailing Forth": 2, # to_site
                                "Sailing Back": 1,  # to_port
                                "Install": 0,
                            }
        
        try:
            from gspn4py.utils.viewer import make_schedule_figure
            import io
            import matplotlib
            matplotlib.use("Agg") 
            import matplotlib.pyplot as plt
            
            fig = make_schedule_figure(
                planned=payload,
                mapping_operationId=mapping_operationId,
                title=title,
                xlabel=xlabel,
            )
            
            # write to in-memory PDF
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf", bbox_inches="tight")
            plt.close(fig)
            buf.seek(0)
            return send_file(
                buf,
                mimetype="application/pdf",
                as_attachment=True,
                download_name="schedule.pdf",
            )
        except Exception as e:
            # You can customize error shape as needed
            ns_offshore_plan.abort(400, f"Failed to render schedule: {e}")
            
        # return {"message": "This endpoint will display the schedule for single vessel."}, HTTPStatus.OK

# @ns_offshore_plan.route('/calc-opt-schedule-single-vessel-from-current')
# @ns_offshore_plan.expect(dto_request_offshore_scenario)
# # @ns_offshore_plan.marshal_list_with(dto_response_offshore_plan)
# class CalcOptScheduleFromCurrent(Resource):
#     def post(self):
#         '''
#         Calculate optimal schedule immediate from given date
#         '''
#         data = request.json
        
#         # current_date = data["current_date"]
        
#         # opt_schedule = get_schedule_start_from_current(current_date=current_date)
        
        
#         # current_schedule = get_opt_schedule_start_from_current()
        
#         # pprint(opt_schedule["firing_sequence"])
#         # print(data)
        
#         results = {
#             "planned_operationsId": [[-1], [-1]],
#             "planned_operationsStart": [[-1], [-1]],
#             "planned_operationsEnd": [[-1], [-1]],
#             "planned_restockOperations": [-1]
#         }
        
#         return results, 200