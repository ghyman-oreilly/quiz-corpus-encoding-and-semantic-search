from get_input_data import (
        get_and_validate_file, 
        get_dir_path, 
        load_json, 
        validate_json_structure, 
        get_queries, 
        get_database_info
    )
from helpers import (
        get_dir_path_from_filepath, 
        generate_filepath, 
        write_array_data_to_file, 
        validate_posix_path_to_file
    )
from prepare_vector_data import (
        get_database, 
        prepare_fields_for_embedding, 
        generate_and_store_embeddings
    )
from pymilvus import model
from search import orchestrate_search
# from openai import OpenAI


def main():
    # oai_api_key = load_config().get("api_key")
    collection_name_str = "quiz_items"
    metadata_fields = [
        "item_reference_id", 
        "question_reference_id", 
        "question_stimulus",
        "question_options",
        "question_rationales",
        "valid_response_values",
        "activity_reference_id", 
        "activity_title"
        ]
    output_fields_arr = metadata_fields
    return_limit = 500
    queries_array = []

    is_new_db, db_path = get_database_info()

    if not validate_posix_path_to_file(db_path):
        raise ValueError("Error: Database file does not exist.")
    
    
    MODEL_NAME = "multi-qa-mpnet-base-dot-v1"
    DIMENSION = 768 # make sure this matches actual/allowable model dimensions
    BATCH_SIZE = 1000 # indicates number of docs sent for embedding at one time (for progress logging purposes)

    embeddings_client = model.dense.SentenceTransformerEmbeddingFunction(
        model_name=MODEL_NAME,
        batch_size=32,
        query_instruction="",
        doc_instruction="",
        device="cpu",
        normalize_embeddings=True,
    )
    # embeddings_client = OpenAI(api_key=oai_api_key)

    db_client = get_database(collection_name_str, db_path, DIMENSION)
    

    if is_new_db:
        file_path = get_and_validate_file()
        json_data = load_json(file_path)
        validate_json_structure(json_data)
        output_directory = get_dir_path_from_filepath(file_path)
        text_array, metadata_array = prepare_fields_for_embedding(json_data, metadata_fields)
        generate_and_store_embeddings(
                embeddings_client, 
                db_client, 
                collection_name_str, 
                text_array, 
                metadata_array, 
                BATCH_SIZE,
                MODEL_NAME, 
                DIMENSION
            )
    else:
        output_directory = get_dir_path()

    queries_array = queries_array + get_queries()
    output_filepath = generate_filepath(output_directory, "results_", "json")   
    search_results = orchestrate_search(
        embeddings_client, 
        db_client, 
        collection_name_str, 
        queries_array, 
        output_fields_arr, 
        return_limit, 
        MODEL_NAME, 
        DIMENSION
    )

    if search_results:
        write_array_data_to_file(search_results, output_filepath)

    db_client.close() # close client connection to DB

    print("Script complete.")

main()