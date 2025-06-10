import simpy
import random
from scipy.stats import norm, expon
from collections import OrderedDict, defaultdict

from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to

from copy import deepcopy


class SimpleMarking(Marking):
    def __init__(): super()
        

class SimplePN(PetriNet):
    class SimplePlace(PetriNet.Place):
        def __init__(self, name, in_arcs=None, out_arcs=None, properties=None, ntokens:int=None):
            super().__init__(name, in_arcs=in_arcs, out_arcs=out_arcs, properties=properties)
            self.__ntokens = 0 if ntokens is None else ntokens
        
        def __repr__(self):
            return super().__repr__()
    
    class SimpleTransition(PetriNet.Transition):
        def __init__(self, name, label=None, in_arcs=None, out_arcs=None, properties=None, priority=None): 
            super().__init__(name, label=label, in_arcs=in_arcs, out_arcs=out_arcs, properties=properties)
            self.__priority = 1 if priority is None else priority
        
        def __get_priority(self):
            pass
        
        def __set_priority(self):
            pass
        
        priority = property(__get_priority, __set_priority)
    
    
    class SimpleArc(PetriNet.Arc):
        def __init__(self, source, target, weight=1, properties=None):
            super().__init__(source, target, weight=weight, properties=properties)
    
    
    def __init__(self, name=None, places=None, transitions=None, arcs=None, properties=None, initial_marking=None):
        super().__init__(name=name, places=places, transitions=transitions, arcs=arcs, properties=properties)
        
        self.__initial_marking = None if initial_marking is None else initial_marking
    
    def __get_initial_marking(self):
        return self.__get_initial_marking
    
    def __set_initial_marking(self, initial_marking: Marking):
        self.__initial_marking = initial_marking
    
    initial_marking = property(__get_initial_marking, __set_initial_marking)
    
    
    @classmethod
    def convert_to_simple_pn(cls, pn: PetriNet, initial_marking: Marking = None) -> "SimplePN":
        # Instantiate your subclass
        new_net = cls()
        new_net.name = pn.name

         # 2. Copy places
        place_map = {}
        for p in pn.places:
            p2 = SimplePN.SimplePlace(name=p.name,
                                      properties=dict(p.properties))
            new_net.places.add(p2)
            place_map[p] = p2
            
         # 3. Copy transitions
        trans_map = {}
        for t in pn.transitions:
            t2 = SimplePN.SimpleTransition(
                name=t.name,
                label=t.label,
                in_arcs=t.in_arcs,
                out_arcs=t.out_arcs,
                properties=dict(t.properties),
                priority=1
            )
            new_net.transitions.add(t2)
            trans_map[t] = t2
        
        # 4. Copy arcs (preserving weights & properties)
        for arc in pn.arcs:
            src = place_map.get(arc.source) or trans_map[arc.source]
            tgt = place_map.get(arc.target) or trans_map[arc.target]
            a2 = SimplePN.SimpleArc(
                source=src,
                target=tgt,
                weight=arc.weight,
                properties=dict(arc.properties)
            )
            new_net.arcs.add(a2)
        
        
        # 5. (Optional) attach the same initial/final marking
        if initial_marking is not None:
            new_net.initial_marking = {
                place_map[p]: cnt for p, cnt in initial_marking.items()
            }

        # Copy over any extra properties dict
        new_net.properties.update(pn.properties)
        return new_net
    
    
    def get_transition_names(self):
        return [t.name for t in self.transitions]
    
    def get_transition_labels(self):
        return [t.label for t in self.transitions]
    
    
    def get_transition_by_name(self, t_name):
        
        for t in self.transitions:
            if t_name == t.name:
                return t
        
    def get_transition_by_label(self, t_label):
        
        for t in self.transitions:
            if t_label == t.label:
                return t
            
    def get_place_names(self):
        return [p.name for p in self.places]
    
    
    def get_place_by_name(self, p_name):
        
        for p in self.places:
            if p_name == p.name:
                return p
            





class SimpleSimulator:
    def __init__(self, net: SimplePN, initial_marking: SimpleMarking, env: simpy.Environment = None):
        """
        Initialize the simulator from a PM4Py PetriNet and its initial marking.
        
        """
        # 1. Simulation environment
        self.env = env or simpy.Environment()  # type simpy.Environment contentReference[oaicite:5]{index=5}
        
        self.net = net
        
        # 2. Place‐token mapping (copy from Marking dict)
        #    Marking is a dict Place→int in PM4Py :contentReference[oaicite:6]{index=6}
        self.initial_marking = initial_marking
        self.current_marking = {p.name: initial_marking.get(p, 0) for p in net.places}

        # # 3. Build transition metadata: inputs, outputs, weights, type, delay, priority
        # self.transitions = {}
        # for t in net.transitions:
        #     inputs  = [(arc.source, arc.weight) for arc in t.in_arcs]
        #     outputs = [(arc.target, arc.weight) for arc in t.out_arcs]
  
        #     self.transitions[t] = {
        #         'input':   inputs,
        #         'output':  outputs,
        #     }
        
        # 4. Prepare logs
        self.detailed_log    = dict()
        self.firing_log      = defaultdict(list)   # per‐transition timestamps
        self.firing_sequence = []                  # global ordered list

    def __initialize_marking(self):
        for item in self.initial_marking.items():
            self.current_marking[item[0].name] = item[1]
            
    def __fire_transition(self, t:SimplePN.SimpleTransition):
        """
        Atomically consume and produce tokens for one transition `t`.
        """
        
        # meta = self.transitions[t]
        # consume
        for arc in t.in_arcs:
            self.current_marking[arc.source.name] -= arc.weight
            
        # produce
        for arc in t.out_arcs:
            self.current_marking[arc.target.name] += arc.weight

        # log the event
        now = self.env.now  # current sim time
        self.firing_log[t.name].append(now)
        self.firing_sequence.append((t.name, now))
        print(f"[{now}] Fired PNML-ID: {t.name} (Label: {t.label}); tokens={self.current_marking}")
        
        
    def is_transition_enabled(self, transition: SimplePN.SimpleTransition) -> bool:
        """
        check if a transition is enabled
        A transition can fire iff every input place has at least `weight` tokens.
        """

        for arc in transition.in_arcs:
            input_place = arc.source
            weight = arc.weight
            ntokens = self.current_marking.get(input_place.name)
            if ntokens < weight:
                return False
        
        # for place, weight in self.transitions[transition]['input']:
        #     if self.places.get(place, 0) < weight:
        #         return False
        return True

    
    def get_enabled_transitions(self):
        """
        Return all transitions that are enabled.
        """
        
        enabled_transitions = []
                
        for tran in self.net.transitions:
            if self.is_transition_enabled(transition=tran):
                enabled_transitions.append(tran)
        
        # return [
        #     t for t, meta in self.transitions.items()
        #     if meta['type'] == ttype and self.can_fire(t)
        # ]
        return enabled_transitions
        
    
    def simulate(self):
        """
        The main SimPy process: fire immediate transitions first, then timed ones.
        """
        # intialize marking
        self.__initialize_marking()
            
            
        while True:
            # 1️Immediate transitions (zero‐delay, highest priority)
            enabled_transitions = self.get_enabled_transitions()
            
            if enabled_transitions:
                # respect max priority among immediates (GSPN semantics)
                # max_prio = max(t.priority for t in enabled_transitions)
                # print(max_prio)
                
                
                
                
                # batch    = [t for t in enabled_transitions if t.priority == max_prio]
                batch    = [t for t in enabled_transitions]
                
                now = self.env.now
                enabled_transitions_names = [t.name for t in enabled_transitions]
                transition_to_fire = random.choice(batch)
                # print(transition_to_fire)
                
                self.detailed_log.update(
                    {now: {
                    "enabled_transitions" : enabled_transitions_names,
                    "transition_to_fire" : transition_to_fire.name
                    }}
                )
                
                # for t in batch:
                self.__fire_transition(transition_to_fire)
                
                enabled_transitions = self.get_enabled_transitions()
                print(f"Enabled Transitions: {enabled_transitions}")
                
                if enabled_transitions == []:
                    # No transitions → end simulation
                    print("No more enabled transitions → simulation ends")
                    break
                
                
                yield self.env.timeout(1)   # immediate :contentReference[oaicite:8]{index=8}
                continue


    # def _delayed_fire(self, t, delay: float):
    #     """
    #     A helper process: wait `delay`, then fire transition `t`.
    #     """
    #     yield self.env.timeout(delay)
    #     self._fire_transition(t)

    def run(self, until=None):
        """
        Kick off the simulation and run until no events remain (or until time).
        """
        # start the main simulate() process
        self.env.process(self.simulate())
        # run the SimPy event loop
        self.env.run(until=until)  # until None ⇒ run until exhaustion :contentReference[oaicite:9]{index=9}

    
    def get_firing_sequence(self):
        """
        Return an OrderedDict of transitions → timestamp of first firing.
        """
        seq = OrderedDict()
        for t, ts in self.firing_sequence:
            if t not in seq:
                seq[t] = ts
        return seq