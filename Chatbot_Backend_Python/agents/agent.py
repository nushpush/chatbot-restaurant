from services import get_auth_token, call_ica_db, call_llm, evaluate_llm_response
from utils import extract_req_body, getUrlReqbody
import asyncio
from socketio_instance import socketio
import time
import requests


# import redis_client
class GreetingAgent:
    def greet(self):
        return "How can I assist you?"


# original code
class IngredientAgent:
    productList = []

    async def get_ingredient_help(self, user_prompt, allhistory):
        try:
            # socketio.emit('response', {'message': 'Sure, let me search ingredient and provide you details'})
            # time.sleep(1)
            print("inside getingredienthelp")
            # socketio.emit('show_loader', {'message': 'Loading...'})
            print("after socketioemit")
            urlreq = getUrlReqbody(user_prompt)
            print("urlreq", urlreq)
            url = None
            payloads = []
            for item in urlreq:
                for key, value in item.items():
                    if url is None:
                        url = value["url"]
                    if value["url"] == url:
                        payloads.append(value["payLoad"])
            print("URL:", url)
            print("Payloads:", payloads)
            token = get_auth_token()
            all_data = []

            # Fetch initial data from ICA DB
            async def fetch_data(url, payload):
                print("urlinfetch_Data", url)
                print("payloadinfetch_Data", payload)
                callicadb = call_ica_db(url, payload, token)
                print("callicadb =", callicadb)
                return callicadb

            ica_response = await asyncio.gather(
                *(fetch_data(url, payload) for payload in payloads)
            )
            print("ica_response = ", ica_response)

            has_records = any(
                "page" in response
                and "records" in response["page"]
                and len(response["page"]["records"]) > 0
                for response in ica_response
            )
            print("has_records =", has_records)

            if has_records:
                additional_req_body = [
                    {**element, "additional": True} for element in urlreq
                ]
                print("additional_req_body = ", additional_req_body)
                additional_payloads = []
                for item in additional_req_body:
                    for key, value in item.items():
                        if (
                            isinstance(value, dict)
                            and "url" in value
                            and value["url"] == url
                        ):
                            additional_payloads.append(value["payLoad"])

                additional_ica_db_response = await asyncio.gather(
                    *(fetch_data(url, payload) for payload in additional_payloads)
                )
                print("additional_ica_db_response =", additional_ica_db_response)

                for response in additional_ica_db_response:
                    if (
                        response is not None
                        and "page" in response
                        and "records" in response["page"]
                    ):
                        for original_response in ica_response:
                            if (
                                original_response is not None
                                and "page" in original_response
                                and "records" in original_response["page"]
                            ):
                                original_response["page"]["records"].extend(
                                    response["page"]["records"]
                                )

            # Generate response using LLM
            llm_response = call_llm(user_prompt, ica_response, allhistory)
            print("LLM Response = ", llm_response)

            # Determine the message based on the presence of records
            message = "Response from private" if has_records else "Response from OpenAI"

            # Format the final response content
            final_response_content = f"{llm_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"
            print("LLM Response Content = ", final_response_content)

            # Evaluate the LLM response
            rating_scores = evaluate_llm_response(user_prompt, llm_response)

            # Return both LLM response and rating scores
            # return {
            #    "rating": rating_scores,
            #    "response": final_response_content
            # }
            # vector = create_vector_representation(user_prompt)
            # redis_client.lpush(f"vector:{user_prompt}",vector)
            print("finalresponse", final_response_content)
            # socketio.emit("show_loader", {"message": "Hideloader"})
            socketio.emit("response", {"message": final_response_content})
            return final_response_content
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error processing ingredient request: {e}")

            # Stop the loader and send an error response
            # socketio.emit("show_loader", {"message": "Hideloader"})
            # socketio.emit('response', {'message': 'Error: Could not process your request. Please try again.'})
            return "Error: Could not process your request. Please try again."


# streamincode


# class IngredientAgent:
#     productList = []

#     async def get_ingredient_help(self, websocket: WebSocket, user_prompt, allhistory):
#         try:
#             await websocket.send_text("Sure, let me search ingredient and provide you details")
#             await asyncio.sleep(1)
#             await websocket.send_text("Loading...")

#             urlreq = getUrlReqbody(user_prompt)
#             url = None
#             payloads = []
#             for item in urlreq:
#                 for key, value in item.items():
#                     if url is None:
#                         url = value['url']
#                     if value['url'] == url:
#                         payloads.append(value['payLoad'])

#             token = get_auth_token()

#             async def fetch_data(url, payload):
#                 callicadb = call_ica_db(url, payload, token)
#                 return callicadb

#             ica_response = await asyncio.gather(*(fetch_data(url, payload) for payload in payloads))

#             has_records = any('page' in response and 'records' in response['page'] and len(response['page']['records']) > 0 for response in ica_response)

#             if has_records:
#                 additional_req_body = [{**element, 'additional': True} for element in urlreq]
#                 additional_payloads = []
#                 for item in additional_req_body:
#                     for key, value in item.items():
#                         if isinstance(value, dict) and 'url' in value and value['url'] == url:
#                             additional_payloads.append(value['payLoad'])

#                 additional_ica_db_response = await asyncio.gather(*(fetch_data(url, payload) for payload in additional_payloads))

#                 for response in additional_ica_db_response:
#                     if response is not None and 'page' in response and 'records' in response['page']:
#                         for original_response in ica_response:
#                             if original_response is not None and 'page' in original_response and 'records' in original_response['page']:
#                                 original_response['page']['records'].extend(response['page']['records'])

#             # Stream the response from LLM
#             llm_response = call_llm(user_prompt, ica_response, allhistory)

#             message = "Response from private" if has_records else "Response from OpenAI"
#             final_response_content = f"{llm_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"

#             # Send chunks of response content
#             for chunk in final_response_content:
#                 await websocket.send_text(chunk)
#                 await asyncio.sleep(0.01)  # Adjust as needed for smoother streaming

#             rating_scores = evaluate_llm_response(user_prompt, llm_response)

#             await websocket.send_text(f"Rating: {rating_scores}")
#             await websocket.send_text("[DONE]")  # Indicate completion

#         except Exception as e:
#             await websocket.send_text(f"Error processing ingredient request: {e}")


# class IngredientAgent:
#     async def get_ingredient_help(self, user_prompt, allhistory):
#         try:
#             # Emit initial response and show loader
# socketio.emit('response', {'message': 'Sure, let me search ingredients and provide you details'})
#             socketio.emit('show_loader', {'message': 'Loading...'})

#             # Hardcoded URL
#             url = "https://dcponazure-entity-api03.azurewebsites.net/api/v1/entities/PRODUCT/query/"

#             # Dynamically create the payload with the user's input
#             payload = {
#                 'pageNumber': 0,
#                 'itemsPerPage': 10,
#                 'fields': [
#                     {
#                         'name': 'name',
#                         'match': {
#                             'regex': user_prompt,
#                             'ignoreCase': True
#                         }
#                     }
#                 ]
#             }
#             token = get_auth_token()

#             async def fetch_data(url, payload):
#                 print('urlinfetch_Data', url)
#                 print('payloadinfetch_Data', payload)
#                 callicadb = call_ica_db(url, payload, token)
#                 print("callicadb =", callicadb)
#                 return callicadb

#             # Fetch initial data from ICA DB
#             ica_response = await asyncio.gather(fetch_data(url, payload))
#             print("ica_response = ", ica_response)

#             # Check if records are present in the response
#             has_records = any(response and 'page' in response and 'records' in response['page'] and len(response['page']['records']) > 0 for response in ica_response)
#             print("has_records =", has_records)

#             # If records exist, attempt to fetch additional data
#             if has_records:
#                 additional_payload = {**payload, 'additional': True}
#                 additional_ica_db_response = await asyncio.gather(fetch_data(url, additional_payload))
#                 print("additional_ica_db_response =", additional_ica_db_response)

#                 # Append additional records to the original response
#                 for response in additional_ica_db_response:
#                     if response and 'page' in response and 'records' in response['page']:
#                         ica_response[0]['page']['records'].extend(response['page']['records'])

#             modified_user_prompt = f"I need ingredient of {user_prompt}"
#             # Generate response using LLM
#             llm_response = call_llm(modified_user_prompt, ica_response, allhistory)
#             print("LLM Response = ", llm_response)

#             # Determine the message based on the presence of records
#             message = "Response from private" if has_records else "Response from OpenAI"

#             # Format the final response content
#             final_response_content = f"{llm_response}<span style='color:black;font-weight: bold;font-family: sans-serif;'>{message}</span>"
#             print("LLM Response Content = ", final_response_content)

#             # Evaluate the LLM response
#             rating_scores = evaluate_llm_response(user_prompt, llm_response)

#             # Return both LLM response and rating scores
#             print("finalresponse", final_response_content)
#             socketio.emit('show_loader', {'message': 'Hideloader'})
#             socketio.emit('response', {'message': final_response_content})
#             return final_response_content

#         except Exception as e:
#             # Log the error for debugging purposes
#             print(f"Error processing ingredient request: {e}")

#             # Stop the loader and send an error response
#             socketio.emit('show_loader', {'message': 'Hideloader'})
#             # socketio.emit('response', {'message': 'Error: Could not process your request. Please try again.'})
#             return 'Error: Could not process your request. Please try again.'
