import pm4py
import os, pathlib, io
from datetime import datetime
import pandas as pd
from l3s_offshore_2.utils.constants import TEMP_DIR
from werkzeug.datastructures import FileStorage

from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

ALLOWED_EXTENSIONS = {'csv', 'xes'}

def allowed_file_extension(filename:str):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )
    
    
def event_log_processer(uploaded_event_log):
    event_log_suffix = uploaded_event_log.filename.rsplit('.', 1)[-1]
    if event_log_suffix == 'csv':
        raw_data = pd.read_csv(uploaded_event_log, sep=";")
        event_log = pm4py.format_dataframe(raw_data, 
                                           case_id='case_id', 
                                           activity_key='activity', 
                                           timestamp_key='timestamp', 
                                           timest_format='%Y-%m-%d %H:%M:%S%z')
    
    if event_log_suffix == 'xes':
        event_log = pm4py.read_xes(uploaded_event_log)
    
    return event_log


def inductive_miner(uploaded_event_log):
    '''
    A wrapper of pm4py.discover_petri_net_inductive
    
    input:
        event_log
    
    output:
        Petri net in .pnml file
    '''
    
    event_log = event_log_processer(uploaded_event_log)
    pn, im, fm = pm4py.discover_petri_net_inductive(log=event_log, timestamp_key="time:timestamp")
    
    uploaded_file_id = uploaded_event_log.filename.rsplit('.', 1)[0].lower()
    
    time_id = datetime.now().strftime("%Y%m%d%H%M%S")
    pnml_file_path = f'{TEMP_DIR}/{uploaded_file_id}_{time_id}.pnml'
    
    pm4py.write_pnml(petri_net=pn, initial_marking=im, final_marking=fm, file_path=pnml_file_path)
    
    return pnml_file_path




# # absolute path to this file
# this_file = os.path.abspath(__file__)  
# # directory containing this file
# this_dir = os.path.dirname(this_file)  

# print("File:", this_file)
# print("Directory:", this_dir)
