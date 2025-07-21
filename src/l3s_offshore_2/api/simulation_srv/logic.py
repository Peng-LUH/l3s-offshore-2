import pm4py
import tempfile
import json
# from l3s_offshore_2.api.test import ns_sim
from l3s_offshore_2.petri_net_sim.simplepn import SimplePN, SimpleSimulator
from gspn4py import TimedPetriNet, TimedSimulator
from gspn4py import pnml_to_json
from pprint import pprint

def simple_sim_run(pnml_path):
    pn, im, fm = pm4py.read_pnml(file_path=pnml_path)
            
    simple_pn = SimplePN.convert_to_simple_pn(pn=pn, initial_marking=im)
    
    sim = SimpleSimulator(net=simple_pn, initial_marking=im)
    
    sim.run()
    
    # Extracting only the PNML IDs from the firing_sequence
    firing_seq_ids = [pnml_id for pnml_id, timestamp in sim.firing_sequence]
    
    simulation_results = {
        "firing_seq" : firing_seq_ids, # Use the new list of PNML IDs
        "detailed_log": sim.detailed_log
    }
    return simulation_results


def timed_sim_run(model_path):
    file_type = model_path.split('.')[-1]
    
    if file_type == 'pnml':
        temp_json = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_json_path = temp_json.name
        temp_json.close()
        pndf = pnml_to_json(pnml_path=model_path, json_path=temp_json_path)
    elif file_type == 'json':
        with open(model_path, 'r') as f:
            pndf = json.load(f)
    
    # return pndf
    pn = TimedPetriNet()

    r = pn.build_from_pndf(pndf_json=pndf)
    timed_sim = TimedSimulator(timed_petri_net=pn)
    timed_sim.run()
    results = timed_sim.get_sim_results()
    pprint(results)
    
    sim_results = {
        'stop_at': results["stop_at"],
        'final_marking': [{f"{p.name}": f"{p.num_of_tokens}"} for p in results["final_marking"]],
        'initial_marking': [{f"{p.name}": f"{p.num_of_tokens}"} for p in results["initial_marking"]],
        'firing_sequence': results['firing_sequence']
    }
    
    return sim_results