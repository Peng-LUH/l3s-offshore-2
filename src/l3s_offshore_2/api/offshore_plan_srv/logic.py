
from gspn4py.offshoreplan import offshore_utils
from datetime import datetime
import os
import numpy as np
from pprint import pprint

WEATHER_DATA_PATH = f"{os.getcwd()}/WEATHER_DATA/weatherdata.npy"


# def get_operation_prabability(job_requirements):
#     weather_data = np.load(WEATHER_DATA_PATH)
#     operation_prob = offshore_utils.get_prob(weather=weather_data, job_requirements=job_requirements)
#     print(f"Operation Probability: {operation_prob}")
#     return operation_prob

def get_expected_operation_duration(current_date:str, job_duration:float, job_requirements:list):
    
    estimated_duration = offshore_utils.get_operation_duration_markov(current_date, 
                                                                      job_duration=[job_duration], 
                                                                      job_requirements=np.column_stack(job_requirements))
    return estimated_duration


def convert_sim_results_to_response(sim_results:dict):
    
    ops = sim_results["plan"]
    
    pattern = ["Reposition", "JackUp", "Construction", "JackDown"]
    merged = []
    i = 0
    
    while i < len(ops):
        # check if the next operations match the pattern
        # op = (op_name, op_duration, op_delay, op_start, op_end)
        if (i + 3 < len(ops) and [ops[i][0], ops[i+1][0], ops[i+2][0], ops[i+3][0]] == pattern) :
                
                op_name = 'Install'
                op_duration = ops[i][1] + ops[i+1][1] + ops[i+2][1] + ops[i+3][1]
                op_delay = ops[i][2] + ops[i+1][2] + ops[i+2][2] + ops[i+3][2]
                op_start = ops[i][3] # start of "Reposition"
                op_end = ops[i+3][4] # end of "JackDown"
                
                merged.append((op_name, op_duration, op_delay, op_start, op_end))
                i += 4  # Skip the merged ones
        elif ops[i][0] == "LoadingOWT":
            n = int(ops[i][1]/12)
            for j in range(n):
                if j == n-1:
                    temp = (ops[i][0], 12, ops[i][2], ops[i][3]+12*j, ops[i][3]+12*(j+1)+ops[i][2]-1)
                else:
                    temp = (ops[i][0], 12, 0, ops[i][3]+12*j, ops[i][3]+12*(j+1)-1)
                    
                merged.append(temp)
            i += 1
        else:
            merged.append(ops[i])
            i += 1
    
    mapping_operationId = {
        "LoadingOWT": 3, # load
        "SailingForth": 2, # to_site
        "SailingBack": 1, # to_port
        "Install" : 0,
        # "Construction": 0, # install
        # "JackUp": 0, # install
        # "JackDown": 0, # install
        # "Reposition": 0 # install
    }
    operationsId = []
    operationsStart = []
    operationsEnd = []
    
    
    for op in merged:
        operationsId.append(mapping_operationId[op[0]])
        operationsStart.append(op[3])
        operationsEnd.append(op[4])
    
    results = {
                "planned_operationsId": [[-1], operationsId],
                "planned_operationsStart": [[-1], operationsStart],
                "planned_operationsEnd": [[-1], operationsEnd],
                "planned_restockOperations": [-1]
            }
    return  results


def calc_opt_install_cycle_single_vessel(scenario:dict):
    
    from gspn4py import TimedPetriNet, OffshoreSimulator
    from gspn4py.utils import import_pndf_from_json
    pndf = import_pndf_from_json(json_file_path=f"{os.getcwd()}/models/offshore_models/full_cyclic_model.json")
    
    pn = TimedPetriNet()
    r = pn.build_from_pndf(pndf_json=pndf)
    
    if r:
        # print("TPN build successfully.")
        # run simulation
        timed_simulator = OffshoreSimulator(timed_petri_net=pn, properties=scenario)
        sim_results = timed_simulator.calc_opt_install_cycle_single_vessel_single()
        # pprint(sim_results)
        # opt_schedule = timed_simulator.get_sim_results()
        return sim_results
    else:
        raise ValueError("Cannot build model from pndf.")
    

def calc_opt_schedule_single_vessel_to_horizon(scenario:dict):
    from gspn4py import TimedPetriNet, OffshoreSimulator
    from gspn4py.utils import import_pndf_from_json
    pndf = import_pndf_from_json(json_file_path=f"{os.getcwd()}/models/offshore_models/full_cyclic_model.json")
    pn = TimedPetriNet()
    r = pn.build_from_pndf(pndf_json=pndf)
    
    if r:
        timed_simulator = OffshoreSimulator(timed_petri_net=pn, properties=scenario)
        
        sim_results = timed_simulator.calc_opt_schedule_single_vessel_to_horizon()
            
        
        return sim_results
    else:
        raise ValueError("Cannot build model from pndf.")
    



def opt_schedule(start_at:datetime, num_owt):
    
    
    
    start_idx = offshore_utils.date_to_weather_index(year=start_at.year, 
                                         month=start_at.month, 
                                         day=start_at.day,
                                         hour=start_at.hour
                                         )
    
    
    
    pass