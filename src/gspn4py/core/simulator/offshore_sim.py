from copy import deepcopy
from typing import Set
import simpy
import numpy as np

from gspn4py.core.simulator import TimedSimulator
from gspn4py.core.models.timed import TimedPetriNet
from datetime import datetime, timedelta
from dateutil import parser

from pprint import pprint


class OffshoreSimulator(TimedSimulator):
    
    def __init__(self, timed_petri_net: TimedPetriNet, properties=None):
        super().__init__(timed_petri_net, properties)
        
        self._template_net = deepcopy(timed_petri_net)
        self.reset()
        
    
    def reset(self):
        '''
        Restore net and env to their initial state.
        '''
        
        self.net = deepcopy(self._template_net)
        self.env = simpy.Environment()
        self.end_event = self.env.event()    
        self.firing_sequences = []
    
    
    def get_enabled_transitions(self) -> Set[TimedPetriNet.Transition]:
        '''
        Get the set of enabled transitions
        Source: 
        
        Return the name of enabled transitions as a list
        '''
        enabled_transitions = set()
        # print(type(self.net))
        
        for t in self.net.transitions:
            # print(type(t))
            if t.is_enabled():
                
                # additional enabling rules
                if t.name == "t_JD0": 
                    # t_JD0 can only be enbaled when:
                    # 1. the vessel current_storage is larger than 0
                    # 2. the vessel to_do is smaller than times fired of t_C
                    vessel = self.net.get_tokens_by_property(property_name="type", property_value="Vessel")[0]
                    # print(f"\n***** vessel properties: {vessel.properties} *****\n")
                    if vessel.properties["current_storage"] > 0:
                        # print(f"t_C times fired: {self.net.get_transition_by_name(name='t_C').times_fired}")
                        if vessel.properties["num_to_do"] > self.net.get_transition_by_name(name='t_C').times_fired:
                            enabled_transitions.add(t)
                if t.name == "t_SB":
                    p_iv = self.net.get_place(place_name="P_IV")
                    p_bp = self.net.get_place(place_name="P_BP")
                    if p_iv.num_of_tokens < p_bp.properties["num_loading_bay"]:
                        enabled_transitions.add(t)
                
                elif t.name == "t_Load":
                    # t_load can only be enbaled when the num of to be loaded OWTs does not exit the vessel capacity
                    
                    num_owt_to_load = self.net.get_arc(source_name="P_BP", target_name="t_Load").weight
                    
                    vessels = list(self.net.get_place(place_name="P_IV").tokens)
                    
                    # if there is at least one vessel can load num_owt_to_load
                    for i in range(len(vessels)):
                        
                        num_owt_loaded = int(vessels[i].properties["current_storage"])
                        v_capacity = int(vessels[i].properties["capacity"])
                        max_num_owt_allowed = v_capacity - num_owt_loaded
                        
                        if num_owt_to_load <= max_num_owt_allowed:
                            enabled_transitions.add(t)
                else:
                    enabled_transitions.add(t)
        return enabled_transitions
    
    
    
    def _fire_t_load(self, ts_to_fire:TimedPetriNet.Transition):
        """
        firing of transition t_Load
        """
        
        ## handle input arcs
        # get num_owts to load
        for arc in ts_to_fire.in_arcs:
            if arc.source.name == "P_BP":
                num_owts = arc.weight
                popped_tokens = arc.source.remove_tokens(n=arc.weight)
            
            if arc.source.name == "P_IV":
                vessel = arc.source.remove_tokens(n=arc.weight).pop()
            
        # update the num_owt_loaded
        if vessel.properties["type"] == "Vessel":
            vessel.properties["current_storage"] =  vessel.properties["current_storage"] + num_owts
        else:
            raise ValueError("Not a vessel")
        
        # add popped_tokens to token_pool
        print(f"popped_tokens: {len(popped_tokens)}")
        for t in popped_tokens:
            self.net.token_pool.add(t)
            
        
        # handle output arc
        for arc in ts_to_fire.out_arcs:
            vessel.consumed = (ts_to_fire.transition_id, self.env.now)
            arc.target.add_tokens(set([vessel]))
        
        
        # print(vessel)
        # print(self.net.token_pool)    
        return
    
    def _fire_transitions(self, ts_to_fire:TimedPetriNet.Transition):
        """
        firing of transitions: t_SF, t_R, t_JU, t_JD1
        """
        
        if len(ts_to_fire.in_arcs) > 1:
            raise ValueError(f"More than one input arc detected at {ts_to_fire.name}")
        
        in_arc = list(ts_to_fire.in_arcs)[0]
        vessel = in_arc.source.remove_tokens(n=in_arc.weight).pop()
        
        
        if len(ts_to_fire.out_arcs) > 1:
            raise ValueError(f"More than one output arc detected at {ts_to_fire.name}")
        
        out_arc = list(ts_to_fire.out_arcs)[0]
        
        vessel.consumed = (ts_to_fire.transition_id, self.env.now)
        out_arc.target.add_tokens(set([vessel]))
            
    
    
    def _fire_t_construction(self, ts_to_fire:TimedPetriNet.Transition):
        """
        firing of transition t_C
        """
        # remove token from input: P_C
        if len(ts_to_fire.in_arcs) > 1:
            raise ValueError(f"More than one input arc detected at {ts_to_fire.name}")
        
        in_arc = list(ts_to_fire.in_arcs)[0]
        vessel = in_arc.source.remove_tokens(n=in_arc.weight).pop()
        
        
        for out_arc in ts_to_fire.out_arcs:
            if out_arc.target.name == "P_OWF":
                if vessel.properties["current_storage"] >= out_arc.weight:
                    for _ in range(out_arc.weight):
                        owt = self.net.token_pool.pop()
                        out_arc.target.add_tokens(set([owt]))
                    
                    vessel.properties["current_storage"] -= 1
    
            if out_arc.target.name == "P_JD":
                vessel.consumed = (ts_to_fire.transition_id, self.env.now)
                out_arc.target.add_tokens(set([vessel]))
        
        
    def _fire_t_jackdown_0(self, ts_to_fire:TimedPetriNet.Transition):
        """
        firing of transition t_JD0
        """
        
        if len(ts_to_fire.in_arcs) > 1:
            raise ValueError(f"More than one input arc detected at {ts_to_fire.name}")
        in_arc = list(ts_to_fire.in_arcs)[0]
        vessel = in_arc.source.tokens.pop()
        
        
        if len(ts_to_fire.out_arcs) > 1:
            raise ValueError(f"More than one output arc detected at {ts_to_fire.name}")
        
        out_arc = list(ts_to_fire.out_arcs)[0]
        vessel.consumed = (ts_to_fire.transition_id, self.env.now)
        out_arc.target.add_tokens(set([vessel]))
        
    
    def _fire_t_sailback(self, ts_to_fire:TimedPetriNet.Transition):
        """
        firing of transition t_SB
        """
        
        if len(ts_to_fire.in_arcs) > 1:
            raise ValueError(f"More than one input arc detected at {ts_to_fire.name}")
        in_arc = list(ts_to_fire.in_arcs)[0]
        vessel = in_arc.source.tokens.pop()
        
        
        if len(ts_to_fire.out_arcs) > 1:
            raise ValueError(f"More than one output arc detected at {ts_to_fire.name}")
        
        out_arc = list(ts_to_fire.out_arcs)[0]
        vessel.consumed = (ts_to_fire.transition_id, self.env.now)
        out_arc.target.add_tokens(set([vessel]))
        
    
    def __fire(self, transition_to_fire: TimedPetriNet.Transition):
        '''
        fire a timed transition
        
        Support:
            - timed transition
            - priority
        '''
        
        
        if not transition_to_fire:
            raise ValueError("Empty transition passed in.")
            ## choose one enabled transition randomly
            
        print(f"Transition to fire: {transition_to_fire.label}")
        # token_pool = set() # place holder for tokens
        
        if transition_to_fire.name == "t_Load":
            self._fire_t_load(ts_to_fire=transition_to_fire)
            # print(f"processed {transition_to_fire.name}")
        
        if transition_to_fire.name == "t_C":
            self._fire_t_construction(ts_to_fire=transition_to_fire)
            # print(f"processed {transition_to_fire.name}")
        
        
        if transition_to_fire.name == "t_JD0":
            self._fire_t_jackdown_0(ts_to_fire=transition_to_fire)
            # print(f"processed {transition_to_fire.name}")
        
        
        if transition_to_fire.name == "t_SB":
            self._fire_t_sailback(ts_to_fire=transition_to_fire)
            # print(f"processed {transition_to_fire.name}")
        
        
        if transition_to_fire.name in {"t_SF", "t_R", "t_JU", "t_JD1"}:
            self._fire_transitions(ts_to_fire=transition_to_fire)
            # print(f"processed {transition_to_fire.name}")
        return
    
        ## remove tokens from the input places
        for in_arc in transition_to_fire.in_arcs:
            # print(f"Input arc: {in_arc}")
            
            input_place: TimedPetriNet.Place = in_arc.source
            # print(f"Input Place: {input_place}")
            # print(f"weight: {in_arc.weight}")
            # print(f"Num of tokens: {input_place.num_of_tokens}")
            
            popped_tokens = input_place.remove_tokens(n=in_arc.weight)
            # print(f"Tokens popped: {popped_tokens}")
            
            if input_place.name == 'P_BP':
                
                # update num_owt_loaded to vessel
                vessel = self.net.get_tokens_by_property(property_name="type", property_value="Vessel")[0]
                vessel.properties["num_owt_loaded"] += len(popped_tokens)
                print(vessel)
                
                # add these tokens to net.token_pool
                for t in popped_tokens:
                    self.net.token_pool.add(t)
                
            else:
                self.net.token_pool.update(popped_tokens)
                # print(f"Token pool: {token_pool}")
                # print(f"Input Place: {input_place}, {input_place.num_of_tokens}")
        
        
        ## add tokens
        # print(f"\nadd tokens to output place\n")
        for out_arc in transition_to_fire.out_arcs:
            output_place: TimedPetriNet.Place = out_arc.target
            # print(f"Output Place: {output_place}, {output_place.num_of_tokens}")
            # print(f"Output arc weight: {out_arc.weight}")
            
            if out_arc.weight <= len(self.net.token_pool): # token pool has enough tokens
                # print(f"Token pool has enough tokens ...")
                tokens_to_add = self._random_pop_n(s=self.net.token_pool, n=out_arc.weight)
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
                num_toks_to_create = out_arc.weight - len(self.net.token_pool)
                # print(f"Need to create {num_toks_to_create} tokens")
                
                
                tokens_to_add = set()
                while self.net.token_pool:
                    tokens_to_add.add(self.net.token_pool.pop())
                
                
                for _ in range(num_toks_to_create):
                    tok = TimedPetriNet.Token(created=(transition_to_fire.transition_id, self.env.now))
                    tokens_to_add.add(tok)
                    transition_to_fire.update_created_tokens({tok})
                
                # print(f"Tokens to add: {tokens_to_add}")
                
                # update token consumption information
                for tok in tokens_to_add:
                    tok.consumed = (transition_to_fire.transition_id, self.env.now)
                    # print(f"Token {tok} consume info: {tok.consumed}")
                    ## everytime t_C fires, consumes a loaded OWT
                    if transition_to_fire.name == "t_C":
                        tok.properties["num_owt_loaded"] -= 1
                        # print(f"num_of_owt_loaded: {tok.properties.get["num_owt_loaded"]}")
                
                # add tokens to the output place
                output_place.add_tokens(tokens=tokens_to_add)
                # print(f"Output place: {output_place}, {output_place.num_of_tokens}")
                
                
        ## update the transition
        # print(f"Update transition: {transition_to_fire}")
        ### add remaining tokens as absorbed
        if len(self.net.token_pool) > 0:
            # print("Tokens are absorbed...")
            transition_to_fire.update_absorbed_tokens(self.net.token_pool)
            # print(f"{transition_to_fire}: {transition_to_fire.absorbed_tokens}")
        
        ### update times fired
        transition_to_fire.update_times_fired()
        # print(f"{transition_to_fire}: {transition_to_fire.times_fired}")
        
        ### update firing at
        transition_to_fire.update_fired_at(fired_at=self.env.now)
        # print(f"{transition_to_fire}: {transition_to_fire.fired_at}")
        
        
    
        # print(self.net.get_current_marking_obj())
        # yield self.env.timeout(transition_to_fire.duration)
        return

    
    def get_sim_results(self):
        '''
        get the results of simulation
        '''
        
        # operation_mapping = {
        #     "Install": 0,
        #     "SailingBack": 1,
        #     "SailingForth": 2,
        #     "LoadingOWT": 3
        # }
        
        results = {"net_id": self.net.net_id,
                   "initial_marking": self.net.initial_marking,
                   "final_marking": self.net.final_marking,
                   "firing_sequence": [{t.label: t.fired_at} for t in self.net.transitions],
                   "end_at": self.env.now
                   }
        return results
    
    
    def run(self, until=None):
        """Run the simulation using the internal environment."""
        self.reset()
        self.env.process(self.simulate()) # type: ignore
        self.env.run(until=until)
    
    
    
    # def calc_opt_schedule_in_horizon(self):
    #     ''''''
    #     horizon = self.properties.get("pn_maxWaitTime")
        
    #     for h in range(horizon):
    #         current_date = parser.parse(start_date) + timedelta(hours=h)
            
    #     pass
    
    
    @staticmethod
    def stopper(env, stop_event):
        yield env.timeout(10000)
        print(f"Stopping simulation at time {env.now}")
        stop_event.succeed()  # This will trigger the event
    
    
    def evaluate_simulation_results(self):
        """
        evaluate the plan yielded by simulation
        """
        
        # fetch the unit cost
        cost_offshore = self.properties["cost_offshore"][0]
        cost_portOP = self.properties["cost_portOp"]
        cost_owtFinished = self.properties["cost_benefitForFinishingAnOWT"]
        cost_waiting = self.properties["cost_waitingPenalty"]
        
        operation_cost = {
            'LoadingOWT': -cost_portOP,
            'SailingForth': -cost_offshore,
            'SailingBack': -cost_offshore,
            'Construction': -cost_offshore,
            'JackUp': -cost_offshore,
            'JackDown': -cost_offshore,
            'Reposition': -cost_offshore,
        }
        
        # pprint(operation_cost)
        
        # initialize cost
        cost = 0
        for op in self.firing_sequences:
            # op = (op_name, op_duration, op_delay, op_start, op_end)
            op_cost = int(operation_cost[op[0]]) * int(op[1]) + int(cost_waiting) * int(op[2])
            cost = cost + op_cost
        
        # print(f"number of owts finished: {self.net.get_place(place_name='P_OWF').num_of_tokens}")
        cost = cost + int(self.net.get_place(place_name='P_OWF').num_of_tokens) * cost_owtFinished
        
        # print(f"cost: {cost}")
        return cost
        
    
    def get_expected_duration_of_installation_cycle(self, n_load:int, n_build:int) -> int:
        """
        get the expected duration of installation cycle
        """
        # get the expected duration of each transition
        expected_duration = 0
        for t in self.net.transitions:
            if t.label == "LoadingOWT":
                expected_duration += t.duration * n_load
            elif t.label in ["Reposition", "JackUp", "Construction", "JackDown"]:
                expected_duration += t.duration * n_build
            elif t.label in ["SailingForth", "SailingBack"]:
                expected_duration += t.duration
                        
        return expected_duration
    
    
    def calc_opt_installation_cycle_multi_vessels_from_current(self):
        """calculate optimal installation cycle for multi vessel immedieate from current"""    
        pass
        
    
    def calc_opt_schedule_single_vessel_to_horizon(self):
        """calculate optimal schedule for single vessel until horizon"""
        horizon = int(self.properties["optim_stepWidth"]) * int(self.properties["optim_planningHorizons"])
        self.properties["stop_at"] = horizon
        
        # max_wait_time = self.properties["pn_maxWaitTime"]
        
        results = {
            "owts_finished": 0,
            "plan_cost": 0,
            "end_at": 0,
            "plan": []
        }
        
        while horizon > 0:
            print(f"\nCurrent date: {self.properties['state_currentDate']}")
            # calculate the optimal installation cycle start from currentDate
            sim_results = self.calc_opt_install_cycle_single_vessel_single()
            print(f"\n**Simulation results:")
            print(sim_results)
            
            print(f"End at: {sim_results['end_at']}")
            # update results
            results["owts_finished"] += sim_results["owts_finished"]
            results["plan_cost"] += sim_results["plan_cost"]
            
            if sim_results.get("end_at") is not None:
                results["end_at"] += sim_results["end_at"]
            
            if sim_results.get("plan") is not None:
                results["plan"].extend(sim_results["plan"])
            
            
            # update the current date for next installation cycle
            current_date = parser.parse(self.properties["state_currentDate"]) + timedelta(hours=sim_results["end_at"])
            self.properties["state_currentDate"] = current_date.strftime("%d-%b-%Y-%H")
            
            horizon = horizon - sim_results["end_at"]
            
            
        return results
        
    
    def calc_opt_install_cycle_single_vessel_single(self):
        """calculate optimal installation cycle for single vessel"""
        
        # assign vessel capacity to token
        vessel_capacity = self.properties["vessel_capacity"][0]
        vessel_storage = self.properties["state_vessel_currentStorage"][0]
        
        sim_results = None
        if self.properties.get("stop_at") == None:
            self.properties["stop_at"] = 8760 # one year 365*24
        
        
        # print(f"Vessel Capacity: {vessel_capacity}")
        # print(f"Vessel Current Storage: {vessel_storage}")
        
        
        cost = 0
        for n_owts in list(i+1 for i in range(vessel_capacity - vessel_storage)):
            for to_do in list(i+1 for i in range(n_owts + vessel_storage)):
                
                # check if the remining time is enough for the installation cycle
                expected_duration = self.get_expected_duration_of_installation_cycle(n_load=n_owts, n_build=to_do)
                if expected_duration > self.properties["stop_at"]:
                    print(f"Expected duration {expected_duration} is larger than stop_at {self.properties['stop_at']}.")
                    continue
                
                print(f"\n\n*******Load: {n_owts}, and Build: {to_do}*******\n\n")
                # update the number of owts to be loaded
                self.properties["num_owts_to_load"] = n_owts
                self.properties["num_to_do"] = to_do

                self.run_installation_cycle()
                
                r = self.get_sim_results()

                # pprint(f"firing_sequences: {self.firing_sequences}")
                # pprint(f"Simulation Result: {r}")
                
                plan_cost = self.evaluate_simulation_results()
                # print(f"Cost of the schedule: {plan_cost}")
            # print(f"********\nProcess stoped at: {r['stop_at']}\n********")
            # # update the simulation result if a shorter schedule is found
            
            # check if the estimated duration is valid
            if r["end_at"] > self.properties["stop_at"]:
                print(f"Estimated duration {r['end_at']} is larger than stop_at {self.properties['stop_at']}.")
                continue
            
            
            print(f"Estimated duration {r['end_at']} is smaller than stop_at {self.properties['stop_at']}.")
            if  cost < plan_cost:
                cost = plan_cost
                sim_results = {
                    "owts_finished": to_do,
                    "plan_cost": cost,
                    "end_at": r["end_at"],
                    "plan": self.firing_sequences
                }
                
        return sim_results

        
    
    
    def run_installation_cycle(self):
        """simulation single installation cycle."""
        self.reset()
        self.initialize() # initialize the net and update the parameters
        self.env.process(self.stopper(self.env, self.end_event))
        self.env.process(self.simulate_installation_cycle()) # type: ignore
        self.env.run(until=self.end_event)
    
    
    def initialize(self):
        """
        initialize the model and environment
        """
        # get the current state
        # current_date = self.properties["state_currentDate"]
        
        
        
        # update weight for arc (P_BP -> t_Load)
        num_owts_to_load = self.properties["num_owts_to_load"]
        self.net.get_arc(source_name="P_BP", target_name="t_Load").weight = num_owts_to_load
        
        # update number of tokens in P_BP
        num_owts_in_base_port = self.properties["state_basePort_currentStorage"]
        self.net.get_place(place_name="P_BP").set_tokens(n=num_owts_in_base_port,
                                                   created_by='init', 
                                                   created_at=self.env.now,
                                                   type='OWT')
        
        # set P_BP capacity
        num_loading_bay = self.properties["basePort_storageCapacity"]
        self.net.get_place(place_name="P_BP").properties["num_loading_bay"] = num_loading_bay
        
        
        # update owt number of OWT already built
        num_owts_build = self.properties["state_currentlyBuiltOWTs"]
        self.net.get_place(place_name="P_OWF").set_tokens(n=num_owts_build,
                                                          created_by='init',
                                                          created_at=self.env.now,
                                                          type='OWT'
                                                        )
        
        
        # update number of vessels in P_IV
        num_installation_vessel = 1#self.properties["vessel_numInstallationVessels"]
        self.net.get_place(place_name="P_IV").set_tokens(n=num_installation_vessel,
                                                         created_by='init',
                                                         created_at=self.env.now,
                                                         type="Vessel")
        
        
        # assign vessel capacity
        vessel_capacity = self.properties["vessel_capacity"]
        current_storage = self.properties["state_vessel_currentStorage"]
        num_to_do = self.properties["num_to_do"]
        vessels = self.net.get_tokens_by_property(property_name="type", property_value="Vessel")
        for i in range(len(vessels)):
            vessels[i].properties["vessel_idx"] = int(i)
            vessels[i].properties["capacity"] = int(vessel_capacity[i])
            vessels[i].properties["current_storage"] = int(current_storage[i])
            vessels[i].properties["num_to_do"] = int(num_to_do)
        
        # initialize token_pool
        for _ in range(current_storage[0]):
            tok = TimedPetriNet.Token(created=('init', self.env.now), properties={"type": 'OWT'})
            self.net.token_pool.add(tok)
        
        # set initial marking
        self.net.initial_marking = self.net.get_current_marking_obj()    
    
    
        
    def simulate_installation_cycle(self):
        '''
        Simulate installation cycle
        
        choose a random enabled transiton and fire
        
        Support:
            - immediate transition
            - incremental firing sequence
            - priority
            
        '''
        
        while True:            
            ## get the enabled transitions
            enabled_ts: Set[TimedPetriNet.Transition] = self.get_enabled_transitions()
            
            if len(enabled_ts) <= 0:
                # If no transitions can fire, stop the simulation
                print("No transitions can fire. Stopping simulation.")
                        
                ## update the final marking
                self.net.final_marking = self.net.get_current_marking_obj()
                self.stop_at = self.env.now
                break
            
            else:
                timeout = [0]
                while len(enabled_ts) > 0:
                    print(f"Number of enabled ts: {len(enabled_ts)}")
                    
                    ## check the validity
                    invalid_ts = set()
                    for t in enabled_ts:
                        if not t.is_enabled():
                            print(f"{t} is disabled.")
                            invalid_ts.add(t)
                        
                        if t.name == 't_JD0':
                            vessel = self.net.get_tokens_by_property(property_name="type", property_value="Vessel")[0]
                            # print(f"vessel properties: {vessel.properties}")
                            # print(f"OWTs finished: {self.net.get_transition_by_name(name='t_C').times_fired}")
                            if self.net.get_transition_by_name(name='t_C').times_fired >= vessel.properties["num_to_do"]:
                                print(f"{t} is disabled.")
                                invalid_ts.add(t)
                        
                        if t.name == 't_JD1':
                            vessel = self.net.get_tokens_by_property(property_name="type", property_value="Vessel")[0]
                            if vessel.properties["current_storage"] > 0: # storage available
                                if self.net.get_transition_by_name(name='t_C').times_fired < vessel.properties["num_to_do"]: # the goal for the installation cycle is not reached
                                    print(f"{t} is disabled.")
                                    invalid_ts.add(t)
                         
                        # if len(enabled_ts) <= 0:
                        #     break
                    
                    enabled_ts = enabled_ts - invalid_ts
                    
                    if len(enabled_ts) <= 0:
                        continue
                                
                   
                    ## randomly select one enabled transition to fire
                    transition_to_fire: TimedPetriNet.Transition = self._sample_enabled_transition(enabled_ts=enabled_ts, n=1)[0]
                    # print(f"Number of enabled ts: {len(enabled_ts)}")
                    # print(f"duration: {transition_to_fire.duration}")
                    
                    ## estimate the fire duration
                    from gspn4py.offshoreplan.offshore_utils import get_operation_duration_markov
                    current_date = parser.parse(self.properties["state_currentDate"]) + timedelta(hours=self.env.now)
                    # print(f"current_date: {current_date}")
                    # print(f"current_date_year: {current_date.year}")
                    
                    if transition_to_fire.name == "t_Load":
                        weight = self.net.get_arc(source_name="P_BP",target_name="t_Load").weight
                        job_duration = transition_to_fire.duration * weight
                    else:
                        job_duration = transition_to_fire.duration
                    # print(f"job_duration: {job_duration}")
                    
                    job_requirements = np.column_stack([transition_to_fire.properties["wind_limit"], transition_to_fire.properties["wave_limit"]])
                    # print(f"job_requirements: {job_requirements}")
                    
                    estimated_duration = get_operation_duration_markov(current_date=current_date, job_duration=[job_duration], job_requirements=job_requirements)
                    print(f"estimated_duration: {estimated_duration}")
                    
                    # fire transition
                    self.__fire(transition_to_fire=transition_to_fire)
                    
                    timeout.append(estimated_duration)
                    
                    ### update times fired
                    transition_to_fire.update_times_fired()
                    ### update firing at
                    transition_to_fire.update_fired_at(fired_at=self.env.now)
                    
                    op_name = transition_to_fire.label
                    op_duration = job_duration
                    op_delay = estimated_duration - job_duration
                    
                    # fmt = "%d-%b-%Y-%H"
                    scenario_startdate = parser.parse(self.properties["scenario_simulationStartDate"])
                    ic_startdate = parser.parse(self.properties["state_currentDate"])
        
                    dt = int((ic_startdate - scenario_startdate).total_seconds() / 3600)
                    op_start = dt + self.env.now
                    op_end = op_start + estimated_duration
                    
                    self.firing_sequences.append((op_name,      # op_name 
                                                  op_duration,  # op_duration
                                                  op_delay,     # op_delay 
                                                  op_start,     # op_start
                                                  op_end        # op_end
                                                ))
                    
                print(f"timeout: {max(timeout)}")
                yield self.env.timeout(max(timeout))
                           
                
                    
            # Termination 1: installation cycle finished
            if self.net.get_transition_by_name(name="t_SB").times_fired >= 1:
                print(f"Number of times fired of t_SB: {self.net.get_transition_by_name(name='t_SB').times_fired}")
                self.net.final_marking = self.net.get_current_marking_obj()
                print(f"\n\n***** Terminating simulation - Termination Model 1 ******")
                print(f"*******Terminate after {transition_to_fire.name}*******")
                print(f"******** Installation Cycle finished. **********\n\n")
                self.end_event.succeed()
                break
        
            # Termination 2: maximum time span for planing reached
            if self.env.now >= self.properties["stop_at"]:
                print(f"\n\n***** Terminating simulation - Termination Model 2 ******")
                print(f"**** Simulation reached maximum time span ****\n\n")
                self.end_event.succeed()
        
                    

                
    # def calc_opt_schdule_immediate_from_current(self):
    #     """Calculate optimal schedule immediate from current"""
        
    #     vessel_capacity = self.properties["vessel_capacity"][0]
        
    #     # self.net.get_place(name="P_BP").set_tokens(num_tokens=32)
        
    #     stop_at = 10000000
    #     sim_results = None
        
    #     for n in list(i+1 for i in range(vessel_capacity)):
    #         self.net.set_weight_to_arc(source_name="P_BP", target_name="t_Load", weight=2)
    #         self.run_installation_cycle()
    #         r = self.get_sim_results()
    #         if r["stop_at"] < stop_at:
    #             stop_at = r["stop_at"]
    #             sim_results = r
    #     return sim_results
    
    
    