
from helpers import convert_to_posix_path, validate_posix_path_to_file
from pathlib import Path
import json



def load_config():
    
    config_filename = "config.json"
    current_dir = Path(__file__).parent.resolve()
    config_filepath = current_dir / config_filename
    config_file_posix_path = convert_to_posix_path(config_filepath)

    if validate_posix_path_to_file(config_file_posix_path):
        try:
            with config_file_posix_path.open('r', encoding='utf-8') as file:
                config = json.load(file)  # Attempt to load the file as JSON
        except json.JSONDecodeError as e:
            print(f"Error: The file does not contain valid JSON: {e}")
    else:
        raise ValueError("Valid config.json file not found.")
    
    return config

