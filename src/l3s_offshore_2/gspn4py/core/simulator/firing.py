import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from collections import deque

@dataclass
class FiringEvent:
    transition_id: int
    delta_marking: np.ndarray
    completion_time: float
    colors: List[str] = None
    cost: float = 0.0
    start_state: int = 0

class PetriNetFiring:
    def __init__(self, petri_net):
        """Initialize firing handler with reference to parent Petri net."""
        self.net = petri_net
        self.events_in_progress = deque()
        self._current_state = 0
        
    def start_firing(self, transition_id: int) -> Optional[FiringEvent]:
        """Initiate a transition firing.
        
        Args:
            transition_id: ID of transition to fire
            
        Returns:
            FiringEvent if successful, None otherwise
        """
        if not self._validate_firing(transition_id):
            return None
            
        firing_time = self._get_firing_time(transition_id)
        delta_marking = self._calculate_delta_marking(transition_id)
        
        event = FiringEvent(
            transition_id=transition_id,
            delta_marking=delta_marking,
            completion_time=self.net.current_time + firing_time,
            start_state=self._current_state
        )
        
        self.events_in_progress.append(event)
        self.net.transitions[transition_id].firing = True
        return event

    def complete_firings(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, List[str]]]]:
        """Process all completed firings.
        
        Returns:
            Tuple of (logs, color_maps) where:
            - logs: List of firing records
            - color_maps: List of color states
        """
        completed_logs = []
        completed_colors = []
        
        while self.events_in_progress:
            event = self.events_in_progress[0]
            if event.completion_time > self.net.current_time:
                break
                
            event = self.events_in_progress.popleft()
            log, colors = self._complete_single_firing(event)
            completed_logs.append(log)
            completed_colors.append(colors)
            
        return completed_logs, completed_colors

    def _complete_single_firing(self, event: FiringEvent) -> Tuple[Dict[str, Any], Dict[str, List[str]]]:
        """Complete a single transition firing.
        
        Args:
            event: FiringEvent to complete
            
        Returns:
            Tuple of (log_entry, color_state)
        """
        trans = self.net.transitions[event.transition_id]
        
        # Update markings
        self.net.marking += event.delta_marking
        self.net.virtual_marking -= trans.absorbed_tokens
        trans.absorbed_tokens = np.zeros(self.net.place_count)
        
        # Handle token deposits
        for place_idx, delta in enumerate(event.delta_marking):
            if delta > 0:
                self._deposit_tokens(place_idx, delta, event.colors, event.cost)
        
        # Update state and counters
        trans.times_fired += 1
        self._current_state += 1
        trans.firing = False
        
        # Create log entry
        log_entry = {
            'marking': self.net.marking.copy(),
            'transition': event.transition_id,
            'state': self._current_state,
            'start_state': event.start_state,
            'start_time': event.completion_time - self._get_firing_time(event.transition_id),
            'end_time': event.completion_time,
            'virtual_marking': self.net.virtual_marking.copy()
        }
        
        # Execute post-actions
        self._execute_post_actions(event.transition_id)
        
        return log_entry, self._get_current_colors()
    
    def _get_current_colors(self) -> Dict[str, List[str]]:
        """Snapshot current color state.
        
        Returns:
            Dictionary mapping place names to their color lists
        """
        return {
            place.name: place.colors 
            for place in self.net.places
            if hasattr(place, 'colors')
        }
        
    def _deposit_tokens(self, place_idx: int, count: int, 
                       colors: Optional[List[str]], cost: float) -> None:
        """Handle token deposits with colors and costs.
        
        Args:
            place_idx: Index of place to deposit tokens
            count: Number of tokens to deposit
            colors: Optional list of colors for tokens
            cost: Cost associated with tokens
        """
        place = self.net.places[place_idx]
        if colors:
            if not hasattr(place, 'colors'):
                place.colors = []
            place.colors.extend(colors[:count])
            
        if cost != 0:
            if not hasattr(place, 'token_costs'):
                place.token_costs = []
            place.token_costs.extend([cost] * count)
    
    def _validate_firing(self, transition_id: int) -> bool:
        """Check if transition can fire.
        
        Args:
            transition_id: ID of transition to validate
            
        Returns:
            True if transition can fire, False otherwise
        """
        trans = self.net.transitions[transition_id]
        return (not trans.firing and 
                self.net.is_enabled(transition_id) and
                self._check_preconditions(transition_id))

    def _check_preconditions(self, transition_id: int) -> bool:
        """Check transition-specific preconditions.
        
        Args:
            transition_id: ID of transition to check
            
        Returns:
            True if preconditions are satisfied
        """
        if self.net.pre_post_manager:
            return self.net.pre_post_manager.execute_pre(
                self.net.transitions[transition_id].name
            )
        return True

    def _get_firing_time(self, transition_id: int) -> float:
        """Get firing duration with stochastic support.
        
        Args:
            transition_id: ID of transition
            
        Returns:
            Firing duration as float
        """
        trans = self.net.transitions[transition_id]
        if isinstance(trans.firing_time, str):
            return self._safe_eval_firing_time(trans.firing_time)
        return trans.firing_time

    def _safe_eval_firing_time(self, expr: str) -> float:
        """Safely evaluate stochastic firing time expressions.
        
        Args:
            expr: String expression to evaluate
            
        Returns:
            Evaluated numeric result
            
        Raises:
            ValueError: If expression is invalid or unsafe
        """
        # Implement safe evaluation - example stub
        allowed = {'unifrnd', 'normrnd', 'exp', 'log', 'sin', 'cos', 'pi'}
        # Add proper validation and sandboxing here
        try:
            return float(eval(expr, {'__builtins__': None}, allowed))
        except Exception as e:
            raise ValueError(f"Invalid firing time expression: {expr}") from e

    def _calculate_delta_marking(self, transition_id: int) -> np.ndarray:
        """Calculate marking change from transition firing.
        
        Args:
            transition_id: ID of firing transition
            
        Returns:
            Numpy array of token changes per place
        """
        # Implement based on your incidence matrix
        # Example: return Dp - Dm for the transition
        _, D, _ = self.net.split_incidence_matrix()
        return D[transition_id, :]
        
    def _execute_post_actions(self, transition_id: int) -> None:
        """Execute post-firing actions.
        
        Args:
            transition_id: ID of completed transition
        """
        if self.net.pre_post_manager:
            self.net.pre_post_manager.execute_post(
                self.net.transitions[transition_id].name
            )