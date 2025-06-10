import pm4py
# from l3s_offshore_2.api.test import ns_sim
from l3s_offshore_2.petri_net_sim.simplepn import SimplePN, SimpleSimulator



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