#decision.py

# Code to call Gemini API for text generation
import requests
import json
import dotenv
import os 
import os
import json
import re
from google import genai
from google.genai.errors import ServerError
import yaml
import asyncio

# Import the local packages for MCP if needed
from mcp_servers.multiMCP import MultiMCP
from action.executor import run_user_code


# Load environment variables from .env file
dotenv.load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# Load prompt from file
with open("prompts/decision_prompt.txt", "r") as file:
    prompt_template = file.read()

# Load memory from JSON file
with open("memory/memory_state1.json", "r") as file:
    memory = json.load(file)
    whatsNeeded = memory["response"]["result_required"]

# Function to generate response from Gemini API
def generate_plan(perception_output):
    """Generates a response from the Gemini API based on user query about perception."""
    # print(f"Prompt \n {prompt_template + perception_output}")
    try:
        response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents = prompt_template + perception_output 
                )
    except ServerError as e:
        return f"Error: {e.message}"
    return response.text.strip()


# # Step 2: Now let's add tools and tool descriptions and see how the planning could be done.
# with open("config/mcp_server_config.yaml") as f:
#     configs = yaml.safe_load(f)["mcp_servers"]

# async def _init(configs):
#     m = MultiMCP(configs)
#     await m.initialize()
#     return m

# mcp = asyncio.run(_init(configs))


# # 2.2: Get the tool descriptions
# tool_descriptions_list = mcp.tool_description_wrapper()

# # Comnvert memory["response"] to string
# # memory_response_str = json.dumps(memory["response"])

# tool_descriptions_list = mcp.tool_description_wrapper()
# tool_descriptions = "\n".join(f"- `{desc.strip()}`" for desc in tool_descriptions_list)
# tool_descriptions = "\n\n### The ONLY Available Tools\n\n---\n\n" + tool_descriptions

# perception_output = json.dumps(memory["response"])
# decision_steps = generate_plan( "\n Perception output: \n" + perception_output + "\n" +tool_descriptions)


# ### 1. Extract python code
# import re
# from typing import Optional, Tuple

# def extract_python_code(plan_text: str) -> Optional[str]:
#     """
#     Extract the first python code block from plan_text.
#     Returns the code (string) or None if not found.
#     """
#     match = re.search(r'```python\s+(.*?)```', plan_text, re.DOTALL)
#     return match.group(1).strip() if match else None


# extract_python_code(decision_steps)




# # 1. Extract python code from the decision result
# code = extract_python_code(decision_steps)
# if code is None:
#     raise ValueError("No python code block found")

# # 2. Run the executor
# result = asyncio.run(run_user_code(code, mcp))

# print("EXECUTOR RESULT:", result)

# executor_result = result["result"]


# prompt_for_critic = "\n\n### Previous perception: \n\n---\n\n" + perception_output + "\n\n### Deicision: \n\n---\n\n" + decision_steps + "\n\n### Executor Result:\n\n---\n\n" + executor_result

# # Load prompt from file
# with open("prompts/perception_prompt.txt", "r") as file:
#     prompt_template = file.read()


# critic_input = prompt_template + "\n\n" + prompt_for_critic

# # Function to generate response from Gemini API
# def generate_perception_response(critic_input):
#     """Generates a response from the Gemini API based on user query about perception."""
#     try:
#         response = client.models.generate_content(
#                     model="gemini-2.0-flash",
#                     contents=critic_input #.format(user_query=user_query)
#                 )
#     except ServerError as e:
#         return f"Error: {e.message}"
#     return response.text.strip()

# generate_perception_response(critic_input)

# if __name__ == "__main__":
#     decision_steps = generate_plan("\n \n perception output in json format is:" + perception_output +"\n" +tool_descriptions)
#     print("Decision Making Steps:\n", decision_steps)









