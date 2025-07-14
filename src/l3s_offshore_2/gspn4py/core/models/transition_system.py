## Package: Strauctural Adaptive Transition System
## Author: Shengrui Peng

from __future__ import annotations
from typing import List, Tuple, Set, Union
import json
from datetime import datetime

from pm4py.objects.transition_system.obj import TransitionSystem
from pm4py import view_transition_system

# from itertools import combinations
# from itertools import chain, combinations

from copy import copy

#SECTION - SATransitionSystem
class StructuralAdaptiveTS(TransitionSystem):
    
    #SECTION - State
    class State(TransitionSystem.State):
        def __init__(self, name, incoming=None, outgoing=None, data=None):
            super().__init__(name, incoming, outgoing, data)
            
        def __repr__(self):
            return f"{self.name}"
            # return f"({self.name}, incoming event: {self.incoming}, outgoing event:{self.outgoing})"
    #!SECTION
    
    #SECTION - Event
    class Event(object):
        def __init__(self, name=None, data=None) -> None:
            self.__name = name
            self.__data = data
        def __get_name(self):
            return self.__name

        def __set_name(self, name):
            self.__name = name
        
        def __repr__(self) -> str:
            return str(self.name)
        
        def __get_data(self):
            return self.__data

        def __set_data(self, data):
            self.__data = data

        #ANCHOR - Porperty
        name = property(__get_name, __set_name)
        data = property(__get_data, __set_data)
    #!SECTION
    
    #SECTION - StateTransition
    class StateTransition(TransitionSystem.Transition):
        def __init__(self, name, from_state, to_state, data=None, abs_frequency:int=0, rel_frequency:float=0):
            super().__init__(name, from_state, to_state, data)
            
            self.__abs_frequency = abs_frequency
            self.__rel_frequency = rel_frequency
            
            
        def __repr__(self):
            return f"[({self.from_state.name}, {self.event_name}, {self.to_state.name}), {self.abs_frequency}, {self.rel_frequency}]"
        
        def __get_abs_frequency(self):
            return self.__abs_frequency
        
        def __get_rel_frequency(self):
            return self.__rel_frequency
        
        def __set_rel_frequency(self, n:float):
            if n > 0:
                self.__rel_frequency = self.__abs_frequency/n
        
        def update_frequency(self):
            self.__abs_frequency += 1
        
        event_name = TransitionSystem.Transition.name
        abs_frequency = property(__get_abs_frequency)
        rel_frequency = property(__get_rel_frequency, __set_rel_frequency)
        def get_tuple(self):
            return (self.from_state.name, self.event_name, self.to_state.name)
    #!SECTION    
    
    
           
    def __init__(self, name=None, states=None, state_transitions=None, events=None, configuration=None):
        super().__init__(name=name, states=states, transitions=state_transitions)
        self.__name = f'TS_{datetime.now().strftime("%y%m%d%H%M%S")}' if name is None else name
        self.__events = set() if events is None else events
        self.__config = dict() if configuration is None else configuration
        
        # self.initial_states = initial_states if initial_states is not None else set()
        # self.events = events if events is not None else set()
    
    
    #SECTION - Private Methods
    def __add_state(self, state_name:str) -> bool:
        '''
        Add a state object to the transition system.
        
        PARAMETERS:
        state_name (str): Name of the state
        
        RETURNS:
        bool: True if the state was added successfully, otherwise False
        '''
        if not state_name:
            return False
        
        if state_name not in self.get_state_names():
            state = StructuralAdaptiveTS.State(name=state_name)
            self.states.add(state)
            return True
        return False
    
    
    def __add_states_batch(self, state_names: List[str]):
        '''
        add state objects to the transition system
        
        PARAMETERS:
        
        '''
        state_added = []
        for sn in state_names:
            flag = self.__add_state(state_name=sn)
            if flag:
                state_added.append(sn)
        return state_added
    
    
    def __ensure_state_exists(self, state_name: str):
        if state_name not in self.get_state_names():
            self.__add_state(state_name=state_name)
    
    def __set_intial_state(self, state_name: str) -> bool:
        """
        Sets an initial state for the transition system.

        Parameters:
        ----------
        state_name : str
            The name of the state to be set as the initial state.

        Returns:
        -------
        bool
            True if the state is set as the initial state successfully, otherwise False.

        Raises:
        ------
        ValueError
            If the state with the given name is not found.
        """
        try:    
            if state_name in self.get_state_names():
                self.initial_states.add(state_name)
                return True
            else:
                raise ValueError(f'State "{state_name}" not found.')
        except ValueError as e:
            print(f'Error: {e.args[0]}')
            return False
    
    
    
    def __add_event(self, event_name: str) -> bool:
        """
        Adds a new event to the transition system if it does not already exist.

        Parameters:
        ----------
        event_name : str
            The name of the event to be added.

        Returns:
        -------
        bool: 
            True if the event was added successfully, or if the event already exists.
        """
        event_names = self.get_event_names()
        if event_name not in event_names:
            event = self.Event(name=event_name)
            self.events.add(event)
        return True
    
    
    def __ensure_event_exists(self, event_name: str):
        if event_name not in self.get_event_names():
            self.__add_event(event_name=event_name)
    
    def __get_initial_states(self):
        '''
        Get the initial states
        '''
        ini_states = self.source_states - self.sink_states
        return ini_states
    
    
    def __get_terminal_states(self):
        '''
        Get the terminal states
        '''
        terminal_states = self.sink_states - self.source_states
        return terminal_states
    
    
    def __get_source_states(self):
        '''
        Get the source states
        '''
        source_states = set()
        for st in self.state_transitions:
            source_states.add(st.from_state.name)
        
        return source_states
    
    def __get_sink_states(self):
        '''
        Get the sink states
        '''
        sink_states = set()
        
        for st in self.state_transitions:
            sink_states.add(st.to_state.name)
        return sink_states
    
    
    
    
    #!SECTION
    
    #SECTION - Properties
    @property
    def name(self) -> set:
        return self.__name # type: ignore
    
    # @property
    # def state_transitions(self) -> List[StateTransition]:
    #     return self.transitions
    state_transitions = TransitionSystem.transitions
    
    @property
    def events(self) -> set:
        return self.__events
    
    # @property
    # def initial_states(self) -> list:
    #     '''
    #     get initial state
    #     '''
    #     return list(self.__get_initial_states())
    
    # @property
    # def terminal_states(self) -> set:
    #     return self.__get_terminal_states()
    
    # @property
    # def source_states(self) -> set:
    #     return self.__get_source_states()
    
    # @property
    # def sink_states(self) -> set:
    #     return self.__get_sink_states()
    
    source_states = property(__get_source_states)
    sink_states = property(__get_sink_states)
    initial_states = property(__get_initial_states)
    terminal_states = property(__get_terminal_states)

    @property
    def configuration(self) -> dict:
        return self.__config
    
    #!SECTION
            
            
    #SECTION - Public Methods
    
    #ANCHOR - General Functions
    def read_from_json(self, path_to_json_file: str):
        '''
        Construct a transition system from a jason file
        
        PARAMETERS:
        path_to_json_file (str): the path to the json file
        
        RETURN:
        Binary: True if success, otherwise False.
        '''
        pass
    
    def ts_view(self):
        '''
        view the transition system in png format
        
        PARAMETERS: None
        RETURNS: None
        '''
        view_transition_system(transition_system=self, format='png', bgcolor='white')

    
    def print_info(self):
        '''
        print relevent information about the transition system
        
        PARAMETERS: None
        RETURNS: None
        '''
        print(f'Initial States: {self.initial_states}')
        print(f'Events: {self.get_event_names()}')
        print(f'States: {self.get_state_names()}')
        print(f'State Transitions: {self.get_all_state_transition_tuples()}')
    
    
    #ANCHOR - getters
    
    def get_state_names(self) -> List[str]:
        """
        Get the set of state names.

        PARAMETERS:
        None

        RETURNS:
        --------
        
        A lsit of state names in string
        """
        return [s.name for s in self.states]
    
    
    def get_state_by_name(self, state_name: str) -> State: # type: ignore
        """
        Retrieves a state object by its name from the list of states.

        Parameters:
        ----------
        state_name : str
            The name of the state to be retrieved.

        Returns:
        -------
        TransitionSystem.State or None
            The state object if found, or None if the state name is not found.

        Raises:
        ------
        ValueError
            If the state with the given name is not found.
        """
        try:
            if state_name not in self.get_state_names():
                raise ValueError(f'State with name "{state_name}" not found!')
            
            for s in self.states:
                if state_name == s.name:
                    return s
        except ValueError as e:
            print(f'Warning: {e.args[0]}')
            return None # type: ignore
    
    # def get_state_multiplicity(self, state_name: str) -> int:
        
    #     for s in self.states:
    #         if s.name == state_name:
    #             return s.multiplicity
    
    # def get_all_state_multiplicity(self) -> dict:
    #     state_multiplicity = {}
        
    #     for s in self.states:
    #         state_multiplicity[s.name] = s.multiplicity
            
    #     return state_multiplicity
    
    
    # def set_state_multiplicity(self, state_name: str, multiplicity: int) -> bool:
        
    #     for s in self.states:
    #         if s.name == state_name:
    #             s.multiplicity = multiplicity
        
    #             return True
        
    #     return False
    
    ## Event
    
    
    # def get_events(self) -> set:
    #     '''
    #     Get the set of event objects
        
    #     Parameters:
    #     ----------
    #     None
        
    #     Returns:
    #     --------
    #     Set[Event]: 
    #         the set of events in transition system.
    #     '''
    #     return self.events
    
    def get_event_names(self) -> List[str]:
        """
        Retrieves the names of all events in the transition system.

        Parameters:
        ----------
        None

        Returns:
        -------
        Set[str]
            A set containing the names of all events in the transition system.
        """
        return [e.name for e in self.events]
    
    
    def get_event_by_name(self, event_name: str) -> Event:
        """
        Retrieves an event object by its name from the list of events.

        Parameters:
        ----------
        event_name : str
            The name of the event to be retrieved.

        Returns:
        -------
        Event or None
            The event object if found, or None if no event with the specified name exists.
        """
        event = None
        for e in self.events:
            if e.name == event_name:
                event = e
        return event # type: ignore
    
    
    def get_state_transition_by_event_name(self, event_name: str) -> List[StateTransition]:
        """
        Retrieves all state transitions associated with a given event name.

        Each state transition is represented as a tuple containing the source state name,
        the event name, and the target state name.

        Parameters:
        ----------
        event_name : str
            The name of the event to filter transitions by.

        Returns:
        -------
        List[StateTransition]
            A list of StateTransition objects associated with the specified event name.
        """
        # Initialize an empty set to store state transitions for the given event
        state_transitions = []
        
         # Iterate through all transitions and collect those that match the event name
        for t in self.state_transitions:
            if t.event_name == event_name:
                # st = (t.from_state.name, t.name, t.to_state.name)
                state_transitions.append(t)
        
        return state_transitions
    
    
    def get_state_transition(self, event_name:str, from_state_name:str, to_state_name:str) -> Union[StateTransition, None]:
        """
        Retrieves a specific transition object by its name and the names of its source and target states.

        Parameters:
        ----------
        transition_name : str
            The name of the transition.
        from_state_name : str
            The name of the source state.
        to_state_name : str
            The name of the target state.

        Returns:
        -------
        Transition or None
            The transition object if found, otherwise None.
        """
        for t in self.state_transitions:
            if t.event_name == event_name and t.from_state.name == from_state_name and t.to_state.name == to_state_name:
                return t
        return None
    
    
    # def get_state_transitions_by_name(self, event_name: str) -> set:
    #     """
    #     Retrieves the set of state-transition objects associated with a specific event name in the transition system.
        
    #     Parameters:
    #     ----------
    #     event_name: str
    #         The name of the event to filter transitions by.

    #     Returns:
    #     -------
    #     set
    #         A set of transitions associtated with the sepcified event name.
    #     """
    #     transitions = set()
    #     for t in self.transitions:
    #         if t.name == event_name:
    #             transitions.add(t)
    #     return transitions
    
    
    def get_state_transitions_by_from_state_name(self, from_state_name: str) -> List[StateTransition]:
        """
        Retrieves a set of state transitions that originate from a specified source state.

        Each tuple in the set contains the source state name, the transition name, and the target state name.

        Parameters:
        ----------
        from_state_name : str
            The name of the source state to filter transitions by.

        Returns:
        -------
        list
            A list of StateTransition objects.
        """
        state_transitions = [] # Initialize an empty set to store machting state-transitions
        
        for st in self.state_transitions:
            if st.from_state.name == from_state_name:
                # add the transition to the set if it matches the source state
                state_transitions.append(st)
        
        return state_transitions # return the list of matching state-transitions
    
    
    def get_state_transitions_by_to_state_name(self, to_state_name: str) -> List[StateTransition]:
        """
        Retrieves a set of state transitions that target a specified state.

        Each tuple in the set contains the source state name, the transition name, and the target state name.

        Parameters:
        ----------
        to_state_name : str
            The name of the target state to filter transitions by.

        Returns:
        -------
        list
            A list of StateTransition objects.
        """
        state_transitions = [] # Initialize an empty set to store 
        for st in self.state_transitions:
            if st.to_state.name == to_state_name:
                # add the transition to the set if it matches the target state
                state_transitions.append(st)
        return state_transitions # return the list of matching state-transitions
    
    
    def get_all_state_transition_tuples(self) -> List[Tuple[str, str, str]]:
        """
        Retrieves the set of all state transitions represented as tuples.

        Each tuple contains the source state name, the event name, and the target state name.

        Parameters:
        ----------
        None

        Returns:
        -------
        <set>
            A set of tuples, each representing a state transition in the form (from_state_name, event_name, to_state_name).
        """
        results = [] # Initialize an empty set to store state transitions
        
        for st in self.state_transitions:
            results.append(st.get_tuple()) # Add each state transition as a tuple to the set
            
        return results
    
    
    #ANCHOR - Operations
    
    def add_arc_from_to(self, name, fr, to, data=None):
        """
        Adds a transition from a state to another state in some transition system.
        Assumes from and to are in the transition system!

        Parameters
        ----------
        name: name of the transition
        fr: state from
        to:  state to
        ts: transition system to use
        data: data associated to the Transition System

        Returns
        -------
        None
        """
        tran = StructuralAdaptiveTS.StateTransition(name, fr, to, data)
        self.transitions.add(tran)
        fr.outgoing.add(tran)
        to.incoming.add(tran)
        tran.update_frequency()
    
    
    def add_state_transition(self, event_name: str, from_state_name: str, to_state_name: str, data=None) -> bool:
        """
        Adds a transition between states in the transition system.

        Parameters:
        ----------
        name : str
            The name of the event triggering the transition.
        from_state_name : str
            The name of the initial state.
        to_state_name : str
            The name of the target state.
        data : optional
            Additional data associated with the transition.

        Returns:
        -------
        bool
            True if the transition was successfully added, False otherwise.

        Raises:
        ------
        ValueError
            If the state transition already exists.
        """
        # check if state transition already exsits
        # st = (from_state_name, event_name, to_state_name)
        st = self.get_state_transition(event_name=event_name, from_state_name=from_state_name, to_state_name=to_state_name)
        print(st)
        
        
        if st:
            # update the frequency if state-transition already exists
            st.update_frequency()
            print('frequency updated')
            # raise ValueError(f'State transition "{st}" already exists!')
        else:
            # ensure the event, from_state and to_state exist
            self.__ensure_event_exists(event_name=event_name)
            self.__ensure_state_exists(state_name=from_state_name)
            self.__ensure_state_exists(state_name=to_state_name)
            
            # get the from_state and to_state objects
            from_state = self.get_state_by_name(state_name=from_state_name)
            to_state = self.get_state_by_name(state_name=to_state_name)
            
            if from_state and to_state:
                self.add_arc_from_to(name=event_name, fr=from_state, to=to_state, data=data)
                return True
        
        return False
    
    
    def add_state_transitions_batch(self, state_transitions: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        """
        Adds multiple state transitions to the transition system.

        Parameters:
        ----------
        state_transitions : List[Tuple[str, str, str]]
            A list of tuples, each containing the from_state_name, event name, and to_state_name.

        Returns:
        -------
        List[Tuple[str, str, str]]
            A list of successfully added state transitions.
        """
        
        state_transitions = list(state_transitions)
        
        added_state_transitions = []
        for st in state_transitions:
            from_state_name, event_name, to_state_name = st
            try:
                flag = self.add_state_transition(event_name=event_name, from_state_name=from_state_name, to_state_name=to_state_name)
                if flag:
                    added_state_transitions.append(st)
            except ValueError as e:
                print(f"Failed to add transition {st}: {e.args[0]}")
        return added_state_transitions
    
    
    def build_from_state_transitions(self, state_transitions: List[Tuple[str, str, str]]) -> bool:
        '''
        Initialize a transition system by 
        '''
        
        self.add_state_transitions_batch(state_transitions=state_transitions)
        
        
        return True
    
    
    def update_from_state_transitions(self, state_transitions: List[Tuple[str, str, str]]) -> dict:
        pass
    
    def remove_from_state_transitions(self, state_transitions: List[Tuple[str, str, str]]) -> dict:
        pass
    
    def encode_as_vector(self, max_states=10):
        """
        Encode the TS into a fixed-size vector for the RL observation.
        For simplicity, we flatten an adjacency matrix over at most max_states nodes.
        If the number of nodes is less than max_states, we pad with zeros.
        Each cell is 1 if an edge exists, 0 otherwise.
        The resulting vector is cast to np.float32.
        """
        states = list(self.states)[:max_states]
        
        return
    
    #ANCHOR -  Conversions
    def generate_ts_dict(self):
        try:
            ts_dict = {
                'events': self.get_event_names(),
                'states': self.get_state_names(),
                'state_transitions': self.get_all_state_transitions(),
                'initial_states': self.get_initial_states()
            }
            return ts_dict
        except ValueError as e:
            return e.args[0]
    
    
    #ANCHOR - Metrics
    def get_simplicitity(self) -> float:
            '''
            Calculate the simplicity of the transition system 
            according to (Buijs etal 2012, doi:)
            
            Input: None
            Output: simplicity:float
            
            '''
            num_arcs = len(self.state_transitions)  # |F|
            num_states = len(self.states)           # |S|
            num_events = len(self.events)           # |E|
            
            if num_states + num_arcs != 0:
                simplicity = (num_events + 1)/(num_states + num_arcs)
                return simplicity
            else:
                raise ValueError("Empty Transition System!")
                    
    
    
    def calc_precision_of_transition_system(self, 
                                        ref_ts:StructuralAdaptiveTS,
                                        ) -> float:
    
        '''
        Calculate the precision of the transition system
        
        Parameters:
        ref_ts: reference transtion system
        
        Output:
        precision of the this_ts
        '''
    
        # Initialize eta and theta
        # eta: partial precision of states
        # theta: number of times visited
        
        eta = dict()
        theta = dict()
        for s in self.states:
            eta[s.name] = 0
            theta[s.name] = 0
        
        # print(eta)
        # print(theta)
    
        current_state_this = self.initial_states[0] # name of current state
        current_state_ref = ref_ts.initial_states[0] # name of current state
            
        self.calc_state_precision(
                            current_state_this=current_state_this,
                            ref_ts=ref_ts,
                            current_state_ref=current_state_ref,
                            eta=eta,
                            theta=theta)
    
        ts_precision = self.sum_partial_precisions(eta=eta)
        
        return ts_precision


    def sum_partial_precisions(self, eta:dict):
        '''
        
        '''
        sum = 0
        # print(eta)
        for state in self.states:
            # print(eta[state.name])
            sum = sum + eta[state.name]
            # print(sum)
        
        # print(f'sum: {sum}')
        # print(f'n_states: {len(this_ts.states)}')
        result = sum/len(self.states)
        
        # print(f'result: {result}')
        return result


    def calc_state_precision(self, current_state_this:str,
                            current_state_ref:str, 
                            ref_ts:StructuralAdaptiveTS,
                            eta:dict,
                            theta:dict
                            ) -> float:
        '''
        Calculate the state precision
        
        Input:
            etha:float, theta:int
            etha: 
            theta: number of times current_state_this has been visited
            
        Out:
            precision:float
        '''
        
        # print(f'{current_state_this} vs. {current_state_ref}')
        penalty = 0
        
        
        # get the list of output state-transitions for this- and ref-TS
        output_st_this = self.get_state_transitions_by_from_state(from_state_name=current_state_this)
        output_st_ref = ref_ts.get_state_transitions_by_from_state(from_state_name=current_state_ref)
        
        if output_st_this:
            # print(f'\nOutput State-Transitions: {output_st_this}\n')
            for st_this in output_st_this:
                # print(f'Evaluating: {st_this}')
                if st_this.event_name in [st.event_name for st in output_st_ref]:
                    # print('True')
                    # for st in output_st_ref:
                    #     if st.event_name == st_this.event_name:
                    #         st_ref = st
                    st_ref = next((st for st in output_st_ref if st.event_name == st_this.event_name))
                            
                    # print(f'{st_ref}: state-transition found!')
                    self.calc_state_precision(current_state_this=st_this.to_state.name, 
                                        this_ts=self,
                                        current_state_ref=st_ref.to_state.name, 
                                        ref_ts=ref_ts,
                                        eta=eta,
                                        theta=theta)
                else:
                    # print(f'{st_this}: state-transition NOT found!')
                    penalty += 1
                
                # print(f'penalty of {st_this}: {penalty}')
        
        # number of output state-transitions
        
        num_output_st = len(output_st_this)
        
        if current_state_this in self.terminal_states:
            num_output_st += 1
            
            if current_state_ref not in ref_ts.terminal_states:
                penalty += 1
        
        if not num_output_st == 0:
            partial_precision = (num_output_st - penalty)/ num_output_st
            eta, theta = self.refine_state_precision(state=current_state_this, 
                                eta=eta, 
                                theta=theta, 
                                partial_precision=partial_precision)
        
        return

    def refine_state_precision(self, state:str, eta:dict, theta:dict, partial_precision:float):
        '''
        Refine the value of a state's partial precision
        
        eta: state's partial precision
        theta: number of times state s has been visited
        '''
        
        # if either eta or theta is not deined for this state
        # if eta.get(state) == None:
        #     eta[state] = 0
        
        # if theta.get(state) == None:
        #     theta[state] = 0
        
        
        state_precision = eta[state] * theta[state]
        theta[state] += 1
        eta[state] = (state_precision + partial_precision)/theta[state]
        return eta, theta
    
    #!SECTION