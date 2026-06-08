from services import get_auth_token, call_ica_db, call_llm, evaluate_llm_response
from utils import extract_req_body, getUrlReqbody
import asyncio
from socketio_instance import socketio
from agents import generate_embeddings, findresult
from flask import request
import redis
import re
from agents import chat_memory
import ast

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

# class RagAgent:
#     async def get_agent_help(self, user_prompt, user_id):
#         print("ragasid", request.sid)
#         last_response = chat_memory.ChatMemory().fetch_last_five_responses(user_id)
#         last_prompt = None
#         if last_response:
#             last_response_dict = ast.literal_eval(last_response[-1])
#             last_prompt = last_response_dict["prompt"]

#         extracted_info = getUrlReqbody(user_prompt, last_prompt)
#         print("extracted_info in reg_agent", extracted_info)
#         urlreq = [req for req in extracted_info['extracted_info'] if isinstance (extracted_info, dict ) ]
#         print("urlreq in rag_agent", urlreq)

#         llm_called_question = extracted_info['updated_prompt']
#         print("LLM Called Question:", llm_called_question)

#         token = get_auth_token()
#         print("token", token)

#         combined_records = []
#         api_responses = []

#         if not urlreq:
#             print("No API requests to process, directly generating LLM response.")
#             last_five_response = chat_memory.ChatMemory().fetch_last_five_responses(user_id)
#             llm_response = call_llm(llm_called_question,None, last_five_response)
#             chat_memory.ChatMemory().add_response_in_redis(user_id, llm_called_question, llm_response)
#             message = "Response from OpenAI"
#             final_response_content = f"{llm_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"
#             socketio.emit("show_loader", {"message": "Hideloader"}, room=request.sid)
#             socketio.emit("response", {"message": final_response_content}, room=request.sid)
#             return final_response_content

#         if isinstance(urlreq, dict):
#             urlreq = [urlreq]
#         no_records_in_first_api = (
#             False  # Flag to track if the first API returned no records
#         )
#         entity_id = None

#         for i, api_request in enumerate(urlreq):
#             if not isinstance(api_request, dict):
#                 print(f"Error: Expected dictionary but got {type(api_request).__name__}.")
#                 continue

#             api_url = api_request.get("url")
#             api_payload = api_request.get("payload")

#             if not isinstance(api_url, str) or not isinstance(api_payload, dict):
#                 print(f"Error: Expected string for URL and dictionary for payload, but got {type(api_url).__name__} and {type(api_payload).__name__}.")
#                 continue

#             if i == 0:
#                 print(f"Processing first API: URL = {api_url}, Payload = {api_payload}")
#                 api_response = call_ica_db(api_url, api_payload, token)
#                 print("First API Response =", api_response)
#                 if (
#                     api_response
#                     and api_response.get("success") is True
#                     and api_response.get("page", {}).get("numberOfRecords", 0) == 0
#                    ):
#                     print(
#                         "No records found in the first API response. Setting flag to generate LLM response later."
#                     )
#                     no_records_in_first_api = True
#                     break  # No need to proceed with further API requests
#                 if api_response and api_response.get("success") is True:
#                     entity_id = api_response.get("page", {}).get("records", [{}])[0].get("id")
#                     if not entity_id:
#                         print("Error: No entityId found in the first API response.")
#                         continue
#                 else:
#                     print("No valid records found in the first API response.")
#                     return

#                 api_responses.append(api_response)

#             elif i > 0:
#                 if entity_id:
#                     # Replace entityId in the URL
#                     api_url = api_url.replace("{entityId}", entity_id)

#                     # Replace entityId in the payload if necessary
#                     api_payload = self.replace_entity_id_in_payload(api_payload, entity_id)

#                     print(f"Processing API {i+1} with entityId: URL = {api_url}, Payload = {api_payload}")
#                     api_response = call_ica_db(api_url, api_payload, token)
#                     print(f"API {i+1} Response =", api_response)

#                     api_responses.append(api_response)
#                 else:
#                     print(f"No entityId available for API {i+1} request.")

#         if api_responses:
#             generate_embeddings.main(api_responses, user_id, llm_called_question)
#             response_from_redis = findresult.finalresult(llm_called_question, user_id, True)
#             combined_records.append(response_from_redis if isinstance(response_from_redis, str) else str(response_from_redis))

#         filtered_records = [re.sub(r"INFORMATION:(YES|NO)\n*", "", record) for record in combined_records]
#         combined_records_str = "\n".join(filtered_records)

#         if no_records_in_first_api or not combined_records_str.strip():
#             print("No records found, generating LLM response.")
#             last_five_response = chat_memory.ChatMemory().fetch_last_five_responses(user_id)
#             llm_response = call_llm(llm_called_question,None,last_five_response)
#             chat_memory.ChatMemory().add_response_in_redis(user_id, llm_called_question, llm_response)
#             message = "Response from OpenAI"
#             final_response_content = f"{llm_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"
#         else:
#             message = "Response from private" if filtered_records else "Response from OpenAI"
#             final_response_content = f"{combined_records_str}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"

#         chat_memory.ChatMemory().add_response_in_redis(user_id, llm_called_question, combined_records_str)
#         socketio.emit("show_loader", {"message": "Hideloader"}, room=request.sid)
#         socketio.emit("response", {"message": final_response_content}, room=request.sid)
#         return final_response_content

#     def replace_entity_id_in_payload(self, payload, entity_id):
#         """
#         Recursively replace {entityId} in payload wherever it appears.
#         """
#         if isinstance(payload, dict):
#             for key, value in payload.items():
#                 if isinstance(value, str) and "{entityId}" in value:
#                     payload[key] = value.replace("{entityId}", entity_id)
#                 elif isinstance(value, (dict, list)):
#                     self.replace_entity_id_in_payload(value, entity_id)
#         elif isinstance(payload, list):
#             for index, item in enumerate(payload):
#                 if isinstance(item, str) and "{entityId}" in item:
#                     payload[index] = item.replace("{entityId}", entity_id)
#                 elif isinstance(item, (dict, list)):
#                     self.replace_entity_id_in_payload(item, entity_id)
#         return payload


class RagAgent:
    async def get_agent_help(self, user_prompt, user_id):
        print("ragasid", request.sid)
        last_response = chat_memory.ChatMemory().fetch_last_five_responses(user_id)
        last_prompt = None
        if last_response:
            last_response_dict = ast.literal_eval(last_response[-1])
            last_prompt = last_response_dict["prompt"]

        urlreq = getUrlReqbody(user_prompt, last_prompt)
        print("urlreq", urlreq)

        extracted_info = getUrlReqbody(user_prompt, last_prompt)
        print("extracted_info in reg_agent", extracted_info)
        urlreq = [
            req
            for req in extracted_info["extracted_info"]
            if isinstance(extracted_info, dict)
        ]
        print("urlreq in rag_agent", urlreq)

        llm_called_question = extracted_info["updated_prompt"]
        print("LLM Called Question:", llm_called_question)

        token = get_auth_token()
        print("token", token)

        combined_records = []
        api_responses = []
        no_records_in_first_api = False
        entity_id_1 = None
        entity_id_2 = None

        if not urlreq:
            print("No API requests to process, directly generating LLM response.")
            last_five_response = chat_memory.ChatMemory().fetch_last_five_responses(
                user_id
            )
            llm_response = call_llm(llm_called_question, None, last_five_response)
            chat_memory.ChatMemory().add_response_in_redis(
                user_id, llm_called_question, llm_response
            )
            message = "Response from OpenAI"
            final_response_content = f"{llm_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"
            socketio.emit("show_loader", {"message": "Hideloader"}, room=request.sid)
            socketio.emit(
                "response", {"message": final_response_content}, room=request.sid
            )
            return final_response_content

        if isinstance(urlreq, dict):
            urlreq = [urlreq]

        for i, api_request in enumerate(urlreq):
            if not isinstance(api_request, dict):
                print(
                    f"Error: Expected dictionary but got {type(api_request).__name__}."
                )
                continue

            api_url = api_request.get("url")
            api_payload = api_request.get("payload")

            if not isinstance(api_url, str) or not isinstance(api_payload, dict):
                print(
                    f"Error: Expected string for URL and dictionary for payload, but got {type(api_url).__name__} and {type(api_payload).__name__}."
                )
                continue

            if i == 0:
                print(f"Processing first API: URL = {api_url}, Payload = {api_payload}")
                try:
                    api_response = call_ica_db(api_url, api_payload, token)
                    print("First API Response =", api_response)
                    if (
                        api_response
                        and api_response.get("success") is True
                        and api_response.get("page", {}).get("numberOfRecords", 0) == 0
                    ):
                        print(
                            "No records found in the first API response. Setting flag to generate LLM response later."
                        )
                        no_records_in_first_api = True
                        break

                    if api_response and api_response.get("success") is True:
                        entity_id_1 = (
                            api_response.get("page", {})
                            .get("records", [{}])[0]
                            .get("id")
                        )
                        print("Extracted entity_id_1:", entity_id_1)
                        if not entity_id_1:
                            print("Error: No entityId found in the first API response.")
                            continue
                    api_responses.append(api_response)
                except Exception as e:
                    print(f"Error calling first API: {e}")
                    return

            elif i == 1:
                if entity_id_1:
                    api_url = api_url.replace("{entityId}", entity_id_1)
                    api_payload = self.replace_entity_id_in_payload(
                        api_payload, entity_id_1
                    )

                    print(
                        f"Processing second API with entityId_1: URL = {api_url}, Payload = {api_payload}"
                    )
                    try:
                        api_response = call_ica_db(api_url, api_payload, token)
                        print("Second API Response =", api_response)
                        if api_response and api_response.get("success") is True:
                            entity_id_2 = (
                                api_response.get("page", {})
                                .get("records", [{}])[0]
                                .get("id")
                            )
                            print("Extracted entity_id_2:", entity_id_2)
                        api_responses.append(api_response)
                    except Exception as e:
                        print(f"Error calling second API: {e}")

            elif i == 2:
                if entity_id_1:
                    api_url_with_entity_id_1 = api_url.replace(
                        "{entityId}", entity_id_1
                    )
                    api_payload_with_entity_id_1 = self.replace_entity_id_in_payload(
                        api_payload.copy(), entity_id_1
                    )
                    print(
                        f"Processing third API with entityId_1: URL = {api_url_with_entity_id_1}, Payload = {api_payload_with_entity_id_1}"
                    )
                    try:
                        api_response = call_ica_db(
                            api_url_with_entity_id_1,
                            api_payload_with_entity_id_1,
                            token,
                        )
                        print("Third API Response with entityId_1 =", api_response)
                        api_responses.append(api_response)
                    except Exception as e:
                        print(f"Error calling third API with entityId_1: {e}")

                if entity_id_2:
                    api_url_with_entity_id_2 = api_url.replace(
                        "{entityId}", entity_id_2
                    )
                    api_payload_with_entity_id_2 = self.replace_entity_id_in_payload(
                        api_payload.copy(), entity_id_2
                    )
                    print(
                        f"Processing third API with entityId_2: URL = {api_url_with_entity_id_2}, Payload = {api_payload_with_entity_id_2}"
                    )
                    try:
                        api_response = call_ica_db(
                            api_url_with_entity_id_2,
                            api_payload_with_entity_id_2,
                            token,
                        )
                        print("Third API Response with entityId_2 =", api_response)
                        api_responses.append(api_response)
                    except Exception as e:
                        print(f"Error calling third API with entityId_2: {e}")

        if api_responses:
            generate_embeddings.main(api_responses, user_id, llm_called_question)
            response_from_redis = findresult.finalresult(
                llm_called_question, user_id, True
            )
            combined_records.append(
                response_from_redis
                if isinstance(response_from_redis, str)
                else str(response_from_redis)
            )

        filtered_records = [
            re.sub(r"INFORMATION:(YES|NO)\n*", "", record)
            for record in combined_records
        ]
        combined_records_str = "\n".join(filtered_records)

        if no_records_in_first_api or not combined_records_str.strip():
            print("No records found, generating LLM response.")
            last_five_response = chat_memory.ChatMemory().fetch_last_five_responses(
                user_id
            )
            llm_response = call_llm(llm_called_question, None, last_five_response)
            chat_memory.ChatMemory().add_response_in_redis(
                user_id, llm_called_question, llm_response
            )
            message = "Response from OpenAI"
            final_response_content = f"{llm_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"
        else:
            if not entity_id_1 and not entity_id_2:
                print("No entityId available, calling LLM directly.")
                last_five_response = chat_memory.ChatMemory().fetch_last_five_responses(
                    user_id
                )
                llm_response = call_llm(llm_called_question, None, last_five_response)
                chat_memory.ChatMemory().add_response_in_redis(
                    user_id, llm_called_question, llm_response
                )
                message = "Response from OpenAI"
                final_response_content = f"{llm_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"
            else:
                message = (
                    "Response from private"
                    if filtered_records
                    else "Response from OpenAI"
                )
                final_response_content = f"{combined_records_str}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"

        chat_memory.ChatMemory().add_response_in_redis(
            user_id, llm_called_question, combined_records_str
        )
        socketio.emit("show_loader", {"message": "Hideloader"}, room=request.sid)
        socketio.emit("response", {"message": final_response_content}, room=request.sid)
        return final_response_content

    def replace_entity_id_in_payload(self, payload, entity_id):
        """
        Recursively replace {entityId} in payload wherever it appears.
        """
        if isinstance(payload, dict):
            for key, value in payload.items():
                if isinstance(value, str) and "{entityId}" in value:
                    payload[key] = value.replace("{entityId}", entity_id)
                elif isinstance(value, (dict, list)):
                    self.replace_entity_id_in_payload(value, entity_id)
        elif isinstance(payload, list):
            for index, item in enumerate(payload):
                if isinstance(item, str) and "{entityId}" in item:
                    payload[index] = item.replace("{entityId}", entity_id)
                elif isinstance(item, (dict, list)):
                    self.replace_entity_id_in_payload(item, entity_id)
        return payload
