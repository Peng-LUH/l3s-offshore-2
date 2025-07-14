# dynamics.py
from typing import Dict, Any, Optional
from gspn4py.core.models.base import BasePetriNet

def set_initial_dynamics(net: BasePetriNet, initial_dynamics: Dict[str, Any]) -> None:
    """Initialize markings, firing times, priorities, and resources."""
    # Handle initial marking
    if 'm0' in initial_dynamics:
        net.set_initial_marking(initial_dynamics['m0'])
    
    # Handle firing times (default: empty)
    firing_times = initial_dynamics.get('ft', {})
    net.set_firing_times(firing_times)
    
    # Handle priorities (default: zeros)
    priorities = initial_dynamics.get('ip', {t.name: 0 for t in net.transitions})
    net.set_priorities(priorities)
    
    # Handle resources (default: empty)
    if 're' in initial_dynamics:
        net.allocate_resources(initial_dynamics['re'])
    