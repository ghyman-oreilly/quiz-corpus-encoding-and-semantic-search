from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType
from transformers import AutoTokenizer


def get_database(collection_name_str, db_uri, DIMENSION):
    db_uri = str(db_uri)
    client = MilvusClient(uri=db_uri)
    
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION)
    ]

    schema = CollectionSchema(fields=fields, enable_dynamic_field=True)
    
    if not client.has_collection(collection_name=collection_name_str):
        client.create_collection(collection_name=collection_name_str, schema=schema)
        # client.create_collection(collection_name=collection_name_str, enable_dynamic_field=True, dimension=DIMENSION)
        index_params = client.prepare_index_params()
        index_params.add_index(field_name="vector", index_type="FLAT", metric_type="COSINE")
        client.create_index(collection_name_str, index_params)

    return client


def prepare_fields_for_embedding(json_data_array, metadata_fields=[]):
    
    text_array = []
    metadata_array = []

    for question in json_data_array:
        text = ""
        metadata = []
        
        if question.get('question_stimulus'):
            text = text + question.get('question_stimulus')

        if question.get('question_options'):
            for option in question.get('question_options'):
                if option.get('label'):
                    text = text + "\n" + option.get('label')
        
        if question.get('question_rationales'):
            rationales_str = "\n".join(map(str, question.get('question_rationales')))
            text + "\n" + rationales_str
        
        if len(metadata_fields) > 0:
            for field in metadata_fields:
                value = question.get(field, None)
                metadata.append({field: value})
            metadata_array.append(metadata)
        
        text_array.append(text)

    if len(metadata_array) != 0 and len(text_array) != len(metadata_array):
        raise ValueError("Length of text array does not match length of metadata array.")

    return text_array, metadata_array


def generate_and_store_embeddings(
        embeddings_client, 
        milvus_client, 
        collection_name_str, 
        text_array, 
        metadata_array=[], 
        batch_size=1000, 
        MODEL_NAME="", # if client method requires model name, be sure to set
        DIMENSION=0 # if client method requires dimensions, be sure to set
    ):

    if len(metadata_array) != 0 and len(text_array) != len(metadata_array):
        raise ValueError("Length of text array does not match length of metadata array.")

    print("Encoding documents...")

    for batch_start in range(0, len(text_array), batch_size):
        data = [] # clear array for each iteration
        batch_end = batch_start + batch_size
        text_batch = text_array[batch_start:batch_end]
        metadata_batch = metadata_array[batch_start:batch_end] if len(metadata_array) > 0 else []

        # obtain vectors from SentenceTransformers model
        vectors = embeddings_client.encode_documents(text_batch) 

        # obtain vectors from OpenAI model
        # vectors = [
        #     vec.embedding
        #     for vec in embeddings_client.embeddings.create(input=text_batch, model=MODEL_NAME, dimensions=DIMENSION).data
        # ]

        if len(vectors) != len(text_batch) or len(text_batch) != len(metadata_batch):
            raise ValueError("Length of vectors list doesn't match text_batch, or text_batch length doesn't match metadata_batch.")

        for i, _ in enumerate(text_batch):
            item_data = { "vector": vectors[i] }
            
            # Add metadata fields if present
            if len(metadata_batch) > 0:
                for metadata_dict in metadata_batch[i]:
                    for field, value in metadata_dict.items():
                        item_data[field] = value
            
            data.append(item_data)

        # Insert the current batch into the Milvus vector store
        milvus_client.insert(collection_name=collection_name_str, data=data)
        print(f"Inserted batch {batch_start} to {batch_end} of {len(text_array)} documents into vector database.")


def estimate_total_tokens_sentence_transformers(text_array, MODEL_NAME):
    model_name=f"sentence-transformers/{MODEL_NAME}"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    total_tokens = sum(len(tokenizer(text, truncation=True, padding=False)['input_ids']) for text in text_array)
    return total_tokens
