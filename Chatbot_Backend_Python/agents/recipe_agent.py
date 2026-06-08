import os
import openai
from langchain import OpenAI as LangChainOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.tools import BaseTool
from flask import Flask, request, jsonify
from retriever import cotpromptswithLangchain
from socketio_instance import socketio

app = Flask(__name__)

os.environ["OPENAI_API_KEY"] = "1b04d6c0973d41269e2898f830c6bc4e"
# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


# Define a function to interact with OpenAI's ChatCompletion API
def get_chat_completion(messages, model="gpt-4-vision", temperature=0.7):
    response = openai.ChatCompletion.create(
        model=model, messages=messages, temperature=temperature
    )
    return response.choices[0].message["content"]


# Define a simple recipe tool to simulate recipe search
class RecipeTool(BaseTool):
    name: str = "Recipe Finder"  # Add a type annotation
    description: str = "Use this tool to find recipes based on user input."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callbacks = []  # Define an empty list for callbacks

    def _run(self, query: str) -> str:
        return cotpromptswithLangchain.initate_cot(query)

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async operations.")


# Instantiate the recipe tool
recipe_tool = RecipeTool()

# Define the prompt template for the chatbot
template = "You are a helpful assistant. Conversation history: {history}\n\nUser: {input}\nAssistant:"
prompt = PromptTemplate(input_variables=["history", "input"], template=template)

# Set up the LangChain memory to store conversation context
memory = ConversationBufferMemory(memory_key="history", input_key="input")


# Define the LLM using a function to handle completions
class OpenAIChatCompletion(LangChainOpenAI):
    def create(self, messages):
        return get_chat_completion(
            messages, model=self.model_name, temperature=self.temperature
        )


# Initialize the LLM with the OpenAIChatCompletion class
llm = OpenAIChatCompletion(
    model_name="gpt-4-vision",  # Use your desired model like "gpt-3.5-turbo" or "gpt-4"
    temperature=0.7,
)

# Initialize the conversation chain
# conversation_chain = ConversationChain(
#     llm=llm,
#     prompt=prompt,
#     memory=memory
# )

# Define the tools available to the agent
tools = [
    Tool.from_function(
        recipe_tool.run, name="Recipe Finder", description="Use to find recipes"
    )
]

# Initialize the agent with the conversation chain and tools
agent = initialize_agent(
    tools=tools,
    agent_type=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    llm=llm,
    memory=memory,
    verbose=True,
)


class RecipeAgent:
    def __init__(self):
        self.recipe_tool = RecipeTool()

    def get_recipe(self, query):
        return self.recipe_tool.run(query)


# Run the chatbot loop with recipe agent integration
# print("Chatbot is ready! Type 'exit' or 'quit' to end the conversation.")
# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("Ending the conversation. Goodbye!")
#         break
#     messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": user_input}
#     ]
#     if "recipe" in user_input.lower() or "how to make" in user_input.lower():
#         response = recipe_tool.run(user_input)
#     else:
#         response=cotpromptswithLangchain.call_llm_and_ask_que(user_input)
#         cotpromptswithLangchain.assitent_print(f"Assistant: {response[0]['response']}")
#         print("")

# @app.route('/recipecall', methods=['POST'])
# def recipecall():
#     data = request.json
#     user_input=data.get('content')
#     if not user_input:
#         return jsonify({'error': 'No content provided'}), 400
#     if "recipe" in user_input.lower() or "how to make" in user_input.lower():
#         response = recipe_tool.run(user_input)
#     else:
#         response=cotpromptswithLangchain.call_llm_and_ask_que(user_input)
#         cotpromptswithLangchain.assitent_print(f"Assistant: {response[0]['response']}")
#     return jsonify(response)

# if __name__ == "__main__":
#     app.run(debug=False, port=5000)
