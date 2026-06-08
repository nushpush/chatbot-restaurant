import redis
import re
from socketio_instance import socketio
from agents import chat_memory
from flask import request
from guardrail.food_guardrails import is_food_related
from guardrail.prompt_filtering import analyze_content
import json
from agents import (
    recipe_agent,
    IngredientAgent,
    RagAgent,
    generate_embeddings,
    findresult,
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

def process_input(user_input):
    try:
        response = is_food_related(user_input)
        if response:
            return None
        else:
            print("response",response)
            return {"response": "Sorry, this input is not food-related."}

    except Exception as e:
        raise Exception(f"Error analyzing content: {e}")

def analyze_content(content):
    try:
        response = analyze_content(content)
        for result_name, result_data in response.items():
            if result_data['severity'] > 0:
                return {'error': f"We can't process your request because the prompt falls under category {result_data['category']} with severity value {result_data['severity']}."}
        return None
    except Exception as e:
        raise Exception(f"Error analyzing content: {e}")
async def process_request(user_prompt, user_id):
    # Check if the user session exists
    response=process_input(user_prompt)
    print("Response from process input:", response)
    if redis_client.exists(user_id):
        print("User session exists.")
        reposnefromredis = findresult.finalresult(user_prompt, user_id, False)
        print("response from redis", reposnefromredis)
        if isinstance(reposnefromredis, list):
            reposnefromredis = " ".join(reposnefromredis)
        print("upper_list", reposnefromredis)
        if "INFORMATION:NO" in reposnefromredis:
            print("User info is not available----")
            ragagent = RagAgent()
            print("rageagent", ragagent)
            await ragagent.get_agent_help(user_prompt, user_id)
        else:
            print("User info is available----")
            message = "Response from private"   

            # Format the final response content
            cleaned_response = re.sub(r"INFORMATION:\s*YES\n*", "", reposnefromredis).strip()
            chat_memory.ChatMemory().add_response_in_redis(
                user_id, user_prompt, cleaned_response
            )
            chat_memory.ChatMemory().fetch_last_five_responses(user_id)
            final_response_content = f"{cleaned_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"
            print("LLM Response Content =", final_response_content)

            # Evaluate the LLM response (optional, based on your implementation)
            # rating_scores = evaluate_llm_response(user_prompt, llm_response)

            print("Final Response Content =")
            # Hide the loader and send the final response
            socketio.emit("show_loader", {"message": "Hideloader"}, room=request.sid)
            socketio.emit(
                "response", {"message": final_response_content}, room=request.sid
            )
            return final_response_content

    # if user id doent exist
    else:
        print("User session does not exist.")
        ragagent = RagAgent()
        result = await ragagent.get_agent_help(user_prompt, user_id)
        print("result", result)
        return result


# async def process_request(user_prompt, user_id):
#     # Check if the user session exists
#     if redis_client.exists(user_id):
#         print("User session exists.")
#         reposnefromredis = findresult.finalresult(user_prompt, user_id)
#         print("response from redis", reposnefromredis)
#         print("response from redis for same user --- ")

#         # Check if response contains both "YES" and "NO" in the `INFORMATION` field
#         if "INFORMATION:YES" in reposnefromredis.strip().upper() and "INFORMATION:NO" in reposnefromredis.strip().upper():
#             print("Response contains both YES and NO, processing final content.")
#             message = "Response from private"

#             # Clean up and format the final response
#             cleaned_response = re.sub(r"INFORMATION:(YES|NO)\n*", "", reposnefromredis).strip()
#             final_response_content = f"{cleaned_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"

#             print("LLM Response Content =", final_response_content)
#             print("Final Response Content =")

#             # Hide the loader and send the final response
#             socketio.emit("show_loader", {"message": "Hideloader"})
#             socketio.emit("response", {"message": final_response_content})
#             return final_response_content

#         # If only "INFORMATION:NO" exists
#         elif "INFORMATION:NO" in reposnefromredis.strip().upper():
#             print("User info is not available----")
#             ragagent = RagAgent()
#             await ragagent.get_agent_help(user_prompt, user_id)

#         else:
#             print("User info is available----")
#             message = "Response from private"

#             # Format the final response content
#             cleaned_response = re.sub(r"INFORMATION:(YES)\n*", "", reposnefromredis).strip()
#             final_response_content = f"{cleaned_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"

#             print("LLM Response Content =", final_response_content)
#             print("Final Response Content =")

#             # Hide the loader and send the final response
#             socketio.emit("show_loader", {"message": "Hideloader"})
#             socketio.emit("response", {"message": final_response_content})
#             return final_response_content

#     # If user session does not exist
#     else:
#         print("User session does not exist.")
#         ragagent = RagAgent()
#         result = await ragagent.get_agent_help(user_prompt, user_id)
#         print("result", result)
#         return result
