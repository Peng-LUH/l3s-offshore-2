import json
# import os
from pathlib import Path

def import_pndf_from_json(json_file_path):
    # check if the file path is valid
    path_obj = Path(json_file_path)
    
    if not path_obj.exists():
        raise FileNotFoundError(f"File does not exist: {json_file_path}")
    
    if not path_obj.is_file():
        raise FileNotFoundError(f"Path is not a file: {json_file_path}")
    
    if path_obj.is_dir():
        raise IsADirectoryError(f"Path is a directory: {json_file_path}")
    
    if path_obj.suffix.lower() != '.json':
        raise ValueError(f"File is not a JSON file: {json_file_path}")
    
   
    with open(json_file_path, "r") as f:
        pndf = json.load(f)
        
    return pndf
    
    