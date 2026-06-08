import redis
import requests
import json
from openai import AzureOpenAI

class ChatMemory:
    
    def __init__(self):
        redis_host = "genAIbusiness.redis.cache.windows.net"
        redis_port = 6380
        redis_password = "iBucMF8eX6TMgfNJhelrC10XvLHrfdTk1AzCaAWkNF0="
        # Initialize Redis client in the constructor
        self.redis_client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            ssl=True,
            decode_responses=True
        )
        # Initialize Azure OpenAI client in the constructor
        self.client = AzureOpenAI(
            api_key="7ce0a3e988834cdc8b93a968f4e6c7bc",
            api_version="2024-02-15-preview",
            azure_endpoint="https://genai-usecasesforswe-modernization.openai.azure.com"
        )

    def generate_embedding(self, text_chunk, model="genai4swemodernizationembeddingmodel"):
        try:
            print("Generating embeddings in chat memory",)
            print("text_chunk", text_chunk)
            # Ensure text_chunk is either a single string or a list of strings
            if isinstance(text_chunk, list):
                print("Generating embeddings for a list of text chunks")
                response = self.client.embeddings.create(input=text_chunk, model=model)
            else:
                print("Generating embeddings for a single text chunk")
                response = self.client.embeddings.create(input=[text_chunk], model=model)
            
            embedding = response.data[0].embedding
            print("Embedding generated:", embedding)
            print(type(embedding))
            return embedding
        except Exception as e:
            print(f"Error generating embedding in chat memory: {str(e)}")
            return None
    
    def add_response_in_redis(self, user_id, prompt, response):
        try:
            print("Adding response to Redis called:")
            redis_name = f"{user_id}_response"
            data = {"prompt": prompt, "response": response}
            self.redis_client.rpush(redis_name, str(data))
            data = {"prompt": prompt, "response": response}
            self.redis_client.rpush(redis_name, str(data))
            print("Response added to Redis cache.")
            return True
        except requests.exceptions.RequestException as e:
            return f"Error sending request: {e}"
        
    def fetch_last_five_responses(self, user_id):
        try:
            redis_name = f"{user_id}_response"
            if not self.redis_client.exists(redis_name):
                print("No response available in Redis cache.")
                return None
            response_list = self.redis_client.lrange(redis_name, -5, -1)
            print("last 5 response list fetched from Redis cache.", response_list)
            return response_list
        except requests.exceptions.RequestException as e:
            return f"Error sending request: {e}"
        
    def extract_last_five_responses(self, user_id, chat_history):
        try:
           # Get the last five responses along with their messages
            responses = []
            for message in chat_history['Messages']:
                for resp in message['Responses']:
                    # Extract response and message content
                    response_text = resp['response'].replace('<span>Response from private</span>', '')
                    message_content = message['content']
                    
                    responses.append((message_content, response_text))
           
            last_five_responses = responses[-5:]

            # Add both message and response to Redis
            for idx, (message_content, response_text) in enumerate(last_five_responses, 1):
                print(f"Message {idx}: {message_content}")
                print(f"Response {idx}: {response_text}")
                self.add_response_in_redis(user_id, message_content, response_text)
            
        except requests.exceptions.RequestException as e:
            return f"Error sending request: {e}"
        