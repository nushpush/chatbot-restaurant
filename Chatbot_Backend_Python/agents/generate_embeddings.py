import requests
import json
import os
from openai import AzureOpenAI
from langchain_community.vectorstores.azuresearch import AzureSearch
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import redis
import numpy as np
 
# from sklearn.decomposition import PCA
 
 
azure_search_endpoint = "https://genaipocllmsearch.search.windows.net"
azure_search_index_name = "qsr-chef"
azure_search_api_key = "kB4ez5gc3g2McSC4PnWzcfXdzoAJyJYseWmqqtk9eKAzSeA8zh9V"
 
search_client = SearchClient(
    endpoint=azure_search_endpoint,
    index_name=azure_search_index_name,
    credential=AzureKeyCredential(azure_search_api_key),
)
print("search_client", search_client)
# from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
 
 
# Configuration
# azure_base_url = "https://genai-usecasesforswe-modernization.openai.azure.com"
# azure_deployment_name = "genai4swemodernizationembeddingmodel"
# azure_api_key = "7ce0a3e988834cdc8b93a968f4e6c7bc"
 
client = AzureOpenAI(
    api_key="7ce0a3e988834cdc8b93a968f4e6c7bc",
    api_version="2024-02-15-preview",
    azure_endpoint="https://genai-usecasesforswe-modernization.openai.azure.com",
)
 
# Redis Cache setup
redis_host = "genAIbusiness.redis.cache.windows.net"
redis_port = 6380
redis_password = "iBucMF8eX6TMgfNJhelrC10XvLHrfdTk1AzCaAWkNF0="
redis_client = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    ssl=True,
    decode_responses=True,
)
 
# Embedding Generation Function
# def generate_embeddings(text_chunk, model="genai4swemodernizationembeddingmodel"):
#     try:
#         response = client.embeddings.create(input=[text_chunk], model=model)
#         return response.data[0].embedding
#     except Exception as e:
#         print(f"Error generating embeddings: {e}")
#         return None
 
# def generate_embeddings(text_chunk, model="genai4swemodernizationembeddingmodel"):
#     print("Generating embeddings",text_chunk)
#     response = client.embeddings.create(input=[text_chunk], model=model)
#     print("responseee",response)
#     return response.data[0].embedding
 
 
 
def generate_embeddings(text_chunk, model="genai4swemodernizationembeddingmodel"):
    response = client.embeddings.create(input=[text_chunk], model=model)
    return response.data[0].embedding
 
 
def preprocess_text(text):
    return json.dumps(json.loads(text), separators=(",", ":"))
 
# def save_results_to_file(results, output_filename):
#     try:
#         with open(output_filename, "w") as output_file:
#             json.dump(results, output_file, indent=4)
#         print(f"Results saved to {output_filename}")
#     except IOError as e:
#         print(f"Error writing to file {output_filename}: {e}")
 
# Main Function to Process API Response
def main(api_response, user_id, user_prompt):
    try:
        # Debugging: Log the type of api_response
        print(f"Received api_response type: {type(api_response)}")
 
        # Check and parse the type of api_response
        if isinstance(api_response, str):
            data = json.loads(api_response)
        elif isinstance(api_response, dict):
            data = api_response
        elif isinstance(api_response, list):
            # Handle the case where api_response is a list
            data = {"page": {"records": api_response}}  # Convert list to dict format
        else:
            print(f"Invalid type for api_response: {type(api_response)}. Expected str, dict, or list.")
            return
 
        print(f"Parsed Data: {data}")
 
        # Extract and process records
        records = data.get("page", {}).get("records", [])
        if not records:
            print("No records found in the JSON data.")
            return
 
        # Generate embeddings for combined records
        text_chunk = json.dumps(records)  # Converts the entire records list to a JSON string
        print("text_chunk",text_chunk)
        processed_text = preprocess_text(text_chunk)
        print("")
        embedding = generate_embeddings(processed_text)
        prompt_embedding = generate_embeddings(user_prompt)
        # print("embeddings",embedding)
 
        # if embedding is None:
        #     print("Embedding generation failed. Exiting.")
        #     return
 
        # Prepare the document structure
        document = {
            "chunk_id": "chunk_1",
            "parent_id": "ica_responses",
            "title": "Document Title",
            "chunk": processed_text,
            "vector": embedding,
            "prompt": user_prompt,
            "prompt_vector" : prompt_embedding,
            "last_modified": "2024-09-03T00:00:00Z",
        }
 
        # Check if Redis session exists and update accordingly
        if redis_client.exists(user_id):
            existing_results = json.loads(redis_client.get(user_id))
            results = [document] + existing_results
            print("Existing results found. Merging new records.")
        else:
            results = [document]
 
        # Save and store results
        # save_results_to_file(results, output_filename)
        print("redis size",  redis_client.dbsize())
        redis_client.set(user_id, json.dumps(results))
        print(f"Processed and stored {len(results)} chunks for user ID: {user_id}.")
 
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error processing API response: {e}")
 
 
# Run Main Function
# if __name__ == "__main__":
#     sample_api_response = '{"page": {"records": [{"id": 1, "text": "Sample text"}]}}'
#     main(api_response=sample_api_response, user_id="user_123") 
 
# Optional: PCA for Dimensionality Reduction
def reduce_embeddings_dimensionality(embeddings, n_components=50):
    pca = PCA(n_components=n_components)
    reduced_embeddings = pca.fit_transform(np.array(embeddings))
    return reduced_embeddings.tolist()