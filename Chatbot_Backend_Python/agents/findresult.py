import numpy as np
import requests
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from langchain_community.vectorstores.azuresearch import AzureSearch
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# from azure.search.documents.indexes.models import VectorSearchParameters, VectorSearchQuery
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import VectorSearchProfile
from azure.search.documents.models import QueryType, SearchMode
from azure.search.documents.models import VectorizedQuery

# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.decomposition import PCA


import redis


import json


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


client = AzureOpenAI(
    api_key="7ce0a3e988834cdc8b93a968f4e6c7bc",
    api_version="2024-02-15-preview",
    azure_endpoint="https://genai-usecasesforswe-modernization.openai.azure.com",
)


def generate_embeddings(
    text_chunk, model="genai4swemodernizationembeddingmodel"
):  # model = "deployment_name"
    return client.embeddings.create(input=[text_chunk], model=model).data[0].embedding


# Initialize the SearchClient
search_client = SearchClient(
    endpoint="https://genaipocllmsearch.search.windows.net",
    index_name="qsr-chef",
    credential=AzureKeyCredential(
        "kB4ez5gc3g2McSC4PnWzcfXdzoAJyJYseWmqqtk9eKAzSeA8zh9V"
    ),
)


def search_by_embedding(embedding, top_k=5):
    # Specify the name and algorithm configuration name
    # vector_search_profile = VectorSearchProfile(
    #     name="myExhaustiveKnnProfile",
    #     algorithm_configuration_name="myExhaustiveKnn",  # This is your vector search algorithm configuration
    #     vector=embedding,
    #     fields=["vector"],
    #     k=top_k
    # )

    # # Search using the embedding
    # results = search_client.search(search_text="", vector_search_profile=vector_search_profile)

    # for result in results:
    #     print(f"Chunk ID: {result['chunk_id']}, Score: {result['@search.score']}, Title: {result['title']}")
    #     results = search_client.search(
    #     search_text="*",  # Use '*' to search all documents
    #     vector=embedding,
    #     vector_fields=["vector"],  # Replace with your vector field name
    #     filter="parent_id eq 'ica_response'",  # Replace with the parent_id you want to filter by
    #     query_type=QueryType.SEMANTIC,  # Use semantic search
    #     search_mode=SearchMode.ALL  # Adjust based on your needs
    # )

    # Process the results
    for result in results:
        print(result)


# Example usage


def search_azure_search(query_embedding):
    vectorized_query = VectorizedQuery(
        vector=query_embedding, k_nearest_neighbors=5, fields="vector"
    )

    response = search_client.search(
        vector_queries=[vectorized_query],
    )

    return response


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def prompt_similarity_score(prompt_embedding, user_id):
    stored_data = json.loads(redis_client.get(user_id))
    prompt_similarities = []

    # Iterate over each dictionary in the array
    for chunk_data in stored_data:  
        stored_prompt_embedding = np.array(chunk_data["prompt_vector"])  # Fetch all the embedding

        similarity = cosine_similarity(prompt_embedding, stored_prompt_embedding)
        prompt_similarities.append((chunk_data, similarity))

    # Sort by similarity in descending order
    prompt_similarities.sort(key=lambda x: x[1], reverse=True)
   
    top_prompt_results = []
    for i in range(len(prompt_similarities)):
        chunk_data, similarity = prompt_similarities[i]
        top_prompt_results.append(
            {
                "prompt": chunk_data["prompt"],  
                "similarity rating": similarity,
            }
        )
    print("top_prompt_results", top_prompt_results)
    first_similarity_rating = top_prompt_results[0]['similarity rating']
    return first_similarity_rating

def retrieve_most_similar(query_embedding, user_id):
    top_k=1
    # Retrieve stored data from Redis (expecting an array of chunks)
    stored_data = json.loads(redis_client.get(user_id))

    similarities = []

    # Iterate over each dictionary in the array
    for chunk_data in stored_data:  # Assuming stored_data is a list of chunks (dicts)
        stored_embedding = np.array(chunk_data["vector"])  # Fetch the embedding

        # Calculate cosine similarity
        similarity = cosine_similarity(query_embedding, stored_embedding)
        similarities.append((chunk_data, similarity))

    # Sort by similarity in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Retrieve the top_k most similar chunks
    top_results = []
    for i in range(min(top_k, len(similarities))):
        chunk_data, similarity = similarities[i]
        top_results.append(
            {
                "chunk": chunk_data["chunk"], 
                "similarity": similarity,
            }
        )

    print("top_prompt", top_results)
    return top_results


# def retrieve_most_similar(query_embedding, top_k=5, n_components=50):
#     # Load data from Redis
#     stored_data = json.loads(redis_client.get("user_session1"))

#     similarities = []

#     # Convert query_embedding to a NumPy array if it is not already
#     query_embedding = np.array(query_embedding)
#     query_embedding = query_embedding.reshape(1, -1)  # Ensure it's 2D

#     # Prepare list for PCA
#     embeddings = [query_embedding]
#     for chunk_data in stored_data:
#         embeddings.append(np.array(chunk_data['vector']).reshape(1, -1))

#     # Apply PCA for dimensionality reduction
#     pca = PCA(n_components=n_components)
#     reduced_embeddings = pca.fit_transform(np.vstack(embeddings))

#     # Extract the reduced query embedding
#     query_embedding_reduced = reduced_embeddings[0].reshape(1, -1)

#     # Extract reduced stored embeddings
#     stored_embeddings_reduced = reduced_embeddings[1:]

#     # Calculate similarity
#     for idx, chunk_data in enumerate(stored_data):
#         stored_embedding = stored_embeddings_reduced[idx]

#         # Check if dimensions match
#         if query_embedding_reduced.shape[1] != stored_embedding.shape[0]:
#             print(f"Dimension mismatch: query_embedding {query_embedding_reduced.shape[1]}, stored_embedding {stored_embedding.shape[0]}")
#             continue

#         # Calculate cosine similarity
#         similarity = cosine_similarity(query_embedding_reduced, stored_embedding.reshape(1, -1))[0][0]
#         similarities.append((chunk_data, similarity))

#     # Sort by similarity in descending order
#     similarities.sort(key=lambda x: x[1], reverse=True)

#     # Retrieve the top_k most similar chunks
#     top_results = []
#     for i in range(min(top_k, len(similarities))):
#         chunk_data, similarity = similarities[i]
#         top_results.append({
#             "chunk_id": chunk_data['chunk_id'],  # Include chunk_id or any other relevant metadata
#             "parent_id": chunk_data['parent_id'],
#             "title": chunk_data['title'],
#             "chunk": chunk_data['chunk'],
#             "similarity": similarity
#         })

#     return top_results


def save_results_to_file(results, output_filename):
    try:
        # Open the output file in write mode
        with open(output_filename, "w") as output_file:
            # Convert results (list of records with embeddings) to JSON and write to file
            json.dump(results, output_file, indent=4)

        print(f"Results have been saved to {output_filename}")
    except IOError as e:
        print(f"Error writing to file {output_filename}: {e}")


def llm_response(prompt):
    try:
        llm_api = "https://genaiazurellmapp.azurewebsites.net/api/v1/chat"
        # Directly use the content you provided in the payload
 
        payload = {"content": prompt, "model": "gpt-4-vision"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        print("Payload:", payload)  # For debugging to confirm payload content
        response = requests.post(llm_api, data=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print("Response data:", response_data)
        # Adjust the response handling based on the response format
        if isinstance(response_data["response"], list):
            # Handle list response appropriately
            return response_data["response"][0].get(
                "response", "No response available."
            )
        else:
            return response_data["response"].get("response", "No response available.")
    except requests.exceptions.RequestException as e:
        return f"Error sending request: {e}"


# Function to calculate cosine similarity between two vectors
# def cosine_similarity(v1, v2):
#     v1 = np.array(v1)
#     v2 = np.array(v2)
#     return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# # Load embeddings from the text file
# def load_embeddings_from_file(file_path):
#     embeddings_responses = []
#     with open(file_path, 'r') as file:
#         for line in file:
#             # # Split the line into the embedding string and the response
#             # embedding_str, response = line.strip().split('|')

#             # # Convert the embedding string into a list of floats
#             # embedding = list(map(float, embedding_str.split(',')))

#             # # Append the embedding and response as a dictionary to the list
#             embeddings_responses.append(line)

#     return embeddings_responses

# Function to find the most similar response for a given prompt
# def find_most_similar_response(prompt, file_path):
#     print("prompt",prompt)
#     print("file_path",file_path)
#     prompt_embedding = generate_embeddings(prompt)
#     print("prompt_embedding",prompt_embedding)
#     stored_embeddings = load_embeddings_from_file(file_path)

#     most_similar = max(stored_embeddings, key=lambda x: cosine_similarity(prompt_embedding, x['embedding']))
#     return most_similar['response']


# Example usage
# file_path = 'embeddings_input.txt'  # The file is in the same directory as the code"
# def finalresult(prompt, user_id):

#     # print("prompt in finalresult", prompt)
#     systemprompt = """
#     We are providing the rag response with the prompt,
#     please provide the response as per given instructions.
#     If an exact match for entity is found, return INFORMATION:YES and also provide the response with the information.
#     If the item is not present or the name doesn't match exactly, return INFORMATION:NO and don't provide the response.
#     Ensure that all entities and values are checked accurately, matching the entitys and values precisely to provide the correct response"""
#     # updatedprompt = prompt + " give only what is asked and not anything more"
#     embeddings = generate_embeddings(prompt)
#     response = retrieve_most_similar(embeddings, user_id)  # getting data from RAG
#     print("response", response)
#     # print("response from RAG : ", response)
#     if response and "chunk" in response[0]:
#         # chunk_data = json.loads('chunk')  # Use json.dumps to make it readable
#         # print("chunk_data",chunk_data)
#         object_str = json.dumps(response)  # Format the object for better readability
#         print("object_str : ", object_str)
#         template = systemprompt + "\n" + prompt + "\n" + object_str
#         # print("template : ", template)
#         finalresponse = llm_response(template)  # getting data from LLM
#         print("finalresponse : ", finalresponse)
#         return finalresponse
#     else:
#         return f"Sorry, I couldn't find any relevant information based on your prompt '{prompt}'."
# def chunk_text(text, max_chunk_size):
#     # Split the text into smaller chunks of a specified size
#     for i in range(0, len(text), max_chunk_size):
#         yield text[i:i + max_chunk_size]
# def finalresult(prompt, user_id, max_chunk_size=3990):

    

#     systemprompt = """
#     You are provided with a RAG response along with the original prompt. Based on the provided information, please adhere to the following instructions:
#     1. If an **exact match** is found for the entity in the response, return `INFORMATION:YES` and include the response details.
#     2. If the entity **name or information does not match exactly**, return only `INFORMATION:NO` without any additional information.
#     3. Always ensure that only one of `INFORMATION:YES` or `INFORMATION:NO` is returned for each query. Do not return both for the same item.
#     4. Be strict in checking the entity and values for precise matches before deciding the response."""
                                                                                                        
#     # Generate embeddings for the entire prompt
#     embeddings = generate_embeddings(prompt)
    
#     # Retrieve the most similar response from RAG based on embeddings
#     response = retrieve_most_similar(embeddings, user_id)  # getting data from RAG
#     print("response", response)
    
#     if response and "chunk" in response[0]:
#         object_str = json.dumps(response)  # Format the object for better readability

#         # If object_str is too large, split it into chunks
#         if len(object_str) > max_chunk_size:
#             print(f"Response is too large, splitting into chunks of size {max_chunk_size}")
#             response_chunks = list(chunk_text(object_str, max_chunk_size))

#             final_responses = []
#             for chunk in response_chunks:
#                 template =  "\n" + prompt + "\n" + chunk + systemprompt 
#                 final_responses.append(llm_response(template))

#             # Combine all responses or summarize
#             finalresponse = " ".join(final_responses)
#         else:
#             # Process normally if within size limit
#             template = systemprompt + "\n" + prompt + "\n" + object_str
#             finalresponse = llm_response(template)

#         print("finalresponse : ", finalresponse)
#         return finalresponse

#     else:
#         return f"Sorry, I couldn't find any relevant information based on your prompt '{prompt}'."





def chunk_text(text, max_chunk_size):
    # Split the text into smaller chunks of a specified size
    for i in range(0, len(text), max_chunk_size):
        print("inside chunk_text of findresult")
        yield text[i:i + max_chunk_size]

def finalresult(prompt, user_id, get_api_called):
    max_chunk_size=5000
    systemprompt = """
    You are an expert whose task is to provide specific information from the private knowledge base provided in the response.
    1. If an exact match for entity is found, return INFORMATION:YES and also provide the response with the information.
    2. If the item is not present or the name doesn't match exactly or if they ask any alternative item, return INFORMATION:NO and don't provide the response.
    3. Ensure that all entities and values are checked accurately, matching the entities and values precisely to provide the correct response
    4. Do not interpret, summarize, or add any extra information. Only return the information available from the provided response.
    5. Avoid including external information from external or public knowledge sources, relying strictly on the provided private knowledge base.
    """
    systemprompt2 = """
    You are an expert whose task is to extract and present only the exact information from the private knowledge base provided in the response.
 
    1. Do not interpret, summarize, or add any extra information. Present only the precise content from the provided response.
    2. Absolutely refrain from including any information from external or public knowledge sources, relying strictly on the provided private knowledge base.
    """                                                                                                    
    # Generate embeddings for the entire prompt
    embeddings = generate_embeddings(prompt)

    prompt_similarity_rating = prompt_similarity_score(embeddings, user_id)
    
    # Retrieve the most similar response from RAG based on embeddings
    response = retrieve_most_similar(embeddings, user_id)  # getting data from RAG
    print("response", response)

    first_similarity_rating_response = response[0]['similarity'] # getting the similarity rating from the response of the first chunk
    print("prompt_similarity_rating", prompt_similarity_rating)
    print("first_similarity_rating_response", first_similarity_rating_response)

    if(get_api_called == False):
        if prompt_similarity_rating < 0.95 or first_similarity_rating_response < 0.8:
            print("INFORMATION:NO from prompt_similarity_rating")
            return "INFORMATION:NO"
    
    if response and "chunk" in response[0]:
        object_str = json.dumps(response)  # Format the object for better readability

        # If object_str is too large, split it into chunks
        if len(object_str) > max_chunk_size:
            print(f"Response is too large, splitting into chunks of size {max_chunk_size}")
            response_chunks = list(chunk_text(object_str, max_chunk_size))

            final_responses = []
            last_final_response = []
            # finalresponse = []
            for chunk in response_chunks:
                print("chunk in for loop: ", type(chunk), chunk)
                template = (
                f"This is the prompt:\n{prompt}.\n"
                f"This is the response data that we are providing:\n{chunk}.\n"
                f"These are the instructions:\n{systemprompt}."
                )
                print("template in findresult: ", template)
                result = llm_response(template)
                print("result in findresult: ", type(result), result)
                final_responses.append(result.strip()) 
                print("final_responses in line 430: ", type(final_responses), final_responses)
            print("final_responses : ", final_responses)
            
            # Determine final response based on all chunk results
            if any("INFORMATION:YES" in res or "INFORMATION: YES" for res in final_responses):
                # Return INFORMATION:YES if found in any chunk
                # finalresponse = next(res for res in final_responses if "INFORMATION: YES" in res)
                dump = json.dumps(final_responses)
                template1 = (
                f"This is the prompt:\n{prompt}.\n"
                f"This is the private knowledge base data that we are providing:\n{dump}.\n"
                f"These are the instructions:\n{systemprompt2}."
                )
                print("template1 : ", template1)
                result1 = llm_response(template1)
                print("result1 : ", result1)
                # last_final_response.append(result1.strip())
                finalresponse = result1
                
            else:
                # Return INFORMATION:NO if no YES found
                finalresponse = "INFORMATION:NO"
                # finalresponse = llm_response(prompt)
        else:
            # Process normally if within size limit
            template =  prompt + "\n" + object_str  +  "\n" + systemprompt 
            finalresponse = llm_response(template)
            
        print("finalresponse : ", finalresponse)
        return finalresponse

    else:
        return f"Sorry, I couldn't find any relevant information based on your prompt '{prompt}'."





# print("embeddings",embeddings)

# response = retrieve_most_similar(embeddings, 5, 50)