# from typing import Dict, Any, Optional
# from copy import deepcopy
# import warnings
# from gspn4py.core.models.petri_net import BasePetriNet
# from gspn4py.core.simulator.dynamics import set_initial_dynamics


# class DynamicsInitializer:
#     """Handles initialization of Petri net dynamics (markings, firing times, etc.)"""
    
#     @staticmethod
#     def initialize(net: BasePetriNet,
#                   dynamics: Optional[Dict[str, Any]] = None) -> BasePetriNet:
#         """
#         Combines static Petri net structure with initial dynamics.
        
#         Args:
#             net: The static Petri net (from builder)
#             dynamics: Dictionary containing dynamics configuration with keys:
#                 - 'initial_marking': {place_name: tokens}
#                 - 'firing_times': {transition_name: (min, max)}
#                 - 'priorities': {transition_name: priority}
#                 - 'resources': {resource_name: quantity}
                
#         Returns:
#             Initialized Petri net ready for simulation
#         """
#         if dynamics is None:
#             warnings.warn("No dynamics provided - using empty initialization")
#             dynamics = {}
        
#         # Create a deep copy to maintain structural immutability
#         initialized_net = deepcopy(net)
        
#         # Convert to internal format expected by set_initial_dynamics
#         internal_dynamics = {
#             'm0': dynamics.get('initial_marking', {}),
#             'ft': dynamics.get('firing_times', {}),
#             'ip': dynamics.get('priorities', {}),
#             're': dynamics.get('resources', {})
#         }
        
#         # Apply all dynamics at once using the centralized function
#         set_initial_dynamics(initialized_net, internal_dynamics)
        
#         return initialized_net
        
    # @staticmethod
    # def from_matlab_style(net: BasePetriNet,
    #                      matlab_dynamics: Dict[str, Any]) -> BasePetriNet:
    #     """
    #     Alternative initializer for MATLAB-style dynamics dictionaries.
    #     Maintains compatibility with existing MATLAB-defined configurations.
        
    #     Args:
    #         net: The static Petri net
    #         matlab_dynamics: Dictionary with MATLAB-style keys:
    #             - 'm0': Initial marking
    #             - 'ft': Firing times  
    #             - 'ip': Priorities
    #             - 're': Resources
                
    #     Returns:
    #         Initialized Petri net
    #     """
    #     initialized_net = deepcopy(net)
    #     set_initial_dynamics(initialized_net, matlab_dynamics)
    #     return initialized_net