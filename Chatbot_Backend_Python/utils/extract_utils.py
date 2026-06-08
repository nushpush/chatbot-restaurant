# import re
# import json
# import requests


# def extract_req_body(text):
#     try:
#         json_matches = re.findall(r'```json[\s\S]*?```|```[\s\S]*?```', text)
#         req_bodies = []
#         for match in json_matches:
#             json_string = re.sub(r'```json\s*|```', '', match).strip()
#             try:
#                 req_bodies.append(json.loads(json_string))
#             except json.JSONDecodeError:
#                 print(f"Failed to parse JSON: {json_string}")
#         return req_bodies
#     except Exception as e:
#         print(f"Error extracting req body: {e}")
#         return []

# # def getUrlReqbody(user_prompt):
# #     promtx_api = "https://genaiazurellmapp.azurewebsites.net/api/v1/chat"
# #     updated_content = f"{user_prompt} Also give its AI request. In each payload, insert the exact keyword from the given prompt."
# #     payload = {
# #         "content": updated_content,
# #         "model": "gpt-4-vision",
# #         "workspace": "qsr-chef",
# #     }
# #     try:
# #         headers = {
# #             "Content-Type": "application/x-www-form-urlencoded",
# #         }
# #         response = requests.post(promtx_api, data=payload, headers=headers)
# #         response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
# #         response_data = response.json()
# #         #print("response_Data: ", response_data.get("response", {}).get("response", ""))
# #         req_bodies = extract_req_body(response_data.get("response", {}).get("response", ""))
# #         # cotpromptswithLangchain.check_if_multiple_product_requested(req_bodies)
# #         return (req_bodies)
# #     except requests.exceptions.RequestException as e:
# #         return f'Error sending request: {e}'

# def getUrlReqbody(user_prompt):
#     promtx_api = "http://localhost:3002/generate"  # URL to call
#     updated_content = user_prompt
#     payload = {
#         "question": updated_content,  # Adjust payload structure as needed
#     }
#     try:
#         headers = {
#             "Content-Type": "application/json",  # Use application/json for JSON payload
#         }
#         response = requests.post(promtx_api, json=payload, headers=headers)
#         response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
#         response_data = response.json()
#         # print("response_data",response_data)
#         req_bodies = extract_req_body(response_data.get("api_details", ""))
#         return req_bodies
#     except requests.exceptions.RequestException as e:
#         return f'Error sending request: {e}'

import re
import json
import requests


def extract_req_body(response_text):
    # URL pattern to handle dynamic and static URL formats
    url_pattern = r'https://[^\s`\'"\)]+(?:\{[^\s\}]+\})?'

    # Improved payload pattern to handle variations and ensure correct capture, including code block delimiters
    payload_pattern = r"```json\s*({.*?})\s*```"

    # Extract all URLs
    urls = re.findall(url_pattern, response_text)

    # Extract all matching payloads within code blocks
    print("before extracting payload", urls)
    payload_matches = re.findall(payload_pattern, response_text, re.DOTALL)
    print("after extracting payload", payload_matches)

    pairs = []
    payload_index = 0
    # Pair URLs with the corresponding payloads, if available
    for i in range(len(urls)):
        try:
            # Match URL with payload or assign None if no valid payload is available
            if payload_index < len(payload_matches):
                payload = json.loads(payload_matches[payload_index])
                payload_index += 1
            else:
                payload = None
            pairs.append({"url": urls[i], "payload": payload})
        except json.JSONDecodeError:
            # Skip invalid JSON payloads
            pairs.append({"url": urls[i], "payload": None})
    return pairs


def llm_response(prompt):
    print("called llm_response")
    try:
        llm_api = "https://genaiazurellmapp.azurewebsites.net/api/v1/chat"
        payload = {"content": f"{prompt}", "model": "gpt-4-vision"}
        print("payload of llm_response:", payload)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        # socketio.emit('response', {'message': 'going for general chat'})
        response = requests.post(llm_api, data=payload, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        response_data = response.json()
        print("response_data in extract utils:", response_data)
        response = response_data["response"]["response"]
        return response
    except requests.exceptions.RequestException as e:
        return f"Error sending request: {e}"


def getUrlReqbody(user_prompt, last_prompt):
    print("called getUrlReqbody", type(last_prompt), last_prompt)

    promtx_api = "https://promptx-py-alpha.azurewebsites.net/api/food/v4/graphrag/query/businessquery"

    template = f"""
        This is the current Question:
        {user_prompt}
        
        This is my previous Question to help you build context, if required:
        {last_prompt}
        
        Instructions:
        1.Assess Dependency: Before combining, decide if the current question directly relies on the previous question for context. If the current question is understandable on its own, do not combine — use only the current question as the prompt.
        2.Reasoning Step: If you believe combining is necessary, briefly think through why the previous question adds essential context to the current question. Only add context if it directly clarifies or completes the question.
            Ways to assess whether combining is necessary:
            Contextual Carryover with Modification:- "When a prompt asks for 'the same' or 'similar' information as a previous query, adapt the previous context to fit the new item or attribute mentioned. For example, if I first asked for 'sugar content' and then 'the same for salt,' interpret this as requesting the 'salt content.'”
            Contextual Substitution Based on Keywords:- "If a prompt references a prior query with terms like 'the same,' 'similar,' or 'as before,' assume I am asking for the same type of information but substitute the specific items or attributes as specified in the new prompt."
            Adjusting Context by Replacing Item Names:- "When a follow-up prompt uses 'the same' or similar wording, retain the context structure but replace specific terms to match the new prompt. For example, if I ask for 'sugar content' and then say 'the same for salt,' understand it as a request for 'salt content.'"
            Interpreting 'Same' Requests for Related Data:- "Treat phrases like 'the same' as a prompt to retrieve similar information but change the specific item to match the new query. Maintain the query type but switch items (e.g., from 'sugar' to 'salt') as mentioned."
            Contextual Reference Matching:- "When the phrase 'the same' is used, reference the structure of the previous query, adjusting the item or attribute as specified. So if the prior prompt was about 'sugar content' and the new one asks for 'the same for salt,' understand this as 'salt content.'"
        3.Avoid Unnecessary Context: Keep the rephrased or combined question as concise as possible without additional assumptions.
        4.Generate the Final Prompt: Based on your assessment, either:
            Use only the current question if independent, or
            Form a combined question only if context is essential.
            Do not add the clarifications in response.
        5. Follow below template to generate the final prompt:
            Clarification: 
            Updated Prompt: 
    
        Contextual Dependency:
            Example 1:
            - Previous Question: What are the ingredients for a Caesar salad?
            - Current Question: Can you give me the recipe for the above dish?
            Updated Prompt: What is the recipe for a Caesar salad? # This "Combined Question:" is for example only; do not include it in the response.
        
            Example 2 (Handling Personal Information):
            - Previous Question: What are the details of customer named Apeksha?
            - Current Question: What is the feedback for the customer mentioned previously?
            Updated Prompt: What is the feedback for the customer named Apeksha? # This "Combined Question:" is for example only; do not include it in the response.
            
        Independent case:
            Example 1:
            - Previous Question: What is the calorie count and allergen information for fruit oatmeal and hotcakes?
            - Current Question: Which products are for breakfast.
            Updated Prompt: Which products are for breakfast. # This "Combined Question:" is for example only; do not include it in the response.
        """

    # print("template:", template)
    llm_called = llm_response(template)
    print("llm_called:", llm_called)
    print(type(llm_called))
    # data = json.loads(llm_called)
    # print("Updated",data["Updated Prompt"])
    updated_prompt = re.search(r"Updated Prompt:\s*(.*)", llm_called)
    updated_prompt_value = updated_prompt.group(1)  # Access the matched text
    payload = {
        "index_name": "grfap",
        "prompt": updated_prompt_value,
        "model": "gpt-4o",
        "temperature": 0,
        "top_p": 0.2,
        "max_tokens": 2000,
    }
    print("payload of call graphgrag:", payload)

    try:
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(promtx_api, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print("response_data:", response_data)

        # Assuming that 'result' contains the text to be parsed
        result = response_data.get("result", "No result found")
        print("final", result)

        # Extract the URLs and payload pairs from the result
        extracted_info = extract_req_body(result)
        print("Extracted Info:", extracted_info)

        result_object = {"extracted_info": extracted_info, "updated_prompt": llm_called}
        print("result_object in extract_utils:", result_object)
        return result_object

    except requests.exceptions.RequestException as e:
        return {"error": f"Error sending request: {e}"}
