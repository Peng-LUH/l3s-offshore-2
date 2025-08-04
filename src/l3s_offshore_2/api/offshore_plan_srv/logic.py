
from gspn4py.offshoreplan import offshore_utils
from datetime import datetime
import os
import numpy as np


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


def get_schedule_start_from_current(current_date:str):
    
    from gspn4py import TimedPetriNet, TimedSimulator
    from gspn4py.utils import import_pndf_from_json
    
    
    pndf = import_pndf_from_json(json_file_path=f"{os.getcwd()}/models/offshore_models/full_cyclic_model.json")
    
    # print(current_date)
    # print(pndf)
    
    pn = TimedPetriNet()
    r = pn.build_from_pndf(pndf_json=pndf)
    
    if r:
        print("TPN build successfully.")
        # run simulation
        timed_simulator = TimedSimulator(timed_petri_net=pn)
        timed_simulator.run()
        
        opt_schedule = timed_simulator.get_sim_results()
        return opt_schedule
    else:
        raise ValueError("Cannot build model from pndf.")
    
    
    



def opt_schedule(start_at:datetime, num_owt):
    
    
    
    start_idx = offshore_utils.date_to_weather_index(year=start_at.year, 
                                         month=start_at.month, 
                                         day=start_at.day,
                                         hour=start_at.hour
                                         )
    
    
    
    pass