
from collections import Counter


def orchestrate_search(
        embeddings_client, 
        db_client, 
        collection_name_str, 
        queries_array, 
        output_fields_arr, 
        return_limit, 
        MODEL_NAME, 
        DIMENSION
    ):
    vector_search_results = perform_vector_search(
        embeddings_client, 
        db_client, 
        collection_name_str, 
        queries_array, 
        output_fields_arr, 
        return_limit, 
        MODEL_NAME, 
        DIMENSION
    )
    vector_search_results_data = validate_and_extract_results_from_extralist(vector_search_results)
    # activity_ids_arr = gather_metadata_values_from_vector_search_results(vector_search_results_data)
    # scalar_search_results = perform_scalar_filtering(
    #     db_client,
    #     collection_name_str,
    #     activity_ids_arr,
    #     output_fields_arr
    # )

    return vector_search_results_data


def validate_and_extract_results_from_extralist(extralist):
    # we expect an ExtraList object with array in the 0 location
    if extralist and extralist[0]:
        results = extralist[0]
    else:
        raise ValueError(f"Search results data has unexpected structure. Unable to output results.")

    return results


def perform_vector_search(
        embeddings_client,
        milvus_client, 
        collection_name_str,  
        queries_array,
        output_fields_arr=["text"],
        return_limit=100,
        MODEL_NAME="", # if client method requires model name, be sure to set
        DIMENSION=0, # if client method requires dimensions, be sure to set
    ):
    
    # obtain vectors from SentenceTransformers model
    query_vectors = embeddings_client.encode_queries(queries_array)

    # obtain vectors from OpenAI model
    # query_vectors = [
    #     vec.embedding
    #     for vec in embeddings_client.embeddings.create(input=queries_array, model=MODEL_NAME, dimensions=DIMENSION).data
    # ]

    res = milvus_client.search(
        collection_name=collection_name_str, 
        data=query_vectors, 
        limit=return_limit,
        output_fields=output_fields_arr,
    )

    return res


def gather_metadata_values_from_vector_search_results(
        vector_search_results, 
        metadata_field="activity_reference_id",
        threshold=2
    ):

    if not isinstance(vector_search_results, list):
        raise ValueError("Function expects list datatype for search results.")

    metadata_field_values = [d['entity'][metadata_field] for d in vector_search_results] # get list of field values
    metadata_field_counts = Counter(metadata_field_values) # count occurences of each unique field value
    metadata_field_counts_filtered = {
            value: count for value, count 
            in metadata_field_counts.items() 
            if count >= threshold
        } # filter to include only field values meeting threshold

    metadata_field_values = []

    for metadata_field_value in metadata_field_counts_filtered.keys():
        metadata_field_values.append(metadata_field_value)

    return metadata_field_values
    

def perform_scalar_filtering(
        milvus_client, 
        collection_name_str,
        metadata_values_arr, 
        output_fields_arr=["text"],
        metadata_field="activity_reference_id"
    ):
    
    if not isinstance(metadata_values_arr, list):
        raise ValueError("Function expects list datatype for metadata values.")

    query_filter = f"'{metadata_field}' in {metadata_values_arr}"

    res = milvus_client.query(
        collection_name=collection_name_str,
        filter=query_filter,
        output_fields=output_fields_arr
    )

    return res


def combine_and_dedup_results():
    pass