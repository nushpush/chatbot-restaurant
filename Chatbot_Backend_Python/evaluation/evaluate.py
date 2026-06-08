import json
import mlflow
import os
import pandas as pd
from flask import jsonify, request
import asyncio
from guardrail import food_guardrails, prompt_filtering

from utils.keys import key
keys = key()
os.environ["OPENAI_DEPLOYMENT_NAME"] = keys['AZURE_OPENAI_DEPLOYMENT_ID']
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2024-04-01-preview"
os.environ["OPENAI_API_BASE"] = keys['AZURE_OPENAI_ENDPOINT']
os.environ["OPENAI_API_KEY"] = keys['AZURE_OPENAI_API_KEY']
search_endpoint = keys['AZURE_NEW_AI_SEARCH_ENDPOINT']
search_api_key = keys['AZURE_NEW_AI_SEARCH_API_KEY']

async def async_llm_evaluate():
    print("inside async_llm_evaluate")
    inputs = request.json.get("inputs", [])
    response = request.json.get("response", [])
    
    
    
    # Defining the model function
    def model(inputs):
        print("inputs", inputs)
        print("response", response)
        return response

    # Defining the ground truth function
    def ground_truth(inputs):
        ground_truth = []
        first_question = str(inputs[0])
        print("first", first_question)
        response = inputs
        print("response", response)

        if isinstance(response, dict) and 'response' in response:
            response_text = response['response']
        elif isinstance(response, list) and len(response) > 0:
            response_text = response[0]  # Adjust this based on the actual content of the list
        else:
            raise TypeError("Unexpected type or missing 'response' key.")
        
        response_text = response_text.replace('\n', ' ').replace('    ', ' ').replace('-', '')
        ground_truth.append(response_text)
        print("ground_truth", ground_truth)
        return ground_truth

    # Continue with evaluation as usual
    ground_truth = ground_truth(inputs)
    eval_data = pd.DataFrame(
        {
            "inputs": inputs,
            "ground_truth": ground_truth,
        }
    )
    results = mlflow.evaluate(
        model,
        eval_data,
        targets="ground_truth",
        model_type="question-answering",
        evaluators="default",
        predictions="result",
        extra_metrics=[
            mlflow.metrics.latency(),
            mlflow.metrics.genai.answer_similarity(),
            mlflow.metrics.genai.answer_correctness(),
            mlflow.metrics.genai.answer_relevance(),
            mlflow.metrics.ari_grade_level(),
            mlflow.metrics.flesch_kincaid_grade_level()
        ],
    )
    
    eval_table = results.tables["eval_results_table"]
    df = pd.DataFrame(eval_table)
    asyncio.sleep(2000)
    
    json_results = results.tables["eval_results_table"].to_json(orient="records")
    print("json_results", json_results)
    
    # Call process_input to check if the input is food-related
    

    # Otherwise, just return the evaluation results
    return json_results

    
