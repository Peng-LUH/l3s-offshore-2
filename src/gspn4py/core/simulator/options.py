from typing import Optional, Dict, Any, Union
import time
import numpy as np

class GlobalOptions:
    
    PRINT_LOOP_NUMBER: int
    MAX_LOOP: int
    DELTA_TIME: Optional[float]
    REAL_TIME: bool
    START_AT: Optional[Union[float, tuple]]
    STOP_AT: Optional[Union[float, tuple]]
    FIRING_SEQ: Optional[list]
    FS_REPEAT: int
    FS_ALLOW_PARALLEL: bool
    FS_Current_Ptr: int
    FS_Repeat_Count: int

    def __init__(self):
        self.PRINT_LOOP_NUMBER = 0
        self.MAX_LOOP = 200
        self.DELTA_TIME = None
        self.REAL_TIME = False
        self.START_AT = None
        self.STOP_AT = None
        self.FIRING_SEQ = None
        self.FS_REPEAT = 1
        self.FS_ALLOW_PARALLEL = False
        self.FS_Current_Ptr = 1
        self.FS_Repeat_Count = 1

    """Class to hold global simulation options"""
    def __init__(self):
        self.PRINT_LOOP_NUMBER = 0
        self.MAX_LOOP = 200
        self.DELTA_TIME: Optional[float] = None
        self.REAL_TIME = False
        self.START_AT: Optional[Union[float, tuple]] = None
        self.STOP_AT: Optional[Union[float, tuple]] = None
        self.FIRING_SEQ: Optional[list] = None
        self.FS_REPEAT = 1
        self.FS_ALLOW_PARALLEL = False
        self.FS_Current_Ptr = 1
        self.FS_Repeat_Count = 1

def set_options(pn: 'EnhancedPetriNet', global_info: Optional[Dict[str, Any]] = None) -> None:
    """
    Handle simulation options like MAX_LOOP, DELTA_TIME, etc.
    
    Args:
        pn: The Petri net instance
        global_info: Dictionary containing simulation options
        
    Returns:
        None (modifies the Petri net and global_info in place)
    """
    if global_info is None:
        global_info = {}
    
    # Initialize default values if not provided
    global_info.setdefault('PRINT_LOOP_NUMBER', 0)
    global_info.setdefault('MAX_LOOP', 200)
    
    # Handle delta time
    pn.delta_T = global_info.get('DELTA_TIME', float('nan'))
    
    # Process real-time settings
    if 'REAL_TIME' in global_info:
        global_info['START_AT'] = current_clock()
        pn.REAL_TIME = True
        pn.REAL_TIME_PREV_X = np.zeros(pn.No_of_places)
    else:
        pn.REAL_TIME = False
    
    # Process time format and starting time
    pn.HH_MM_SS = False  # Hour-Min-Sec flag
    
    if 'START_AT' in global_info:
        start_time = set_options_start_time(global_info['START_AT'])
    else:
        start_time = 0.0
    pn.current_time = start_time
    
    # Process stop time
    if 'STOP_AT' in global_info:
        stop_time = set_options_stop_time(global_info['STOP_AT'])
    else:
        stop_time = float('nan')
    pn.STOP_TIME = stop_time
    
    # Process firing sequence
    if 'FIRING_SEQ' in global_info:
        # Convert transition names to indices
        global_info['FIRING_SEQ'] = check_valid_transition(pn, global_info['FIRING_SEQ'])
        
        global_info.setdefault('FS_REPEAT', 1)
        global_info['FS_Repeat_Count'] = 1
        global_info.setdefault('FS_ALLOW_PARALLEL', False)
        global_info['FS_Current_Ptr'] = 1

# Helper functions
def current_clock() -> tuple:
    """Get current time as (hour, minute, second) tuple"""
    now = time.localtime()
    return (now.tm_hour, now.tm_min, now.tm_sec)

def set_options_start_time(start_at: Union[float, tuple]) -> float:
    """Convert start time to seconds if in HH:MM:SS format"""
    if isinstance(start_at, tuple) and len(start_at) == 3:
        return start_at[0] * 3600 + start_at[1] * 60 + start_at[2]
    return float(start_at)

def set_options_stop_time(stop_at: Union[float, tuple]) -> float:
    """Convert stop time to seconds if in HH:MM:SS format"""
    if isinstance(stop_at, tuple) and len(stop_at) == 3:
        return stop_at[0] * 3600 + stop_at[1] * 60 + stop_at[2]
    return float(stop_at)

def check_valid_transition(pn: 'EnhancedPetriNet', firing_seq: list) -> list:
    """Validate transition names in firing sequence and return indices"""
    valid_transitions = {t.name: idx for idx, t in enumerate(pn.transitions)}
    result = []
    
    for trans in firing_seq:
        if trans not in valid_transitions:
            raise ValueError(f"Invalid transition name in firing sequence: {trans}")
        result.append(valid_transitions[trans])
    
    return result

class SimulationOptions:
    """Wrapper class around GlobalOptions for use in SimulationEngine."""
    def __init__(self, global_options: Optional[GlobalOptions] = None):
        self._global = global_options or GlobalOptions()

    @property
    def MAX_LOOP(self):
        return self._global.MAX_LOOP

    @MAX_LOOP.setter
    def MAX_LOOP(self, value):
        self._global.MAX_LOOP = value

