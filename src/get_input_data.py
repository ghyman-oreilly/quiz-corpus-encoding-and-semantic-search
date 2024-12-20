
from helpers import (
        convert_to_posix_path, 
        validate_posix_path, 
        validate_posix_path_to_file, 
        generate_timestamp
    )
import json
import sys


def get_and_validate_file():
    """Prompt the user for a file path and validate existence of file."""
    
    counter = 0
    
    while True and counter < 3:
        file_path = input("Please enter the path to the JSON file: ")
        path = convert_to_posix_path(file_path)
        
        if not validate_posix_path(path):
            continue
        
        if not validate_posix_path_to_file(path):
            continue

        counter += 1

        print(f"File at following path successfully loaded: {path}")
        return path  # Return the file path

    print('Max number of attempts reached. Exiting.')
    sys.exit()


def get_dir_path():

    counter = 0
    
    while True and counter < 3:
        output_path = input("Please enter the path to the output directory: ")
        output_posix_path = convert_to_posix_path(output_path)
        
        if not output_posix_path.is_dir():
            print("Invalid path to directory.")
            continue
        
        counter += 1


        return output_posix_path  # Return the path

    print('Max number of attempts reached. Exiting.')
    sys.exit()


def load_json(path):
    """Validate input file as JSON."""
    
    counter = 0
    
    while True and counter < 3:
        # Check if the file contains valid JSON
        try:
            with path.open('r', encoding='utf-8') as file:
                data = json.load(file)  # Attempt to load the file as JSON
        except json.JSONDecodeError as e:
            print(f"Error: The file does not contain valid JSON: {e}")
            path = get_and_validate_file()
            continue

        counter += 1

        print(f"JSON file successfully loaded.")
        return data  # Return the loaded JSON data

    print('Max number of attempts reached. Exiting.')
    sys.exit()


def validate_json_structure(
        data, 
        REQUIRED_FIELDS = [
        'item_reference_id', 
        'question_reference_id', 
        'question_stimulus', 
        'question_options', 
        'valid_response_values', 
        'question_rationales'
        ]
    ):

    if not isinstance(data, list):
        raise ValueError("The JSON file must contain a list (array) of objects.")
    
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {index} is not a valid JSON object (must be a dictionary).")

        missing_fields = [field for field in REQUIRED_FIELDS if field not in item]
        if missing_fields:
            raise ValueError(f"Item at index {index} is missing the following required fields: {missing_fields}")
        

def get_queries(queries_array=[]):
    
    if len(queries_array) == 0: 
        query = input("Please input your search query: ")
    else:
        query = input("Please input your additional search query to append: ")

    if query and query != '':
        queries_array.append(query)

    add_query = input("Do you wish to append an additional query to the search? (y/n)")

    if add_query.lower() in ['y', 'yes']:
        get_queries(queries_array)
    
    return queries_array


def get_database_info(filestub="vector_store_", counter=0):
    counter += counter
    db_path = input("Enter the path to the database file you wish to use (provide dir path to create a new one): ")
    path = convert_to_posix_path(db_path)
    timestamp_milliseconds = generate_timestamp()

    if validate_posix_path(path) and not validate_posix_path_to_file(path):
        # dir path provided
        filename = filestub + str(timestamp_milliseconds) + ".db"
        path = path / filename
        path.touch(exist_ok=True)
        is_new_db=True
        print(f"Directory path provided. Database created at: {path}")
        return is_new_db, path
    elif validate_posix_path_to_file(path) and path.suffix == ".db":
        # valid existing database
        is_new_db=False
        return is_new_db, path
    else:      
        # invalid path
        print("Valid dir path or .db filepath not found.")
        if counter < 3:
            get_database_info(counter)
        else:
            print("Max attempts tried. Exiting.")
            sys.exit()
        