from . import BasePetriNet
from copy import deepcopy



#TODO - class::TimedPetriNet    
class TimedPetriNet(BasePetriNet):
    
    class Place(BasePetriNet.Place):
        def __init__(self, name=None, in_arcs=None, out_arcs=None, properties=None, label=None):
            super().__init__(name, in_arcs, out_arcs, properties, label)
    
    
    class Transition(BasePetriNet.Transition):
        def __init__(self, name=None, label=None, in_arcs=None, out_arcs=None, properties=None, times_fired = 0, fired_at = None, firing_cost = 0, priority = 0, absorbed_tokens = None, created_tokens = None, duration = 0):
            super().__init__(name, label, in_arcs, out_arcs, properties, times_fired, fired_at, firing_cost, priority, absorbed_tokens, created_tokens)
            
            self.__duration = duration

        def __repr__(self):
            if self.label=="" or self.label==None or self.name==self.label:
                return f"(n:{str(self.name)}, d:{str(self.duration)})"
            else:
                return f"(n:{str(self.name)}, l:{str(self.label)}, d:{str(self.duration)})"
                
        def __get_duration(self):
            return self.__duration
        
        def __set_duration(self, duration:float):
            self.__duration = duration
        
        duration = property(__get_duration, __set_duration)
        
        # "("+str(self.name)+", '"+str(self.label)+"')"

    
    
    def __init__(self, name = "TimedPetriNet"):
        super().__init__(name)
    
    
    def __deepcopy__(self, memo):
        """Create a deep copy of this BasePetriNet using its builder methods."""
        # Handle recursive references
        if id(self) in memo:
            return memo[id(self)]

        # Instantiate a new net and register it in memo
        copied = TimedPetriNet(self.name)
        memo[id(self)] = copied

        # Copy places
        place_map = {}
        for p in self.places:
            # Use add_place to ensure namespace and tokens
            copied.add_place({'name': p.name, 'tokens': p.num_of_tokens})
            # Retrieve the newly added place object
            new_p = next(x for x in copied.places if x.name == p.name)
            place_map[p] = new_p

        # Copy transitions
        trans_map = {}
        for t in self.transitions:
            copied.add_transition({
                'name': t.name,
                'label': t.label,
                'properties': deepcopy(t.properties, memo),
                'priority': t.priority,
                'duration': t.duration
            })
            new_t = next(x for x in copied.transitions if x.name == t.name)
            trans_map[t] = new_t

        # Copy arcs
        for arc in self.arcs:
            src = place_map.get(arc.source, trans_map.get(arc.source))
            tgt = place_map.get(arc.target, trans_map.get(arc.target))
            copied.add_arc({
                'source': src.name, # type: ignore
                'target': tgt.name, # type: ignore
                'weight': arc.weight,
                'properties': deepcopy(arc.properties, memo)
            })

        # Copy module manager if exists
        if hasattr(self, '_module_manager'):
            copied._module_manager = deepcopy(self._module_manager, memo) # type: ignore

        # Copy markings and resources directly
        if self._BasePetriNet__initial_marking is not None: # type: ignore
            copied._BasePetriNet__initial_marking = deepcopy(self._BasePetriNet__initial_marking, memo) # type: ignore
        if self._BasePetriNet__final_marking is not None: # type: ignore
            copied._BasePetriNet__final_marking = deepcopy(self._BasePetriNet__final_marking, memo) # type: ignore
        copied._Dm = deepcopy(self._Dm, memo)
        copied._Dp = deepcopy(self._Dp, memo)
        copied._resources = deepcopy(self._resources, memo)

        # Preserve locked state
        if self._locked:
            copied.lock() # type: ignore

        return copied
    
    
    def add_transition(self, transition: dict) -> bool:
        """Add transition with duplicate check."""
        
        name = transition.get("name")
        label = transition.get("label")
        priority = transition.get("priority")
        properties = transition.get("properties")
        duration = transition.get("duration")
        
        if not self._check_modifiable():
            raise ValueError
        
        if name in self._name_space: # type: ignore
            raise ValueError(f"Transition name '{name}' already exists")
        
        if name == "":
            name = None
            
        if label == "" or label == None:
            label = name
        
        if duration == "":
            duration = None
        
        t = TimedPetriNet.Transition(name=name, label=label, priority=priority, properties=properties, duration=duration) # type: ignore
        self.transitions.add(t)
        
        # add transition name to namespace
        self._name_space.add(name)
        return True