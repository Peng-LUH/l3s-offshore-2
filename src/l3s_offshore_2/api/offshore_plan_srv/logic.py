
from gspn4py.offshoreplan import offshore_utils
from datetime import datetime
import os
import numpy as np


WEATHER_DATA_PATH = f"{os.getcwd()}/WEATHER_DATA/weatherdata.npy"


def get_operation_prabability(job_requirements):
    weather_data = np.load(WEATHER_DATA_PATH)
    operation_prob = offshore_utils.get_prob(weather=weather_data, job_requirements=job_requirements)
    print(f"Operation Probability: {operation_prob}")
    return operation_prob

def get_expected_operation_duration(job_duration:int, job_requirement:list):
    ## load weather data
    weather_data = np.load(WEATHER_DATA_PATH)
    
    estimated_duration = offshore_utils.get_duration_owt_markoff_single(weather=weather_data, 
                                                                        jobs_duration=list(job_duration), 
                                                                        jobs_requirements=job_requirement)
    return estimated_duration

def opt_schedule(start_at:datetime, num_owt):
    
    
    
    start_idx = offshore_utils.date_to_weather_index(year=start_at.year, 
                                         month=start_at.month, 
                                         day=start_at.day,
                                         hour=start_at.hour
                                         )
    
    
    
    pass