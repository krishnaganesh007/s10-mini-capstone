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

# Load environment variables from .env file
dotenv.load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)


# client = genai.Client(
#     vertexai=True, project='gen-lang-client-0524715282', location='global', api_key=API_KEY
# )


# client.models.generate_content(
#                     model="gemini-2.0-flash",
#                     contents="who is god?"
#                 )

# Load prompt from file
with open("prompts/perception_prompt.txt", "r") as file:
    prompt_template = file.read()

# Function to generate response from Gemini API
def generate_perception_response(user_query):
    """Generates a response from the Gemini API based on user query about perception."""
    try:
        response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt_template.format(user_query=user_query
                                                    , previous_perception = None
                                                    , decision_plan_text = None
                                                    ,executor_output = None)
                )
    except ServerError as e:
        return f"Error: {e.message}"
    return response.text.strip()



def extract_json_text(s: str) -> str:
    """Extract the first JSON object found in a string (handles triple-backticks too)."""
    if not s:
        raise ValueError("Empty response string")
    # remove fenced code blocks if present
    s = s.replace("```json", "").replace("```", "").strip()
    # find the first { and the matching last } (simple heuristic)
    start = s.find('{')
    end = s.rfind('}')
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in response")
    return s[start:end+1]

def parse_response_to_obj(response: str) -> dict:
    """Try to parse response into a Python dict. Raises ValueError on failure."""
    json_text = extract_json_text(response)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        # helpful error if parsing fails
        raise ValueError(f"Failed to parse JSON: {e}\nJSON text was:\n{json_text}")

def write_to_memory(filename: str, data: dict) -> None:
    """Writes the given data to a JSON file in the memory folder."""
    memory_folder = "memory"
    os.makedirs(memory_folder, exist_ok=True)
    filepath = os.path.join(memory_folder, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    



# if __name__ == "__main__":
#     user_query = input("Enter your query about perception: ")
#     response = generate_perception_response(user_query)
#     filename = "memory_state1.json"
#     # Clean reponse before writing to memory
#     response = response.replace("```json", "").replace("```", "").strip()
#     parsed_inner = parse_response_to_obj(response)
#     write_to_memory(filename, {"query": user_query, "response": parsed_inner}) 
#     print("Response from Gemini API:")
#     print(response)
