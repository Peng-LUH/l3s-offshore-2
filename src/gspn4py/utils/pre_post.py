from typing import Dict, List, Optional, Any
from pathlib import Path
import importlib
import sys
from gspn4py.core.models.base import BasePetriNet

class PrePostManager:
    """Manages PRE/POST file registration and execution for EnhancedPetriNet."""
    
    def __init__(self, petri_net: BasePetriNet):
        self.net = petri_net
        self.search_paths = [Path.cwd()]  # Default search path
        
        # File existence tracking
        self.PRE_exist: List[bool] = []
        self.POST_exist: List[bool] = []
        self.MOD_PRE_exist: List[bool] = []
        self.MOD_POST_exist: List[bool] = []
        self.COMMON_PRE: bool = False
        self.COMMON_POST: bool = False
        
        # Module caching
        self._pre_cache: Dict[str, Any] = {}
        self._post_cache: Dict[str, Any] = {}

    def add_search_path(self, path: str) -> None:
        """Add additional directory to search for PRE/POST files."""
        self.search_paths.append(Path(path))

    def register_files(self) -> None:
        """Scan and register all PRE/POST files."""
        # Transition-specific files
        sorted_trans = sorted(self.net.transitions, key=lambda x: x.name)
        self.PRE_exist = [self._check_file_exists(f"{t.name}_pre.py") for t in sorted_trans]
        self.POST_exist = [self._check_file_exists(f"{t.name}_post.py") for t in sorted_trans]

        # Module-specific files
        if hasattr(self.net, 'module_names'):
            self.MOD_PRE_exist = [
                self._check_file_exists(f"MOD_{m}_PRE.py") 
                for m in self.net.module_names
            ]
            self.MOD_POST_exist = [
                self._check_file_exists(f"MOD_{m}_POST.py") 
                for m in self.net.module_names
            ]

        # Common files
        self.COMMON_PRE = self._check_file_exists("COMMON_PRE.py")
        self.COMMON_POST = self._check_file_exists("COMMON_POST.py")

    def execute_pre(self, transition_name: str) -> bool:
        """
        Execute PRE script for a transition.
        Returns True if transition should fire, False to block.
        """
        trans_idx = next(
            (i for i, t in enumerate(sorted(self.net.transitions, key=lambda x: x.name)) 
            if t.name == transition_name),
            None
        )
        
        if trans_idx is None or not self.PRE_exist[trans_idx]:
            return True
            
        try:
            module = self._load_module(f"{transition_name}_pre")
            return module.validate(self.net)  # Expected interface
        except Exception as e:
            raise RuntimeError(
                f"PRE script execution failed for {transition_name}: {str(e)}")

    def _check_file_exists(self, filename: str) -> bool:
        """Check if file exists in search paths."""
        return any((path / filename).exists() for path in self.search_paths)

    def _load_module(self, module_name: str) -> Any:
        """Dynamically load a Python module from file."""
        # Remove .py if present
        module_name = module_name.replace('.py', '')
        
        # Check cache first
        if module_name in self._pre_cache:
            return self._pre_cache[module_name]
        if module_name in self._post_cache:
            return self._post_cache[module_name]
            
        # Find the physical file
        for path in self.search_paths:
            file_path = path / f"{module_name}.py"
            if file_path.exists():
                # Special import logic
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Cache the module
                if "_pre" in module_name:
                    self._pre_cache[module_name] = module
                else:
                    self._post_cache[module_name] = module
                
                return module
                
        raise FileNotFoundError(f"Module {module_name} not found in search paths")