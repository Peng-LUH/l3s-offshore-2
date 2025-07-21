import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from typing import Dict, List, Tuple, Optional, Any, Union, Collection, Set
import numpy as np
from collections import defaultdict
from copy import deepcopy
from pprint import pprint


class BasePetriNet(PetriNet):
    """Base Petri Net class"""
    
    #SECTION class Place
    class Place(PetriNet.Place):
        # class variable for unique ID assignment
        _id_counter = 0
    
        def __init__(self, 
                     name=None, 
                     in_arcs=None, 
                     out_arcs=None, 
                     properties=None, 
                     label=None,
                     tokens=None,
                     capacity=None):
            super().__init__(name, in_arcs, out_arcs, properties)
            self.__place_id = BasePetriNet.Place._id_counter
            BasePetriNet.Place._id_counter += 1
            self.__name = f"P-{self.__place_id}" if name == None else name
            self.__label = "" if label is None else label
            self.__tokens = set() if tokens is None else tokens
            self.__capacity = 0 if capacity is None else capacity
            
        # def __init__(self, identifier, tokens=0):
        #     self.identifier = identifier
        #     self.tokens = tokens
        
        #SECTION - Place::Properties
        def __get_place_id(self):
            return self.__place_id
        
        def __get_label(self):
            return self.__label
        
        def __set_label(self, label:str):
            self.__label = label
        
        def __get_tokens(self):
            return self.__tokens
            
        def __get_num_of_tokens(self):
            if self.__tokens:
                return len(self.__tokens)
            return 0
        
        def __get_capacity(self):
            return self.__capacity

        def __set_capacity(self, capacity:int):
            self.__capacity = capacity
        
        place_id = property(__get_place_id)
        label = property(__get_label, __set_label)
        tokens = property(__get_tokens)
        num_of_tokens = property(__get_num_of_tokens)
        capacity = property(__get_capacity, __set_capacity)
        #!SECTION
        
        #SECTION - Place::PublicMethods
        def add_tokens(self, tokens:Set['BasePetriNet.Token']):
            '''
            add a set of tokens to place
            '''
            self.__tokens.update(tokens)
            return
            
        def remove_tokens(self, n:int=1) -> Set:
            '''
            remove n tokens from a place
            '''
            if n == 0:
                print("No tokens removed!")
                return set()
            
            if n < 0:
                raise ValueError("Number of tokens to be removed must be positive integer!")
            
            if self.num_of_tokens >= n:
                popped = set()
                for _ in range(n):
                    popped.add(self.__tokens.pop())
                return popped
            else:
                raise ValueError("Not enough tokens to remove!")
        
        
        def get_input_transitions(self):
            '''
            Source: GpenSIM/Get-Functions/get_inputtrans.m
            '''
            
            pass
    
    
        def get_output_transitions(self):
            '''
            Source: GpenSIM/Get-Functions/get_outputtrans.m
            '''
            pass
    #!SECTION       
    
    #SECTION - Transition::Class
    class Transition(PetriNet.Transition):
        # Class variable shared across all instances
        _id_counter = 0 
        
        def __init__(self, name=None, label=None, in_arcs=None, out_arcs=None, properties=None, 
                     times_fired:int=0, 
                     fired_at:Optional[List[float]]=None, 
                     firing_cost:float=0.0,
                     priority:int=0, 
                     absorbed_tokens:Optional[Set[int]]=None,
                     created_tokens:Optional[Set[int]]=None):
            super().__init__(name, label, in_arcs, out_arcs, properties)
            
            self.__transition_id = BasePetriNet.Transition._id_counter
            BasePetriNet.Transition._id_counter += 1 # incremental update
            self.__name = f"T-{self.__transition_id}" if name == None else name
            self.__times_fired = times_fired # number of times a transition is fired.
            self.__fired_at = list(fired_at) if fired_at is not None else [] # list of timestamps of when the transition is fired
            self.__firing_cost = firing_cost
            self.__priority = priority
            self.__absorbed_tokens = set(absorbed_tokens) if absorbed_tokens is not None else set()    # set of token ids that absorbed by the transiton
            self.__created_tokens = set(created_tokens) if created_tokens is not None else set()      # set of token ids that created by the transtion
        #SECTION - Transition::Properties 
        
        def __get_transition_id(self):
            return self.__transition_id
        
        def __get_times_fired(self):
            return self.__times_fired
        
        def __get_fired_at(self):
            return self.__fired_at
            
        def __get_firing_cost(self):
            return self.__firing_cost
        
        def __set_firint_cost(self, cost):
            self.__firing_cost = cost
            
        def __get_priority(self):
            return self.__priority
        
        def __set_priority(self, value_prio:int):
            self.__priority = value_prio
            
        def __get_absorbed_tokens(self):
            return self.__absorbed_tokens
        
        def __get_created_tokens(self):
            return self.__created_tokens
        
        
        
        transition_id = property(__get_transition_id)
        times_fired = property(__get_times_fired)
        fired_at = property(__get_fired_at)
        firing_cost = property(__get_firing_cost, __set_firint_cost)
        priority = property(__get_priority, __set_priority)
        absorbed_tokens = property(__get_absorbed_tokens)
        created_tokens = property(__get_created_tokens)
        #!SECTION
        
        #SECTION - Transition::PublicMethod
        def update_created_tokens(self, tokens: Set['BasePetriNet.Token']):
            '''
            update the tokens created when firing the transition
            '''
            for tok in tokens:
                self.__created_tokens.add(tok.token_id)
            return
            
        def update_absorbed_tokens(self, tokens: Set['BasePetriNet.Token']):
            '''
            update the tokens absorbed by transition
            '''
            for tok in tokens:
                self.__absorbed_tokens.add(tok.token_id) # type: ignore
            return
        
        def update_fired_at(self, fired_at) -> None:
            self.__fired_at.append(fired_at)
        
        def update_times_fired(self) -> None:
            self.__times_fired += 1
            return
        
        def get_input_places(self):
            '''
            return the set of input places
            '''
            input_places = set()
            
            for ia in self.in_arcs:
                input_places.add(ia.source)
            
            return input_places
        
        def get_output_places(self) -> Set['BasePetriNet.Place']:
            '''
            return the set of output places
            '''
            output_places = set()
            for oa in self.out_arcs:
                output_places.add(oa.target)
            
            return output_places
        
        def is_enabled(self):
            '''
            check if transition is enabled.
            '''
            for ia in self.in_arcs:
                if ia.source.num_of_tokens < ia.weight:
                    return False
            return True
        #!SECTION
    #!SECTION
    
    #SECTION - Arc::Class
    class Arc(PetriNet.Arc):
        def __init__(self, source, target, weight=1, properties=None):
            super().__init__(source, target, weight, properties)
    #!SECTION
    
    #SECTION - Token::Class
    class Token(object):
        # class variable for unique ID assignment
        _id_counter = 0
        
        def __init__(self, created:Tuple, consumed:List[Tuple]=[], properties:Dict={}, reserved=False):
            self.__token_id = BasePetriNet.Token._id_counter # automatically assign unique token_id
            BasePetriNet.Token._id_counter += 1
            self.__created = created        # (created_by, created_at)
            self.__consumed = consumed      # (consumed_by, consumed_at)
            self.__reserved = reserved      # status of the token
            self.__properties = properties  # properties in dict
            
        
        def __repr__(self) -> str:
            return f"{self.__token_id}"
        
        def __str__(self):
            return self.__repr__()

        def __hash__(self):
            return id(self)
        
        def __get_token_id(self):
            return self.__token_id
        
        def __get_created(self):
            created_by, created_at = self.__created
            
            return {
                "created_by": created_by,
                "created_at": created_at
            }
        
        def __get_properties(self):
            return self.__properties
        
        def __get_consumed(self):
            return self.__consumed
        
        def __set_consumed(self, consumed):
            self.__consumed.append(consumed)
        
        def __get_reserved(self):
            return self.__reserved
        
        def __set_reserved(self, reserved:bool):
            self.__reserved = reserved
        
        token_id = property(__get_token_id)
        created = property(__get_created)
        consumed = property(__get_consumed, __set_consumed)
        reserved = property(__get_reserved, __set_reserved)
        properties = property(__get_properties)
    #!SECTION
    
    
    # class variable for unique ID assignment
    _id_counter = 0
    
    # initialization Class::BasePetriNet 
    def __init__(self, name: str = "BasePetriNet", 
                 place: Collection[Place]=None, 
                 transition: Collection[Transition]=None, 
                 arcs: Collection[Arc]=None, 
                 properties:Dict[str, Any]=None):
        super().__init__(name, place, transition, arcs, properties)
        # instance attributes
        self.net_id = BasePetriNet._id_counter
        BasePetriNet._id_counter += 1
        
        self.__initial_marking = None
        self.__final_marking = None
        self._Dm = None  # Input incidence matrix
        self._Dp = None  # Output incidence matrix
        self._locked = False
        self._resources = {}
        self._name_space = set()

        # self.current_time = 0.0
        # self._inhibitor_arcs = defaultdict(list)
        
        # self._firing_times = {}
        # self._priorities = {}
        
        # self._module_manager = ModuleManager()
        # self.firing_cost_enabled = False
    
    def __deepcopy__(self, memo):
        """Create a deep copy of this BasePetriNet using its builder methods."""
        # Handle recursive references
        if id(self) in memo:
            return memo[id(self)]

        # Instantiate a new net and register it in memo
        copied = BasePetriNet(self.name)
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
                'priority': t.priority
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
    
    
    #SECTION - BasePetriNet::Properties
    def __get_initial_marking(self):
        return self.__initial_marking
    
    def __set_intial_marking(self, initial_marking):
        self.__initial_marking = initial_marking
        
    def __get_final_marking(self):
        return self.__final_marking
    
    def __set_final_marking(self, final_marking):
        self.__final_marking = final_marking
    
    def __get_locked(self):
        return self._locked
    
    def __set_locked(self, locked:bool):
        self._locked = locked
    
    def __get_resources(self):
        return self.resources
    
    def __set_resources(self, resources:dict):
        self._resources = resources
    
    initial_marking = property(__get_initial_marking, __set_intial_marking)
    final_marking = property(__get_final_marking, __set_final_marking)
    locked = property(__get_locked, __set_locked)
    resources = property(__get_resources, __set_resources)
    #!SECTION
    
    
    #SECTION - Protected Methods
    # methods for internal use, not part of the public API.
    def _check_modifiable(self):
        """Enforce structural immutability after locking."""
        if self._locked:
            raise RuntimeError("Network structure is frozen after locking")
        return True
        
    #ANCHOR - _validate_net_properties
    def _validate_net_properties(self) -> None:
        """Post-lock validation checks."""
        # Validate transitions have connections
        for t in self.transitions:
            if not any(arc.source == t or arc.target == t for arc in self.arcs):
                raise ValueError(f"Transition {t.name} has no connections")

        # Validate initial marking places exist
        for p in self._initial_marking:
            if p not in self.places:
                raise ValueError(f"Initial marking contains unknown place {p.name}")
    
    #ANCHOR - _get_place_by_name
    def _get_place_by_name(self, name: str) -> Optional['BasePetriNet.Place']:
        return next((p for p in self.places if p.name == name), None)
    
    #ANCHOR - _get_transition_by_name
    def get_transition_by_name(self, name: str) -> Optional['BasePetriNet.Transition']:
        return next((t for t in self.transitions if t.name == name), None)
    #!SECTION
    
    
    #SECTION - Check-Valid
    def check_valid_file(self, filename):
        '''
        check if filename is valid
        Source: GpenSIM/Check-Valid-Functions/check_valid_file.m
        
        '''
        pass
    
    def check_valid_place(self):
        
        pass
    
    # def check_valid_resource(self):
        '''
        
        '''
        # pass
    
    def check_valid_transition(self):
        '''
        
        '''
        pass
    #!SECTION
    
    
    #SECTION - Structure Modifications
    #ANCHOR - add_place
    def add_place(self, place: Dict) -> bool:
        """Add place with duplicate check."""
        self._check_modifiable()
        
        name = place.get('name')
        tokens = place.get('tokens')
        
        # print(f"name: {name}, tokens: {tokens}")
        
        if name in self._name_space:
            raise ValueError(f"Place name '{name}' already exists!")
        
        if name == "":
            name = None
        
        if tokens < 0: # type: ignore
            raise ValueError("Number of tokens cannot be negative!")
        
        if not isinstance(tokens, int):
            raise ValueError("Number of tokens must be integer!")
        
        place_obj = BasePetriNet.Place(name=name)
        
        if tokens > 0:
            for _ in range(tokens):
                tok = BasePetriNet.Token(created=('init', 0))
                place_obj.tokens.add(tok)
                
        self.places.add(place_obj)
        
        # add place name to namespace
        self._name_space.add(name)
        
        return True

    #ANCHOR - add_transition
    def add_transition(self, transition: dict) -> bool:
        """Add transition with duplicate check."""
        
        name = transition.get("name")
        label = transition.get("label")
        priority = transition.get("priority")
        properties = transition.get("properties")
        
        if not self._check_modifiable():
            raise ValueError
        
        if name in self._name_space: # type: ignore
            raise ValueError(f"Transition name '{name}' already exists")
        
        if name == "":
            name = None
            
        if label == "" or label == None:
            label = name
        
        t = BasePetriNet.Transition(name=name, label=label, priority=priority, properties=properties) # type: ignore
        self.transitions.add(t)
        
        # add transition name to namespace
        self._name_space.add(name)
        return True

    #ANCHOR - add_arc
    def add_arc(self, arc:dict) -> None:
        """Add arc with validation."""
        # pprint(arc)
        source = arc.get("source")
        target = arc.get("target")
        weight = arc.get("weight")
        properties = arc.get("properties")
        if not self._check_modifiable():
            raise ValueError
        
        # check if the weight is larger than 0
        if weight == "" or weight == None:
            weight = 1
        
        if weight is not None and weight <= 0: # type: ignore
            raise ValueError("Arc weight must be positive")
        
        
        # identify source and target obj
        
        source_obj = self.get_obj_by_name(obj_name=source) # type: ignore
        target_obj = self.get_obj_by_name(obj_name=target) # type: ignore
        
        if source_obj and target_obj:
            arc = BasePetriNet.Arc(source=source_obj, target=target_obj, weight=weight, properties=properties) # type: ignore
            self.arcs.add(arc)
            source_obj.out_arcs.add(arc)
            target_obj.in_arcs.add(arc)

    #ANCHOR - add_inhibitor_arc
    #REVIEW
    # def add_inhibitor_arc(self,
    #                     place: PetriNet.Place,
    #                     transition: PetriNet.Transition,
    #                     weight: int = 1) -> None:
    #     """Add inhibitor arc with validation."""
    #     self._check_modifiable()
    #     if weight <= 0:
    #         raise ValueError("Inhibitor weight must be positive")
    #     if place not in self.places:
    #         raise ValueError("Invalid place for inhibitor arc")
    #     if transition not in self.transitions:
    #         raise ValueError("Invalid transition for inhibitor arc")
    #     self._inhibitor_arcs[transition].append((place, weight))

    #ANCHOR - update_incidence_matrix
    #REVIEW
    # def update_incidence_matrix(self) -> None:
    #     """Calculate split incidence matrices."""
    #     places = sorted(self.places, key=lambda x: x.name)
    #     transitions = sorted(self.transitions, key=lambda x: x.name)

    #     place_idx = {p: i for i, p in enumerate(places)}
    #     trans_idx = {t: i for i, t in enumerate(transitions)}

    #     self._Dm = np.zeros((len(transitions), len(places)))  # Input matrix
    #     self._Dp = np.zeros((len(transitions), len(places)))  # Output matrix

    #     for arc in self.arcs:
    #         if isinstance(arc.source, PetriNet.Place):
    #             t_idx = trans_idx[arc.target]
    #             p_idx = place_idx[arc.source]
    #             self._Dm[t_idx, p_idx] += arc.weight
    #         else:
    #             t_idx = trans_idx[arc.source]
    #             p_idx = place_idx[arc.target]
    #             self._Dp[t_idx, p_idx] += arc.weight

    #ANCHOR - lock
    # def lock(self) -> None:
    #     """Finalize network structure."""
    #     self._locked = True
    #     self.update_incidence_matrix()
    #     self._validate_net_properties()

    #ANCHOR - split_incidence_matrix
    # def split_incidence_matrix(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    #     """Return (Dm, Dp, D) matrices."""
    #     D = self._Dp - self._Dm # type: ignore
    #     return self._Dm, self._Dp, D # type: ignore

    #ANCHOR - allocate_resources
    # def allocate_resources(self, resources: Dict[str, int]) -> None:
    #     """Allocate system resources."""
    #     if any(v < 0 for v in resources.values()):
    #         raise ValueError("Resource counts cannot be negative")
    #     self._resources = resources.copy()
    #!SECTION
    
    #SECTION - builder
    # @staticmethod
    def build_from_pndf(self, pndf_json):
        '''
        build BasePetriNet object from definition file
        
        Example:
            def_file = {
                "name": "name of the object",
                "place": [],
                "transitions": [],
                "arcs": []
            }
        '''
        #REVIEW        
        #     if 'ports' in pn_def:
        #         combined['modules'][module_id] = {
        #             'name': pn_def.get('name', f'Module_{module_id}'),
        #             'transitions': pn_def['transitions'],
        #             'ports': pn_def['ports']
        #         }

        ## Add places
        places = pndf_json.get("places")
        if places is None:
            print("Set of places is empty!")
        else:
            for p in places:
                self.add_place(place=p)
                
        # update initial marking
        # self.initial_marking = self.get_current_marking_obj()

        ## Add transitions
        transitions = pndf_json.get("transitions")
        if transitions is None:
            print("Set of transitions is empty!")
        else:
            for t in transitions:
                self.add_transition(t)
        
        ## Add arcs
        arcs = pndf_json.get("arcs")
        if arcs is None:
            print("Set of arcs is empty!")
        else:
            for a in arcs:
                self.add_arc(a)
        
        # for arc_def in combined['arcs']:
        #     if len(arc_def) == 3:
        #         src, tgt, weight = arc_def
        #     else:
        #         src, tgt = arc_def
        #         weight = 1

        #     if weight < 1:
        #         raise ValueError(f"Invalid arc weight {weight} for {src} -> {tgt}")

        #     source = place_map.get(src) or trans_map.get(src)
        #     target = place_map.get(tgt) or trans_map.get(tgt)
            
        #     if not source or not target:
        #         raise ValueError(f"Invalid arc: {src} -> {tgt}")
                
        #     net.add_arc(source, target, weight)

       

        # # Set up modules
        # # for mod_id, data in combined['modules'].items():
        # #     net.module_info.add_module(
        # #         data['name'],
        # #         list(data['transitions']),
        # #         list(data.get('ports', []))
        # #     )

        # # net.update_incidence_matrix()
        # # net.lock()
        # return net
        return True
    
    #TODO - build_from_incidence_matrix
    def build_from_incidence_matrix(self):
        '''
        Build BasePetriNet from Incidence Matrix
        '''
        pass
    
    #TODO - build_from_pnml
    def build_from_pnml(self, pnml_file_path):
        '''
        Build BasePetriNet from PNML file
        '''
        # pn = pm4py.read_pnml(file_path=pnml_file_path)
        pass
    
    #!SECTION
    
    
    
    
    #SECTION - Getters
    #
    def get_initial_marking(self):
        '''
        Source: GpenSIM/Get-Functions/get_initial_marking.m
        '''
        pass
    
    def get_initial_marking_obj(self) -> Marking: # type: ignore
        '''
        Get intial marking
        
        Return: a Marking object
        '''
        pass
    
    def get_final_marking(self):
        '''
        
        '''
    
    def get_current_marking(self):
        '''
        Get the current marking
        '''
        curr_marking = {}
        for p in self.places:
            curr_marking[p.name] = p.tokens
        
        return curr_marking
    
    def get_current_marking_obj(self) -> Marking: # type: ignore
        '''
        Get current marking as Marking object.
        Source: /
        '''
        '''
        Get current marking
        
        returns a Marking object
        '''
        current_marking = Marking()
        
        for p in self.places:
            current_marking[p] = p.num_of_tokens
        
        return current_marking
    
    
    def get_all_tokens(self):
        '''
        Source: GpenSIM/Get-Functions/get_all_tokens.m
        '''
        
        pass
    
    
    # def get_color(self, place_id, token_id):
    #     '''
    #     get the color of the token by tokenID
    #     token is identified by the (place_id, token_id) or (place_idx, token_id)
        
    #     Source: GpenSIM/Get-Functions/get_color.m
    #     '''
    #     pass
        
    
    def get_cost(self):
        '''
        Source: GpenSIM/Get-Functions/get_cost.m
        '''
        pass
    
    
    # def get_current_colors(self):
    #     '''
    #     Source: GpenSIM/Get-Functions/get_current_colors.m
    #     '''
    #     pass
    
    
    # def get_firingtime(self):
    #     '''
    #     This function extracts firing_time of the transition from PetriNet
    #     Source: GpenSIM/Get-Functions/get_firingtime.m
    #     '''
    #     pass
    
    def get_obj_by_name(self, obj_name:str):
        '''
        return the place or transition with the given name
        '''
        place_names = self.get_name_of_places()
        transition_names = self.get_name_of_transitions()
        
        if not obj_name in self._name_space:
            raise ValueError("Name of the object is invalid!")
        
        if obj_name in place_names:
            obj = self._get_place_by_name(name=obj_name)
            return obj
        
        if obj_name in transition_names:
            obj = self.get_transition_by_name(name=obj_name)
            return obj
        
        return None
        
    
    def get_place(self):
        '''
        Source: GpenSIM/Get-Functions/get_place.m
        '''
        pass
    
    
    def get_priority_by_transition_name(self, ts_name:str):
        '''
        Get the priority of a transition by name
        Source: GpenSIM/Get-Functions/get_priority.m
        '''
        
        
        pass
    
    def get_list_of_priorities(self) -> List:
        '''
        get the priorities of all transitions
        return a list
        '''
        
        list_priorities = []
        
        for t in self.transitions:
            list_priorities.append(t.priority)
        
        return list_priorities
    
    
    def get_token_creation_time(self, token_id):
        '''
        get the creation time of a token
        Source: GpenSIM/Get-Functions/get_tokCT.m
        '''
        pass
    
    def get_tokens(self, place_id, token_ids: List):
        '''
        get complete information about the tokens in a place
        Source: GpenSIM/Get-Functions/get_token.m
        Source: GpenSIM/Get-Functions/get_tokens.m
        '''
        pass
    
    def get_transitions(self, transition_name:str='', transition_idx:int=0) -> Union[List[Dict], None]:
        '''
        extract
        
        Source: GpenSIM/Get-Functions/
        
        Input: 
            - transition_name: str 
            - transition_idx: int
        
        Output:
        {
            {
                name:               'tX1'
                firing_time:        1
                firing_cost:        0
                times_fired:        5
                resources_on_use:   []
                resources_reserved: 0
                absorbed_tokens:    [0 0 0]
                resources_owned:    0
            }
        }
        
        '''
        pass

    def get_num_places(self):
        '''
        get number of places
        
        Source: GpenSIM/Get-Functions/nplaces.m
        '''
        pass
    
    def get_num_system_resources(self):
        '''
        get number of system resources
        
        Source: GpenSIM/Get-Functions/nresources.m
        
        
        '''
        # return self.num_of_system_resources
        pass
    
    
    def get_num_tokens_in_place(self, place_id, place_name):
        '''
        get number of tokens in a place
        
        Source: GpenSIM/Get-Functions/ntokens.m
        
        Input:
            - place_id
            - place_name
        
        '''
        
        pass
    
    
    def get_num_transitions(self):
        '''
        get number of transitions
        
        Source: GpenSIM/Get-Functions/ntrans.m
        
        '''
        return len(self.transitions)
    
    
    def get_name_of_place(self, place_id:int):
        '''
        get the 
        
        Source: GpenSIM/Get-Functions/pname.m
        '''
        
        pass
    
    def get_name_of_places(self):
        '''
        get the name of places
        
        Source: /
        '''
        name_of_places = set()
        for p in self.places:
            name_of_places.add(p.name)
        return name_of_places
    
    def get_system_resource_names(self):
        '''
        get the name of system resources
        
        Source: GpenSIM/Get-Functions/rname.m
        
        
        '''
        pass
    
    def get_times_fired_of_transition(self, transition_idx):
        '''
        get the number of times a transition has been fired
        
        Source: GpenSIM/Get-Functions/timesfired.m
        
        '''
        
        pass
    
    def get_name_of_transition_by_id(self, transition_id):
        '''
        get the name of a transition by id
        
        Source: GpenSIM/Get-Functions/tname.m
        
        '''
        pass
    
    def get_name_of_transitions_by_id(self, transition_id:List[str]):
        '''
        get the name of transitions by id
        
        Source: /
        '''
        pass
    
    def get_name_of_transitions(self):
        '''
        get the name of all transitions
        
        Source: /
        '''
        name_of_transitions = set()
        for t in self.transitions:
            name_of_transitions.add(t.name)
        return name_of_transitions
        
    
    #!SECTION
    
    
    #SECTION - Setters
    #ANCHOR - set_intial_marking
    def set_initial_marking(self, marking: Dict[str, int]) -> None:
        """Set initial marking silently."""
        self._initial_marking = Marking()
        for place_name, tokens in marking.items():
            if (place := self._get_place_by_name(place_name)) is None:
                raise ValueError(f"Place '{place_name}' not found")
            self._initial_marking[place] = tokens

    #ANCHOR - set_initial_dynamics
    # def set_initial_dynamics(self, initial_dynamics: Dict[str, Any]):
    #     """Initialize markings, firing times, priorities, and resources."""
    #     # Handle initial marking
    #     if 'm0' in initial_dynamics:
    #         self.set_initial_marking(initial_dynamics['m0'])
        
    #     # Handle firing times (default: empty)
    #     firing_times = initial_dynamics.get('ft', {})
    #     self.set_firing_times(firing_times)
        
    #     # Handle priorities (default: zeros)
    #     priorities = initial_dynamics.get('ip', {t.name: 0 for t in self.transitions})
    #     self.set_priorities(priorities)
        
    #     # Handle resources (default: empty)
    #     if 're' in initial_dynamics:
    #         self.allocate_resources(initial_dynamics['re'])
    
    #ANCHOR - set_firing_times
    # def set_firing_times(self, firing_times: Dict[str, float]) -> None:
    #     """Set transition firing times."""
    #     self._firing_times = {}
    #     for t_name, ft in firing_times.items():
    #         if (t := self._get_transition_by_name(t_name)) is None:
    #             raise ValueError(f"Transition '{t_name}' not found")
    #         self._firing_times[t] = ft
            

    #ANCHOR - set_priorities
    def set_priorities(self, priorities: Dict[str, int]) -> None:
        """Set transition priorities."""
        self._priorities = {}
        for t_name, p in priorities.items():
            if (t := self.get_transition_by_name(t_name)) is None:
                raise ValueError(f"Transition '{t_name}' not found")
            self._priorities[t] = p
    #!SECTION
    
    
    
    
    #SECTION - Private Methods
    # Private method (name mangling)
    #ANCHOR - __deepcopy__
    # def __deepcopy__(self, memo): # type: ignore
    #     """Safe deepcopy implementation using add methods."""
    #     copied = BasePetriNet(self.name)
        
    #     # Copy places
    #     place_map = {}
    #     for p in self.places:
    #         new_p = copied.add_place(p.name)
    #         place_map[p] = new_p
            
    #     # Copy transitions
    #     trans_map = {}
    #     for t in self.transitions:
    #         new_t = copied.add_transition(t.name)
    #         trans_map[t] = new_t
            
    #     # Copy arcs using original weights
    #     for arc in self.arcs:
    #         source = place_map.get(arc.source, trans_map.get(arc.source))
    #         target = place_map.get(arc.target, trans_map.get(arc.target))
    #         copied.add_arc(source, target, arc.weight) # type: ignore
            
    #     # Copy inhibitor arcs
    #     for trans, inhibitors in self._inhibitor_arcs.items():
    #         for place, weight in inhibitors:
    #             copied.add_inhibitor_arc(place_map[place], trans_map[trans], weight)
                
    #     # Copy modules
    #     for module_id in self._module_manager._modules:
    #         module = self._module_manager._modules[module_id]
    #         copied._module_manager.add_module(
    #             name=module['name'],
    #             transitions=list(module['transitions']),
    #             ports=list(module['ports'])
    #         )
        
    #     # Copy dynamics
    #     copied.set_initial_marking({p.name: tokens for p, tokens in self.initial_marking.items()})
    #     copied._firing_times = {trans_map[t]: ft for t, ft in self._firing_times.items()}
    #     copied._priorities = {trans_map[t]: p for t, p in self._priorities.items()}
    #     copied._resources = deepcopy(self._resources, memo)
        
    #     # Copy matrices if calculated
    #     if self._Dm is not None:
    #         copied._Dm = self._Dm.copy()
    #     if self._Dp is not None:
    #         copied._Dp = self._Dp.copy()
            
    #     if self._locked:
    #         copied.lock()
            
    #     return copied
    #!SECTION
    
    
    # @property
    # def initial_marking(self) -> Marking:
    #     return deepcopy(self._initial_marking)

    # @property
    # def inhibitor_arcs(self) -> Dict[PetriNet.Transition, List[Tuple[PetriNet.Place, int]]]:
    #     return deepcopy(self._inhibitor_arcs)

    # @property
    # def module_info(self) -> ModuleManager:
    #     return self._module_manager
    
    
    

    
    

    
    






# class ModuleManager:
#     """Manage modular Petri net structure."""
    
#     def __init__(self):
#         self._modules = {}
#         self._transition_map = {}
#         self._port_transitions = set()
#         self._next_id = 1

    
    
#     def add_module(self, 
#                  name: str, 
#                  transitions: List[str], 
#                  ports: List[str] = []) -> int:
#         """Register a new module with validation."""
#         if not name or not transitions:
#             raise ValueError("Module name and transitions required")
        
#         conflict_trans = [t for t in transitions if t in self._transition_map]
#         if conflict_trans:
#             raise ValueError(f"Transitions already in modules: {conflict_trans}")
        
#         module_id = self._next_id
#         self._modules[module_id] = {
#             'name': name,
#             'transitions': set(transitions),
#             'ports': set(ports) if ports else set()
#         }
        
#         for t in transitions:
#             self._transition_map[t] = module_id
#         for t in ports or []:
#             self._port_transitions.add(t)
        
#         self._next_id += 1
#         return module_id

#     def get_module_membership(self, transition: str) -> Optional[Tuple[int, bool]]:
#         """Get module ID and port status."""
#         mod_id = self._transition_map.get(transition)
#         if mod_id is not None:
#             return (mod_id, transition in self._port_transitions)
#         return None

#     @property
#     def module_names(self) -> List[str]:
#         return [m['name'] for m in self._modules.values()]