from copy import deepcopy
from typing import Set
import simpy
from gspn4py.core.simulator import BaseSimulator
from gspn4py.core.models.timed import TimedPetriNet

class TimedSimulator(BaseSimulator):
    
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
                enabled_transitions.add(t)
        return enabled_transitions
    
    
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
                    for t in enabled_ts:
                        if not t.is_enabled():
                            print(f"{t} is disabled.")
                            enabled_ts.remove(t)
                            
                        if len(enabled_ts) <= 0:
                            break
                    
                    if len(enabled_ts) <= 0:
                        continue
                                
                    ## handle the priority
                    if len(set(self.net.get_list_of_priorities())) > 1:
                        prior = min(set(self.net.get_list_of_priorities()))
                        for ets in enabled_ts:
                            if ets.priority > prior:
                                enabled_ts.remove(ets)
                    
                    ## randomly select one enabled transition to fire
                    transition_to_fire: TimedPetriNet.Transition = self._random_pop_n(s=enabled_ts, n=1)[0]
                    print(f"Number of enabled ts: {len(enabled_ts)}")
                    print(f"duration: {transition_to_fire.duration}")
                    
                    self.__fire(transition_to_fire=transition_to_fire)
                    
                    timeout.append(transition_to_fire.duration)
                    
                            
                print(f"timeout: {timeout}")
                yield self.env.timeout(max(timeout))
            
            
            
            
            
    
    def __fire(self, transition_to_fire: TimedPetriNet.Transition):
        '''
        fire a timed transition
        
        Support:
            - timed transition
            - priority
        '''
            
        if transition_to_fire:
            ## choose one enabled transition randomly
            
            # print(f"Transition to fire: {transition_to_fire}")
            
            token_pool = set() # place holder for tokens
            
            ## remove tokens from the input places
            for in_arc in transition_to_fire.in_arcs:
                # print(f"Input arc: {in_arc}")
                
                input_place: TimedPetriNet.Place = in_arc.source
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
                output_place: TimedPetriNet.Place = out_arc.target
                # print(f"Output Place: {output_place}, {output_place.num_of_tokens}")
                # print(f"Output arc weight: {out_arc.weight}")
                
                if out_arc.weight <= len(token_pool): # token pool has enough tokens
                    # print(f"Token pool has enough tokens ...")
                    tokens_to_add = self._random_pop_n(s=token_pool, n=out_arc.weight)
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
                        tok = TimedPetriNet.Token(created=(transition_to_fire.transition_id, self.env.now))
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
        # yield self.env.timeout(transition_to_fire.duration)
        return

    
    def get_sim_results(self):
        '''
        get the results of simulation
        '''
        results = {"net_id": self.net.net_id,
                   "initial_marking": self.net.initial_marking,
                   "final_marking": self.net.final_marking,
                   "firing_sequence": [{t.name: t.fired_at} for t in self.net.transitions],
                   "stop_at": self.env.now
                   }
        return results
    
    
    def run(self, until=None):
        """Run the simulation using the internal environment."""
        self.reset()
        self.env.process(self.simulate()) # type: ignore
        self.env.run(until=until)