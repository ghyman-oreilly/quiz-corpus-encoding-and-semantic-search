# Quizzes Semantic Search

This app uses a local Milvus Lite vector store and a SentenceTransformers embedding model to perform semantic search on a corpus of quiz documents with a known/expected format. 

## Setting Up to Run the App

1. Create and activate a virtual environment:
    
    `python -m venv venv`

    `source venv/bin/activate`

2. Install dependencies into virtual environment, from requirements.txt:

    `pip install -r requirements.txt`

## Running the App

1. With the virtual environment activated, from the project root, run the following command:

    `python src/main.py`

2. Follow the prompts. You'll have an opportunity to use an existing vector store or to create a new one.
If creating a new store, see the `data/samples/input_format.json` file for the expected document input structure.

3. The results of your query will be outputted to the specified location. See `data/samples/output_format.json` for the structure of the output you can expect.

> **Note:** If creating a new store in Step 2, expect the encoding and inserting process to take ~1 second per 1,500-1,750 tokens on a modern CPU, or ~20 minutes for a 2M token corpus, which was the corpus size used in testing the app. Using a GPU or different embedding models may improve performance, though the current model performed as well as several others in testing. Once the store is created, querying is quite fast.