import requests
 
def llm_response(prompt):
    try:
        llm_api = "https://genaiazurellmapp.azurewebsites.net/api/v1/chat"
       
        # Modify the prompt as needed to avoid content policy issues
        modified_prompt = (
            f"""This is the current prompt:give me ingredients of fruit oatmeal.This is my last prompt to
            help you build context, if required:None.These are my instructions:\n   
            You are an expert whose sole job is to take current prompt and the previous prompt,
            if the current prompt depends on the previous one, combine them into a single prompt that retains all essential details from both. 
            Otherwise, proceed with the current prompt alone. Example: - Previous Prompt: What are the ingredients for a Caesar salad?
            {prompt}
            Resulting System Prompt: What is the recipe for a Caesar salad?"
            """
        )
       
        payload = {"content": modified_prompt, "model": "gpt-4-vision"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
       
        print("Payload:", payload)  # For debugging to confirm payload content
        response = requests.post(llm_api, data=payload, headers=headers)
        response.raise_for_status()
       
        response_data = response.json()
        return response_data["response"]["response"]
   
    except requests.exceptions.RequestException as e:
        return f"Error sending request: {e}"
 
# Test the function by calling it with a sample prompt
if __name__ == "__main__":
    prompt = "give me ingredients of fruit oatmeal"
    print(llm_response(prompt))