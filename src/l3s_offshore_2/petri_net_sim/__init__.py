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