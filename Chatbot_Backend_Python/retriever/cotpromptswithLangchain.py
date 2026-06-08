import time

import openai
import json
import requests
import regex
from flask import request, jsonify
import re
import utils.conversationalbuffer as conversation_context
from utils.keys import key
from openai import AzureOpenAI
from contextlib import redirect_stdout
from app import socketio
from utils import extract_req_body, getUrlReqbody
from flask import session
keys = key()

# dotenv.load_dotenv()

openai.api_type = "azure"
openai.api_base = keys['AZURE_OPENAI_ENDPOINT']
openai.api_version = "2024-04-01-preview"
openai.api_key = keys['AZURE_OPENAI_API_KEY']
content_safety_version = "2021-04-30"
openai_endpoint = keys['AZURE_OPENAI_ENDPOINT']
api_key = keys["AZURE_OPENAI_API_KEY"]


search_endpoint = keys["AZURE_NEW_AI_SEARCH_ENDPOINT"]
search_api_key = keys["AZURE_NEW_AI_SEARCH_API_KEY"]

api_base = keys['AZURE_GPT_4_ENDPOINT']
gpt_api_key=keys["AZURE_GPT_4_KEY"]
deployment_name = 'gpt-4-vision'
api_version = '2024-02-15-preview' # this might change in the future

history = " "
history_array=[]
currentPrompt = " "
productList=[]

def get_client(deployment, indexName=None):
    try:
        azure_api_key = keys["AZURE_OPENAI_API_KEY_WITHOUT_RAG"]
        azure_endpoint = keys["AZURE_OPENAI_ENDPOINT_WITHOUT_RAG"]
        api_version = "2024-02-01"

        if deployment == 'genailllmpocmodel':
            if indexName:
                # Return another client when indexName is provided
                # print(f"{openai_endpoint}/openai/deployments/{deployment}/extensions")
                return openai.AzureOpenAI(
                        base_url=f"{openai_endpoint}/openai/deployments/{deployment}/extensions",
                         api_key=api_key,
                        api_version="2023-08-01-preview",
                )
            else:
                # Return the existing client
                return openai.AzureOpenAI(api_key=azure_api_key, api_version=api_version, azure_endpoint=azure_endpoint)
        else:
            gpt_api_key = keys["AZURE_GPT_4_KEY"]
            api_base = keys["AZURE_GPT_4_ENDPOINT"]
            api_version = "2024-02-15-preview"
            return AzureOpenAI(
                api_key=gpt_api_key,
                api_version=api_version,
                base_url=f"{api_base}openai/deployments/{deployment}/chat/completions?api-version={api_version}",
            )
    except Exception as e:
        raise Exception(f"Error getting client: {e}")

def get_chat_response(client,model,messages,extra_body=None):
    try:
        if model == 'genailllmpocmodel' or model == 'genai4swecodingandunittesting':
            token = 2000
        else:
           token = 4000
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=token,
            extra_body=extra_body
        )
        if model == 'genailllmpocmodel' and extra_body:
            return response.choices[0].message
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error getting chat response: {e}")


def initate_cot(query):
    # print("In Cot Module with prompt")
    global currentPrompt
    global productList
    # check type of prompt
    currentPrompt = query
    # assitent_print(f"Recipe Finder : " +"Sure, let me search and provide you details")
    socketio.emit('show_loader', {'message': 'Loading...'})
    # socketio.emit('response', {'message': 'sure, let me search and provide you details'})
    # print(currentPrompt)

    if "recipe" in currentPrompt:
        invoke_recipeModule()
    elif "Product" in currentPrompt:
        return "You can become a backend developer."
    elif "ingrediants" in currentPrompt:
        return "You can become a Data Scientist"
    else:
        "You're too young to party"

def invoke_recipeModule():
    print("in invoke recipe")
    isMultiProcudt=check_if_multiple_product_requested()
    print("isMultiProcudt",isMultiProcudt)
    if len(productList) > 1:
        print("insideif")
        splitPrompt_process()
    else:
        print("inside else")
        checkSubType(productList[0])

def check_if_multiple_product_requested ():
    # print("in check_if_multiple_product_requested")
    global currentPrompt
    global productList
    productList = []
    # delimiters = [",", ";", "!", "and",".", "i need recipe of",]
    # for delimiter in delimiters:
    #     currentPrompt = "|".join(currentPrompt.split(delimiter))
    # productList = currentPrompt.split("|")
    # productList = list(filter(None, productList))
    # productList = list(filter(bool, productList))
    # productList = list(filter(len, productList))
    # productList = list(filter(lambda item: item, productList))
    # print("productList",productList)
    global reqbodies
    reqbodies=getUrlReqbody(currentPrompt)
    print("reqbodies",reqbodies)
    # Loop through the extracted request bodies
    for reqbody in reqbodies:
        for api, details in reqbody.items():
            # Get the payload from the request body
            payload = details.get('payLoad', {})
            fields = payload.get('fields', [])
            
            # Extract the 'regex' value which contains the product name
            for field in fields:
                regex = field.get('match', {}).get('regex', '')
                if regex and regex.lower() not in productList:
                    productList.append(regex.lower())
    if not productList:
        # Second attempt: Fallback to using delimiters to split the prompt
        delimiters = [",", ";", "!", "and", ".", "I need recipe of",]
        for delimiter in delimiters:
            currentPrompt = "|".join(currentPrompt.split(delimiter))
        
        # Split the prompt into potential product names
        productList = currentPrompt.split("|")
        
        # Clean up the productList by filtering out empty strings, None, and duplicates
        productList = list(filter(None, productList))
        productList = list(filter(bool, productList))
        productList = list(set(productList))

    print("productList", productList)
    # # Ensure productList contains unique product names
    # print("productList",productList)


def splitPrompt_process():
     # print("in splitPrompt_process")
     global productList
     print("productList",productList)
     # assitent_print(f"Recipe Finder : "+"you are looking for recipe of ")
     socketio.emit('show_loader', {'message': 'Hideloader'})
     initial_message = "Recipe Finder : you are looking for recipe of "
    
     if productList:
        # Join product names with commas and add to the initial message
        initial_message += ', '.join(productList)
    
     # Send the initial message with product list
     assitent_print(initial_message)
    #  socketio.emit('show_loader', {'message': 'Loading...'})
     for x in productList:
        checkSubType(x)
        assitent_print(f"Recipe Finder : "+"Going for next recipe.... ")
     
def checkSubType(item):
     print("in checkSubType for: "+item)
     llmResp=call_llm_and_ask_que("Which api should I hit to get product details of "+item+". Also give its Example req body.Do not give example output.")
     pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
     bodys=pattern.findall(str(llmResp[0]['response']))
     print("bodys",bodys)
     data = json.loads(bodys[0])
     print("data",data)
     token=get_token()
     apiRespJson=call_postapi(data["api1"]["url"],json.dumps(data["api1"]["payLoad"]), token )
     if apiRespJson["success"]==True:
         apiResp=apiRespJson["page"]["records"]
         if len(apiResp) ==0:
             assitent_print(f"Recipe Finder : "+"sorry we dont any "+item+"  product in our data please check back in some time")
         elif len(apiResp) ==1:
             productId=apiResp[0]["id"]
             # get_ingredients(productId, " need ingredients of "+item+". Also give its AI request.", item)
             get_recipe(productId, " need recipe of "+item+". Also give its AI request.", item)
         else:
             assitent_print(f"Recipe Finder: "+"we have multiple product with name "+item)
             for x in apiResp:
                 assitent_print("\t"+ x["fields"]["name"])
             assitent_print(f"Recipe Finder: "+" so please confirm which product recipe is required")
             print("")
             #  Set the confirmation state
            #  user_input = input("User: ")
             session['apiResp'] = apiResp  # Set the apiResp in the session
             session['item'] = item  # Store the item name in the session
             session['awaiting_confirmation'] = True  # Set awaiting confirmation flag
            #  if user_input.lower() in ["exit", "quit"]:
            #     return("Ending the conversation. Goodbye!")
            #  elif any(str(tag["fields"]["name"]).lower() == user_input.lower() for tag in apiResp):
            #     checkSubType(user_input)
            #  else:
            #      assitent_print(f"Recipe Finder: "+"you changed the topic, going for general chat" )
            #      assitent_print(f"Assistent : " + str(call_llm_and_ask_que(user_input)))
            #      return


     else:
        assitent_print(f"Recipe Finder: "+"unabale to get recipe at this moment for "+item+" please try after sometime")

def handle_product_confirmation(user_input):
    apiResp = session.get('apiResp')
    session['awaiting_confirmation'] = False
    if any(str(tag["fields"]["name"]).lower() == user_input.lower() for tag in apiResp):
        return checkSubType(user_input)
    else:
        assitent_print(f"Recipe Finder: "+"you changed the topic, going for general chat" )
        assitent_print(f"Assistent : " + str(call_llm_and_ask_que(user_input)))
        return 

def get_ingredients(productId, prompt, item):
    llmResp1=call_llm_and_ask_que(prompt)
    pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
    bodys=pattern.findall(str(llmResp1[0]['response']))
    # print ("body to get the Recipe:" +str(bodys))
    data = json.loads(bodys[0])
    # print(data)
    token=get_token()
    url=str(data["api3"]["url"])
    apiResp=call_postapi(url.replace("{entityId}",productId),json.dumps(data["api2"]["payLoad"]), token )
    # print(apiResp)
    if apiResp["success"]==True:

        apiRespList=apiResp["page"]["records"]
        if len(apiRespList) > 0:
            assitent_print(f"Recipe Finder: "+"here is the ingredients of "+item)
            for x in apiRespList:
                assitent_print("recipe : " + x["fields"]["recipe"])
                assitent_print("preparation_difficulty_level : " + x["fields"]["preparation_difficulty_level"])
                assitent_print("preparation_time : " + x["fields"]["preparation_time"])
                assitent_print("unit : " + x["fields"]["unit"])
                assitent_print("cuisine_type : " + x["fields"]["cuisine_type"])
        else:
            assitent_print(f"Recipe Finder: "+"we are unable to find ingredients for "+item+" please try after sometime")
    else:
        assitent_print(f"Recipe Finder: "+"unabale to get ingredients at this moment for "+item+" please try after sometime")

    get_recipe(productId, " need recipe of "+item+". Also give its AI request.", item)


def get_recipe(productId, prompt, item):
    llmResp1=call_llm_and_ask_que(prompt)
    print("llmResp1",llmResp1)
    pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
    bodys=pattern.findall(str(llmResp1[0]['response']))
    print ("body to get the Recipe:" +str(bodys))
    data = json.loads(bodys[0])
    # print(data)
    token=get_token()
    url=str(data["api2"]["url"])
    apiResp=call_postapi(url.replace("{entityId}",productId),json.dumps(data["api2"]["payLoad"]), token )
    # print(apiResp)
    if apiResp["success"]==True:

        apiRespList=apiResp["page"]["records"]
        if len(apiRespList) > 0:
            socketio.emit('show_loader', {'message': 'Hideloader'})
            assitent_print(f"Recipe Finder: "+"here is the Recipe of "+item)
            for x in apiRespList:
                assitent_print("recipe : " + x["fields"]["recipe"])
                assitent_print("preparation_difficulty_level : " + x["fields"]["preparation_difficulty_level"])
                assitent_print("preparation_time : " + x["fields"]["preparation_time"])
                assitent_print("unit : " + x["fields"]["unit"])
                assitent_print("cuisine_type : " + x["fields"]["cuisine_type"])
        else:
            assitent_print(f"Recipe Finder: "+"we are unable to find recipe for "+item+" please try after sometime")
    else:
        assitent_print(f"Recipe Finder: "+"unabale to get recipe at this moment for "+item+" please try after sometime")
    # return apiRespList

def call_llm_and_ask_que(prompt):
    # print("in call_llm_and_ask_que with prompt: "+prompt)
    global history
    global history_array
    # prompt = str(request.get_json()['content']) + "Which api should I hit. Also give its Example req body.Do not give example output.";
    index = "qsr-chef"
    deployment = "genailllmpocmodel"
    # prompt = request.form.get('content')
    # index = request.form.get('workspace')
    # deployment = "genailllmpocmodel"
    client = get_client(deployment, index)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": ' '.join(history_array)+"Also refer to the above context"+ prompt}
    ]
    try:
        extra_body = {
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": search_endpoint,
                        "key": search_api_key,
                        "indexName": index
                    }
                }
            ]
        }
        response = get_chat_response(client, deployment, messages,extra_body)
        gen_response = response.content.strip()
        # print("gen_response",gen_response)
        history = "role: user, content: "+prompt + "role: assistant, content: "+gen_response
        history_array=conversation_context.update_history(history, history_array)
        if "requested information is not available in the retrieved data." in gen_response:
            deployment = "gpt-4-vision"
            client = get_client(deployment)
            messages = [
                {"role": "system", "content": "You are a helpful assistant which is specializing in food and culinary-related questions. You can provide information on ingredients, recipes, cooking techniques, dietary advice, and restaurant recommendations. Please do not answer questions outside the scope of food and culinary topics."},
                {"role": "user", "content":' '.join(history_array)+"Also refer to the above context" + prompt}
            ]
            gen_response2 = get_chat_response(client, deployment, messages)
            gen_response2 = 'There is no response present in training data. Here is the generic response: ' + gen_response2
            history = "role: user, content: "+prompt + "role: assistant, content: "+gen_response2
            history_array=conversation_context.update_history(history, history_array)
            return {'response': remove_references(gen_response2)}, 200
        return {'response': remove_references(gen_response)}, 200
    except Exception as e:
        return {'error': 'An error occurred while processing the request.'}, 500

def remove_references(text):
    return re.sub(r'\[doc\d+\]', '', text)

def get_token():
    url = "https://dcponazure-account01.azurewebsites.net/api/v1/accounts/authenticate/"
    payload = "{\"credentials\": {\"username\": \"manusha\",\"password\": \"manusha\"},\"typeCodes\": [\"PERSON\"]}"
    headers = {
      'Content-Type': 'application/json',
      'X-TENANT': 'QSR',
      'X-USER-ID': 'manusha'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()["authToken"]

def call_postapi(url,payload, token):
    # print(url)
    # print(payload)
    headers = {
      'Content-Type': 'application/json',
      'X-TENANT': 'QSR',
      'X-USER-ID': 'manusha',
      'X-AUTHORIZATION': token
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print("responsein ica",response)
    return response.json()
output_log = []
# def assitent_print(text):
#     global output_log
#     output_log.append(text)
#     print("")
#     for char in text:
#         print(char, end="", flush=True)
#         time.sleep(0.04)

def assitent_print(text):
    # print("Entering assitent_print")
    # print("textinassistantprint", text)
    # try:
    #     socketio.emit('response', {'message': text})
    #     # socketio.emit('response', {'message': 'Test message from assitent_print'})
    #     # print("Emitted message")
    # except Exception as e:
    #     print(f"Error emitting message: {e}")
    message = ""
    for char in text:
        message += char
        print(char, end="", flush=True)
    print("message",message)
    socketio.emit('response', {'message': message})


   
    



# Global variable to store all messages




