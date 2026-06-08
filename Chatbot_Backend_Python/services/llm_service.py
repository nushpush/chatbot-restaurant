import requests
from socketio_instance import socketio

def call_llm(prompt, response, last_five_responses):
    
    try:
        llm_api = "https://genaiazurellmapp.azurewebsites.net/api/v1/chat"

        # payload = {
        #     "content": f"{response} {prompt} {last_five_response}",
        #     "model": "gpt-4-vision",
        # }
        # headers = {
        #     "Content-Type": "application/x-www-form-urlencoded",
        # }
        # print("payload111", payload)
        # response = requests.post(llm_api, data=payload, headers=headers)

        # response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        # response_data = response.json()
        # return response_data.get("response", {}).get("response", "")
        # Constructing the content based on the presence of last_five_response
        if last_five_responses:
            # If there are last responses, include them in the prompt
            content = (
                f"Here are the last five responses:\n{last_five_responses}.\n"
                f"This is the prompt:\n{prompt}.\n"
                f"This is the current response:\n{response}."
            )
        else:
            # If there are no last responses, just include the prompt and current response
            content = f"This is the prompt: {prompt}. This is the current response: {response}."

        print("content----------", content)
        payload = {
            "content": f"{response} {prompt} {last_five_responses}",
            "model": "gpt-4-vision"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        print("payload111", payload)
        response = requests.post(llm_api, data=payload, headers=headers)

        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        response_data = response.json()
        return response_data.get("response", {}).get("response", "")
    except requests.exceptions.RequestException as e:
        return f"Error sending request: {e}"


def evaluate_llm_response(content, final_response):
    evaluate_api = "https://genaiazurellmapp.azurewebsites.net/api/v1/llmevaluate"
    final_evaluate_payload = {"inputs": [content], "response": [final_response]}
    try:
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(
            evaluate_api, json=final_evaluate_payload, headers=headers
        )
        response.raise_for_status()
        evaluation_data = response.json()
        rating_score = [
            {
                "flesch_kincaid_grade_level/v1/score": evaluation.get(
                    "flesch_kincaid_grade_level/v1/score"
                ),
                "ari_grade_level/v1/score": evaluation.get("ari_grade_level/v1/score"),
                "answer_similarity/v1/score": evaluation.get(
                    "answer_similarity/v1/score"
                ),
                "answer_correctness/v1/score": evaluation.get(
                    "answer_correctness/v1/score"
                ),
                "answer_relevance/v1/score": evaluation.get(
                    "answer_relevance/v1/score"
                ),
            }
            for evaluation in evaluation_data
        ]
        return rating_score
    except requests.exceptions.RequestException as e:
        return f"Error sending request: {e}"
