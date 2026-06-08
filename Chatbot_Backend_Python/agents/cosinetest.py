from openai import AzureOpenAI
 
# Azure OpenAI settings
AZURE_OPENAI_API_KEY = "1b04d6c0973d41269e2898f830c6bc4e"
AZURE_OPENAI_ENDPOINT = "https://genai-poc-promptiq.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-04-01-preview"
DEPLOYMENT_NAME = "genailllmpocmodel"
 
# Initialize the AzureOpenAI client
azure_openai = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
)
 
def generate_response(prompt):
    """Function to take a user prompt and generate a response using Azure OpenAI with streaming enabled."""
   
    # Create the content string using the provided structure
    content = (
        "This is the current prompt:\n"
        f"{prompt}\n"
        "This is my last prompt to help you build context, if required:\n"
        "give me recipe of sausage griddles.\n"
        "These are my instructions:\n\n"
        "    You are an expert whose sole job is to take current prompt and the previous prompt, if the current prompt depends on the previous one, \n"
        "    combine them into a single prompt that retains all essential details from both. Otherwise, proceed with the current prompt alone.\n"
        "    Example: - Previous Prompt: \"What are the ingredients for a Caesar salad?\" \n"
        "    - Current Prompt: \"Can you give me the recipe for the above dish?\" \n"
        "    Resulting System Prompt: \"What is the recipe for a Caesar salad?\"\n    ."
    )
 
    # Create a completion with the specified deployment name and streaming enabled
    response = azure_openai.completions.create(
        model=DEPLOYMENT_NAME,
        prompt=content,  # Use the constructed content
        max_tokens=2000,
        temperature=0.7,
        stream=True  # Enable streaming
    )
   
    # Process the streaming response
    full_response = ""
    for chunk in response:
        if 'choices' in chunk:
            for choice in chunk['choices']:
                if 'text' in choice:
                    full_response += choice['text']
 
    return full_response
 
# Example usage
if __name__ == "__main__":
    prompt = "give me the total calorie for above dish."
    response_text = generate_response(prompt)
    print("Generated Response:", response_text)