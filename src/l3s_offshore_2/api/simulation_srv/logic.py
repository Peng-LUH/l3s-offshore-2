import pm4py
# from l3s_offshore_2.api.test import ns_sim
from l3s_offshore_2.petri_net_sim.simplepn import SimplePN, SimpleSimulator



def simple_sim_run(pnml_path):
    pn, im, fm = pm4py.read_pnml(file_path=pnml_path)
            
    simple_pn = SimplePN.convert_to_simple_pn(pn=pn, initial_marking=im)
    
    sim = SimpleSimulator(net=simple_pn, initial_marking=im)
    
    sim.run()
    
    simulation_results = {
        "firing_seq" : sim.get_firing_sequence(),
        "detailed_log": sim.detailed_log
    }
    return simulation_results