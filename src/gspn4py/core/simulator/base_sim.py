import numpy as np
import simpy
import random, secrets
from dataclasses import dataclass
from typing import Dict, List, Any, Set
from collections import defaultdict
from gspn4py.core.models.base import BasePetriNet
from gspn4py.core.simulator.firing import PetriNetFiring, FiringEvent
from gspn4py.core.simulator.options import GlobalOptions  # Changed import path
from copy import deepcopy

from pm4py import Marking

# @dataclass
# class SimulationState:
#     current_time: float = 0.0
#     marking: np.ndarray = 
#     virtual_marking: np.ndarray = None
#     enabled_transitions: List[bool] = None
#     firing_transitions: List[bool] = None
#     state_number: int = 0



class BaseSimulator(object):
    def __init__(self, base_petri_net: BasePetriNet, properties:None):
        self._template_net = deepcopy(base_petri_net)
        self.__properties = dict() if properties is not None else properties
        self.reset()
        
    def __get_properties(self):
        return self.__properties
    
    properties = property(__get_properties)
    
    def reset(self):
        '''
        Restore net and env to their initial state.
        '''
        self.net = deepcopy(self._template_net)
        self.env = simpy.Environment()
    
    @staticmethod
    def _random_pop_n(s: set, n: int):
        if n > len(s):
            raise ValueError("Cannot pop more elements than are in the set")
        
        # Convert to a tuple (or list) for sampling
        sampled = random.sample(tuple(s), n)
        
        # remove elem from the set
        for elem in sampled:
            s.remove(elem)
            
        return sampled
    
    
    def simulate(self):
        '''
        Simulate the BasePetriNet
        
        choose a random enabled transiton and fire
        
        Support:
            - immediate transition
            - incremental firing sequence
            - priority
            
        '''
        # set initial marking
        self.net.initial_marking = self.net.get_current_marking_obj()
        
        
        while True:
            # print(f"\nSimulation Time: {self.env.now}\n")
            
            ## get the enabled transitions
            enabled_ts = self.get_enabled_transitions()
            # print(f"Enabled Transitions: {enabled_ts}")
            

            if enabled_ts: # if there are enabled transitions
                ## handle the priority
                if len(set(self.net.get_list_of_priorities())) > 1:
                    prior = min(set(self.net.get_list_of_priorities()))
                    for ets in enabled_ts:
                        if ets.priority > prior:
                            enabled_ts.remove(ets)
                
                
                self.__fire(ts_to_fire=enabled_ts)
            
                yield self.env.timeout(1)
                continue
            
            # If no transitions can fire, stop the simulation
            print("No transitions can fire. Stopping simulation.")
            
            
            ## update the final marking
            self.net.final_marking = self.net.get_current_marking_obj()
            
            break
    
    
    def __fire(self, ts_to_fire: Set[BasePetriNet.Transition]):
        '''
        fire the set of enabled transitions
        '''
        
        def random_pop_n(s: set, n: int):
            if n > len(s):
                raise ValueError("Cannot pop more elements than are in the set")
            
            # Convert to a tuple (or list) for sampling
            sampled = random.sample(tuple(s), n)
            
            # remove elem from the set
            for elem in sampled:
                s.remove(elem)
                
            return sampled
        
            
        while ts_to_fire:
            ## choose one enabled transition randomly
            transition_to_fire: BasePetriNet.Transition = random_pop_n(s=ts_to_fire, n=1)[0]
            # print(f"Transition to fire: {transition_to_fire}")
            
            token_pool = set() # place holder for tokens
            
            ## remove tokens from the input places
            for in_arc in transition_to_fire.in_arcs:
                # print(f"Input arc: {in_arc}")
                
                input_place: BasePetriNet.Place = in_arc.source
                # print(f"Input Place: {input_place}")
                # print(f"weight: {in_arc.weight}")
                # print(f"Num of tokens: {input_place.num_of_tokens}")
                
                popped_tokens = input_place.remove_tokens(n=in_arc.weight)
                # print(f"Tokens popped: {popped_tokens}")
                
                token_pool.update(popped_tokens)
                # print(f"Token pool: {token_pool}")
                # print(f"Input Place: {input_place}, {input_place.num_of_tokens}")
            
            
            ## add tokens
            # print(f"\nadd tokens to output place\n")
            for out_arc in transition_to_fire.out_arcs:
                output_place: BasePetriNet.Place = out_arc.target
                # print(f"Output Place: {output_place}, {output_place.num_of_tokens}")
                # print(f"Output arc weight: {out_arc.weight}")
                
                if out_arc.weight <= len(token_pool): # token pool has enough tokens
                    # print(f"Token pool has enough tokens ...")
                    tokens_to_add = random_pop_n(s=token_pool, n=out_arc.weight)
                    # print(f"Token pool: {token_pool}")
                    # print(f"Tokens to add: {tokens_to_add}")
                    
                    # update token consumption information
                    for tok in tokens_to_add:
                        tok.consumed = (transition_to_fire.transition_id, self.env.now)
                        # print(f"Token {tok} consume info: {tok.consumed}")
                    
                    output_place.add_tokens(set(tokens_to_add))
                    # print(f"Output place: {output_place}, {output_place.num_of_tokens}")
                
                else: # token pool has not enough tokens
                    # print("Token pool has not enough tokens...")
                    # create tokens
                    num_toks_to_create = out_arc.weight - len(token_pool)
                    # print(f"Need to create {num_toks_to_create} tokens")
                    
                    
                    tokens_to_add = set()
                    while token_pool:
                        tokens_to_add.add(token_pool.pop())
                    
                    
                    for _ in range(num_toks_to_create):
                        tok = BasePetriNet.Token(created=(transition_to_fire.transition_id, self.env.now))
                        tokens_to_add.add(tok)
                        transition_to_fire.update_created_tokens({tok})
                    
                    # print(f"Tokens to add: {tokens_to_add}")
                    
                    # update token consumption information
                    for tok in tokens_to_add:
                        tok.consumed = (transition_to_fire.transition_id, self.env.now)
                        # print(f"Token {tok} consume info: {tok.consumed}")
                    
                    # add tokens to the output place
                    output_place.add_tokens(tokens=tokens_to_add)
                    # print(f"Output place: {output_place}, {output_place.num_of_tokens}")
                    
                    
            ## update the transition
            # print(f"Update transition: {transition_to_fire}")
            ### add remaining tokens as absorbed
            if len(token_pool) > 0:
                # print("Tokens are absorbed...")
                transition_to_fire.update_absorbed_tokens(token_pool)
                # print(f"{transition_to_fire}: {transition_to_fire.absorbed_tokens}")
            
            ### update times fired
            transition_to_fire.update_times_fired()
            # print(f"{transition_to_fire}: {transition_to_fire.times_fired}")
            
            ### update firing at
            transition_to_fire.update_fired_at(fired_at=self.env.now)
            # print(f"{transition_to_fire}: {transition_to_fire.fired_at}")
            
        
        # print(self.net.get_current_marking_obj())
        
        return
    
    # def update_sime_time(self) -> None:
    #     self.sim_time += 1
    #     return
        
    def get_enabled_transitions(self) -> Set[BasePetriNet.Transition]:
        '''
        Get the set of enabled transitions
        Source: 
        
        Return the name of enabled transitions as a list
        '''
        enabled_transitions = set()
        
        for t in self.net.transitions:
            if t.is_enabled():
                enabled_transitions.add(t)
        return enabled_transitions
    
    
    def get_firing_sequences(self):
        pass
    
    def get_sim_results(self):
        '''
        get the results of simulation
        '''
        results = {"net_id": self.net.net_id,
                   "intial_marking": self.net.initial_marking,
                   "final_marking": self.net.final_marking,
                   "firing_sequence": [{t.name: t.fired_at} for t in self.net.transitions]}
        return results
    
    
    
    def run(self, until=None):
        """Run the simulation using the internal environment."""
        self.reset()
        self.env.process(self.simulate()) # type: ignore
        self.env.run(until=until)

    
    def montecarlo_simulation(self, num_simulation:int) -> List[Dict]:
        '''
        run Monte Carlo simulation
        '''
        results = []
        for _ in range(num_simulation):
            self.run()
            results.append(self.get_sim_results())
        
        return results            


            

    
    
    

# class SimulationEngine:
#     def __init__(self, petri_net: BasePetriNet):
#         self.net = petri_net
        
#         # Initialize required net attributes with defaults
#         if not hasattr(self.net, 'STOP_TIME'):
#             self.net.STOP_TIME = float('nan')
#         if not hasattr(self.net, 'delta_T'):
#             self.net.delta_T = 1.0
#         if not hasattr(self.net, 'REAL_TIME'):
#             self.net.REAL_TIME = False
#         if not hasattr(self.net, 'initial_marking'):
#             self.net.initial_marking = defaultdict(int)
            
#         self.options = GlobalOptions()
#         self.state = SimulationState()
#         self.firing_manager = PetriNetFiring(petri_net)
#         self.Enabled_Trans_SET = []
#         self.Firing_Trans_SET = []
#         self.LOG = []
#         self.color_map = []
#         self._initialize_simulation_state()

#     def _initialize_simulation_state(self):
#         """Initialize all simulation variables"""
#         sorted_places = sorted(self.net.places, key=lambda x: x.name)
#         sorted_trans = sorted(self.net.transitions, key=lambda x: x.name)
        
#         # Initialize markings
#         self.state.marking = np.array([
#             self.net.initial_marking.get(p, 0) for p in sorted_places
#         ])
#         self.state.virtual_marking = np.zeros(len(sorted_places))
        
#         # Initialize transition states
#         self.state.enabled_transitions = [False] * len(sorted_trans)
#         self.state.firing_transitions = [False] * len(sorted_trans)
        
#         # Record initial state
#         self._record_log_entry()

#     def run(self, max_loops: int = 200) -> Dict[str, Any]:
#         """Main simulation loop"""
#         loop_count = 0
#         while not self._simulation_complete(loop_count, max_loops):
#             if self.net.REAL_TIME:
#                 self.state.current_time = self._current_clock()
            
#             self._update_enabled_transitions()
#             self._log_enabled_transitions()
            
#             if any(self.state.enabled_transitions):
#                 self._start_firing_transitions()
            
#             completed_logs, completed_colors = self.firing_manager.complete_firings()
#             for log in completed_logs:
#                 self._update_state_from_log(log)
#                 self._record_log_entry()
            
#             self._advance_time(len(completed_logs))
#             loop_count += 1
            
#             if self._should_stop_early():
#                 break
        
#         return self._pack_results()

#     def _update_enabled_transitions(self):
#         """Update enabled status for all transitions"""
#         for i in range(len(self.net.transitions)):
#             self.state.enabled_transitions[i] = self._is_transition_enabled(i)

    
#     def _is_transition_enabled(self, trans_idx: int) -> bool:
#         """Check if transition is enabled"""
#         sorted_trans = sorted(self.net.transitions, key=lambda x: x.name)
#         trans = sorted_trans[trans_idx]
        
#         # Check inhibitor arcs if they exist
#         if hasattr(self.net, 'inhibitor_arcs'):
#             for place, weight in self.net.inhibitor_arcs.get(trans, []):
#                 place_idx = self._get_place_index(place)
#                 if self.state.marking[place_idx] >= weight:
#                     return False
        
#         # Check input arcs
#         input_places = [
#             arc.source for arc in getattr(self.net, 'arcs', [])
#             if getattr(arc, 'target', None) == trans and hasattr(arc.source, 'name')
#         ]
#         for place in input_places:
#             place_idx = self._get_place_index(place)
#             if self.state.marking[place_idx] < 1:
#                 return False
        
#         return True

#     def _start_firing_transitions(self):
#         """Start firing all enabled transitions"""
#         for i, enabled in enumerate(self.state.enabled_transitions):
#             if enabled:
#                 event = self.firing_manager.start_firing(i)
#                 if event:
#                     self.state.firing_transitions[i] = True
#         self._log_firing_transitions()

#     def _advance_time(self, num_completions: int):
#         """Time advancement"""
#         if not self.net.REAL_TIME:
#             self.state.current_time += self.net.delta_T
#             self.state.state_number += 1

#     def _update_state_from_log(self, log: Dict):
#         """Update state from completed firing"""
#         self.state.marking = log.get('marking', self.state.marking)
#         self.state.virtual_marking = log.get('virtual_marking', self.state.virtual_marking)
#         self.state.current_time = log.get('end_time', self.state.current_time)
#         self.state.state_number = log.get('state', self.state.state_number)

#     def _record_log_entry(self):
#         """Create log entry"""
#         log_entry = [
#             *self.state.marking.tolist(),
#             0,  # transition
#             self.state.state_number,
#             0,  # prev_state
#             0,  # FTS_index
#             self.state.current_time,
#             self.state.current_time,
#             *self.state.virtual_marking.tolist()
#         ]
#         self.LOG.append(log_entry)

#     def _log_enabled_transitions(self):
#         """Record enabled transitions"""
#         self.Enabled_Trans_SET.append(
#             [self.state.current_time] + self.state.enabled_transitions
#         )

#     def _log_firing_transitions(self):
#         """Record firing transitions"""
#         self.Firing_Trans_SET.append(
#             [self.state.current_time] + self.state.firing_transitions
#         )

#     def _get_place_index(self, place) -> int:
#         """Get index from sorted places list"""
#         return sorted([p.name for p in self.net.places]).index(place.name)

#     def _simulation_complete(self, loop_count: int, max_loops: int) -> bool:
#         """Check simulation completion conditions"""
#         if loop_count >= max_loops:
#             return True
#         if hasattr(self.net, 'STOP_TIME') and not np.isnan(self.net.STOP_TIME):
#             if self.state.current_time >= self.net.STOP_TIME:
#                 return True
#         return False

#     def _should_stop_early(self) -> bool:
#         """Check additional stopping conditions"""
#         return (not any(self.state.enabled_transitions) and 
#                (not hasattr(self.firing_manager, 'events_in_progress') or 
#                not self.firing_manager.events_in_progress))

#     def _pack_results(self) -> Dict[str, Any]:
#         """Package simulation results"""
#         return {
#             'type': 'simulation',
#             'LOG': self.LOG,
#             'Enabled_Transitions': self.Enabled_Trans_SET,
#             'Firing_Transitions': self.Firing_Trans_SET,
#             'color_map': self.color_map,
#             'completion_time': self.state.current_time,
#             'final_marking': self.state.marking,
#             'virtual_marking': self.state.virtual_marking,
#             'state_number': self.state.state_number
#         }

#     def _current_clock(self) -> float:
#         """Get current time for real-time simulations"""
#         return self.state.current_time