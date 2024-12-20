
import json
from pathlib import Path
import time


def convert_to_posix_path(path):
    path = Path(path)

    return path


def validate_posix_path(posix_path, verbose=False):
    """Check if the path exists"""
    
    if not posix_path.exists():
        if verbose:
            print(f"Error: Invalid path: {posix_path}")
        return False
    return True


def validate_posix_path_to_file(posix_path, verbose=False):
    """Check if path is a filepath"""
    
    if not posix_path.is_file():
        if verbose:
            print(f"Error: File not found at: {posix_path}")
        return False
    return True


def get_dir_path_from_filepath(posix_path):
    """Get directory path from POSIX filepath"""
    
    if validate_posix_path_to_file(posix_path):
        directory_path = posix_path.parent
    elif validate_posix_path(posix_path):
        directory_path = posix_path
    else:
        raise ValueError(f"Error: Input to function is not a valid POSIX path: {posix_path}")

    return directory_path
    

def generate_timestamp():
    timestamp_milliseconds = int(time.time() * 1000)
    return timestamp_milliseconds


def generate_filepath(posix_path, filename_stub="output_", extension="txt"):
    """ Generate filepath from arguments."""

    if not validate_posix_path(posix_path):
        raise ValueError(f"Error: Input to function is not a valid POSIX directory path: {posix_path}")
    
    extension = extension.lower()
    valid_extensions = ["txt", "csv", "tsv", "json"]

    if not extension in valid_extensions:
        raise ValueError(f"Extension passed to function must be one of the following: {valid_extensions}")

    timestamp_milliseconds = generate_timestamp()
    output_file_string = f"{filename_stub}{timestamp_milliseconds}.{extension}"

    file_path = posix_path / output_file_string

    return file_path


def write_array_data_to_file(data_array, output_file):

    if not isinstance(data_array, list):
        raise ValueError(f"Data passed to function must be a list/array.")

    with open(output_file, 'w', encoding='utf-8') as f:
        array_length = len(data_array)
        f.write("[")
        for index, item in enumerate(data_array):
            item = json.dumps(item)
            f.write(item)
            if not array_length - index == 1:
                f.write(",\n")
        f.write("]")

    print(f"Data written to: {output_file}")

