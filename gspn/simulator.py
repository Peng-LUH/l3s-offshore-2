import simpy
import random
from scipy.stats import norm, expon
from collections import OrderedDict

def run_gspn_simulation(places, transitions):
    # Create the GSPN
    gspn = GeneralizedStochasticPetriNet(places=places, transitions=transitions)
    # Run the simulation
    print("Starting simulation...")
    gspn.run()
    print("Simulation complete.")
    
    # print(p)
    # print(t)
    return gspn.get_firing_sequence()

class GeneralizedStochasticPetriNet:
    def __init__(self, places, transitions):
        """
        Initialize the GSPN with user-defined places and transitions.

        Args:
            places (dict): A dictionary where keys are place names and values are the initial token counts.
            transitions (dict): A dictionary where keys are transition names and values are transition definitions.
                                Each transition is defined as:
                                {
                                    'type': 'immediate'|'fixed'|'stochastic',
                                    'priority': <priority for immediate transitions>,
                                    'fixed_time': <fixed delay for fixed transitions>,
                                    'rate': <rate for stochastic transitions>,
                                    'input': [list of input place names],
                                    'output': [list of output place names]
                                }
        """
        
        # Set up the SimPy environment
        self.env = simpy.Environment()

        # Places: Dictionary to hold token counts for each place
        self.places = places
        
        # Transitions: Define input/output places, type, rate, and priority
        self.transitions = transitions

        # Firing log: Dictionary where keys are transition names, and values are lists of firing times
        self.firing_log = {t: [] for t in self.transitions}
        
        # Firing Sequence: List of tuples to capture the firing order
        self.firing_sequence = []

    def can_fire(self, transition):
        """Check if a transition can fire (all input places have enough tokens)."""
        for place in self.transitions[transition]['input']:
            if self.places[place] == 0:
                return False
        return True

    def fire(self, transitions):
        """Fire a set of transitions simultaneously."""
        # Update tokens for all transitions in the batch
        for transition in transitions:
            for place in self.transitions[transition]['input']:
                self.places[place] -= 1
            for place in self.transitions[transition]['output']:
                self.places[place] += 1

            # Log the firing event
            self.firing_log[transition].append(self.env.now)
            self.firing_sequence.append((transition, self.env.now))  # Record in firing sequence
            print(f"Transition {transition} fired at time {self.env.now}. Current tokens: {self.places}")

    def get_enabled_transitions(self, transition_type):
        """Get all transitions of a given type that can fire."""
        return [
            t for t in self.transitions
            if self.transitions[t]['type'] == transition_type and self.can_fire(t)
        ]

    
    def sample_delay(self, transition):
        """
        Sample the delay for a transition based on its defined distribution.

        Args:
            transition (str): The name of the transition.

        Returns:
            float: The sampled delay.
        """
        distribution = self.transitions[transition].get('distribution', 'exponential')
        params = self.transitions[transition].get('params', {})

        if distribution == 'exponential':
            rate = params.get('rate', 1.0)
            return random.expovariate(rate)
        elif distribution == 'normal':
            mean = params.get('mean', 1.0)
            std_dev = params.get('std_dev', 0.1)
            return max(0, random.gauss(mean, std_dev))  # Ensure non-negative delay
        elif distribution == 'lognormal':
            mu = params.get('mu', 0.0)
            sigma = params.get('sigma', 1.0)
            return max(0, random.lognormvariate(mu, sigma))  # Ensure non-negative delay
        elif distribution == 'fixed':
            return self.transitions[transition].get('fixed_time', 0)
        else:
            raise ValueError(f"Unsupported distribution type: {distribution}")
        
    
    def simulate(self):
        """Simulate the GSPN."""
        while True:
            # Handle immediate transitions
            immediate_transitions = self.get_enabled_transitions('immediate')
            if immediate_transitions:
                max_priority = max(self.transitions[t]['priority'] for t in immediate_transitions)
                batch = [t for t in immediate_transitions if self.transitions[t]['priority'] == max_priority]
                self.fire(batch)
                yield self.env.timeout(0)  # Immediate transitions have no delay
                continue

            # Handle stochastic transitions
            stochastic_transitions = self.get_enabled_transitions('stochastic')
            if stochastic_transitions:
                batch = random.sample(stochastic_transitions, min(len(stochastic_transitions), 2))  # Example: max 2
                delays = [self.sample_delay(t) for t in batch]
                # delay = min(delays)  # Wait for the shortest delay
                delay = max(delays)  # Wait for the longest delay
                yield self.env.timeout(delay)
                self.fire(batch)
                continue

            # Handle fixed-time transitions
            fixed_transitions = self.get_enabled_transitions('fixed')
            if fixed_transitions:
                batch = random.sample(fixed_transitions, min(len(fixed_transitions), 2))  # Example: max 2
                delay = self.sample_delay(batch[0])
                yield self.env.timeout(delay)
                self.fire(batch)
                continue

            # If no transitions can fire, stop the simulation
            print("No transitions can fire. Stopping simulation.")
            break
    
        
    def get_firing_sequence(self):
        """Return the firing sequence as an ordered dictionary."""
        # Convert the firing sequence list into an ordered dictionary
        ordered_sequence = OrderedDict()
        for transition, time in self.firing_sequence:
            ordered_sequence[transition] = time
        return ordered_sequence
    
            
    # def get_ordered_firing_log(self):
    #     """Flatten and order the firing log by firing times."""
    #     all_events = [
    #         (transition, time)
    #         for transition, times in self.firing_log.items()
    #         for time in times
    #     ]
    #     # Sort by firing time
    #     all_events.sort(key=lambda x: x[1])

    #     # Convert to ordered dictionary for better readability
    #     ordered_log = OrderedDict()
    #     for transition, time in all_events:
    #         if transition not in ordered_log:
    #             ordered_log[transition] = []
    #         ordered_log[transition].append(time)

    #     return ordered_log

    def run(self):
        """Run the simulation using the internal environment."""
        self.env.process(self.simulate())
        self.env.run()
    
    
        
    
# from pm4py.objects.petri_net.obj import PetriNet
# class GeneralizedStochasticPetriNet:
#     def __init__(self, env, places, transitions):
#         self.env = env

#         # Places: Dictionary to hold token counts for each place
#         self.places = places
        
#         # Transitions: Define input/output places, type, rate, and priority
#         self.transitions = transitions

#         # Firing log: Dictionary where keys are transition names, and values are lists of firing times
#         self.firing_log = {t: [] for t in self.transitions}

#     def can_fire(self, transition):
#         """Check if a transition can fire (all input places have enough tokens)."""
#         for place in self.transitions[transition]['input']:
#             if self.places[place] == 0:
#                 return False
#         return True

#     def fire(self, transitions):
#         """Fire a set of transitions simultaneously."""
#         # Update tokens for all transitions in the batch
#         for transition in transitions:
#             for place in self.transitions[transition]['input']:
#                 self.places[place] -= 1
#             for place in self.transitions[transition]['output']:
#                 self.places[place] += 1

#             # Log the firing event
#             self.firing_log[transition].append(self.env.now)
#             print(f"Transition {transition} fired at time {self.env.now}. Current tokens: {self.places}")

#     def get_enabled_transitions(self, transition_type):
#         """Get all transitions of a given type that can fire."""
#         return [
#             t for t in self.transitions
#             if self.transitions[t]['type'] == transition_type and self.can_fire(t)
#         ]

#     def simulate(self):
#         """Simulate the GSPN."""
#         while True:
#             # Handle immediate transitions
#             immediate_transitions = self.get_enabled_transitions('immediate')
#             if immediate_transitions:
#                 # Sort by priority and fire all highest-priority transitions simultaneously
#                 max_priority = max(self.transitions[t]['priority'] for t in immediate_transitions)
#                 batch = [
#                     t for t in immediate_transitions if self.transitions[t]['priority'] == max_priority
#                 ]
#                 self.fire(batch)
#                 yield self.env.timeout(0)  # Immediate transitions have no delay
#                 continue

#             # Handle fixed-time transitions
#             fixed_transitions = self.get_enabled_transitions('fixed')
#             if fixed_transitions:
#                 # Randomly select a subset of fixed transitions to fire simultaneously
#                 batch = random.sample(fixed_transitions, min(len(fixed_transitions), 2))  # Example: max 2
#                 delay = self.transitions[batch[0]]['fixed_time']  # Assume same fixed time for batch
#                 yield self.env.timeout(delay)
#                 self.fire(batch)
#                 continue

#             # Handle stochastic transitions
#             stochastic_transitions = self.get_enabled_transitions('stochastic')
#             if stochastic_transitions:
#                 # Randomly select a subset of stochastic transitions to fire simultaneously
#                 batch = random.sample(stochastic_transitions, min(len(stochastic_transitions), 2))  # Example: max 2
#                 rate = self.transitions[batch[0]]['rate']  # Assume same rate for batch
#                 delay = random.expovariate(rate)
#                 yield self.env.timeout(delay)
#                 self.fire(batch)
#                 continue

#             # If no transitions can fire, stop the simulation
#             print("No transitions can fire. Stopping simulation.")
#             break













# import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# from pm4py.objects.petri_net.obj import PetriNet, Marking
# from pm4py.objects.petri_net.utils.petri_utils import add_arc_from_to


# import simpy
# import random


# class GeneralizedStochasticPetriNetPM4Py:
#     def __init__(self, env):
#         self.env = env

#         # Create PM4Py PetriNet object
#         self.net = PetriNet("GSPN")

#         # Define places
#         self.places = {
#             'P1': PetriNet.Place("P1"),
#             'P2': PetriNet.Place("P2"),
#             'P3': PetriNet.Place("P3"),
#             'P4': PetriNet.Place("P4"),
#         }
#         for place in self.places.values():
#             self.net.places.add(place)

#         # Define transitions
#         self.transitions = {
#             'T1': PetriNet.Transition("T1", None),
#             'T2': PetriNet.Transition("T2", None),
#         }
#         for transition in self.transitions.values():
#             self.net.transitions.add(transition)

#         # Add arcs
#         add_arc_from_to(self.net, self.places['P1'], self.transitions['T1'])
#         add_arc_from_to(self.net, self.places['P2'], self.transitions['T1'])
#         add_arc_from_to(self.net, self.transitions['T1'], self.places['P3'])
#         add_arc_from_to(self.net, self.places['P3'], self.transitions['T2'])
#         add_arc_from_to(self.net, self.transitions['T2'], self.places['P4'])

#         # Define initial marking
#         self.marking = Marking()
#         self.marking[self.places['P1']] = 1
#         self.marking[self.places['P2']] = 1

#         # Define transition types
#         self.transition_types = {
#             'T1': {'type': 'immediate', 'priority': 2},
#             'T2': {'type': 'timed', 'rate': 1.0},
#         }

#     def can_fire(self, transition):
#         """Check if a transition can fire based on the current marking."""
#         for arc in transition.in_arcs:
#             if self.marking[arc.source] == 0:
#                 return False
#         return True

#     def fire(self, transition):
#         """Fire a transition: update the marking."""
#         for arc in transition.in_arcs:
#             self.marking[arc.source] -= 1
#         for arc in transition.out_arcs:
#             self.marking[arc.target] += 1
#         print(f"Transition {transition.name} fired at time {self.env.now}. Marking: {self.marking}")

#     def simulate(self):
#         """Simulate the GSPN."""
#         while True:
#             # Check for enabled immediate transitions
#             immediate_transitions = [
#                 t for t in self.transitions.values()
#                 if self.transition_types[t.name]['type'] == 'immediate' and self.can_fire(t)
#             ]
#             if immediate_transitions:
#                 # Sort by priority
#                 immediate_transitions.sort(
#                     key=lambda t: self.transition_types[t.name]['priority'], reverse=True
#                 )
#                 chosen_transition = immediate_transitions[0]
#                 self.fire(chosen_transition)
#                 yield self.env.timeout(0)  # Immediate transitions have no delay
#                 continue

#             # Check for enabled timed transitions
#             timed_transitions = [
#                 t for t in self.transitions.values()
#                 if self.transition_types[t.name]['type'] == 'timed' and self.can_fire(t)
#             ]
#             if not timed_transitions:
#                 print("No transitions can fire. Stopping simulation.")
#                 break

#             # Choose one transition to fire based on rates
#             rates = [self.transition_types[t.name]['rate'] for t in timed_transitions]
#             chosen_transition = random.choices(timed_transitions, weights=rates, k=1)[0]

#             # Calculate the delay
#             delay = random.expovariate(self.transition_types[chosen_transition.name]['rate'])
#             yield self.env.timeout(delay)

#             # Fire the chosen transition
#             self.fire(chosen_transition)