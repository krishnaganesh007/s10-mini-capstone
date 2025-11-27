# perception.py
import json
import os
import dotenv
from google import genai

dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("prompts/perception_prompt.txt", "r") as f:
    PROMPT_TEMPLATE = f.read()

class PerceptionAgent:
    def __init__(self):
        self.model = "gemini-2.0-flash"

    def _call_llm(self, prompt):
        try:
            response = client.models.generate_content(
                model=self.model, contents=prompt
            )
            return json.loads(self._clean_json(response.text))
        except Exception as e:
            return {"error": str(e), "local_goal_achieved": False}

    def _clean_json(self, text):
        text = text.replace("```json", "").replace("```", "").strip()
        s, e = text.find('{'), text.rfind('}')
        return text[s:e+1] if s != -1 else "{}"

    # --- READ/WRITE PATTERN ---
    
    def analyze_intent(self, state):
        """
        Reads: state.query
        Writes: updates state.perception
        """
        prompt = PROMPT_TEMPLATE.format(
            mode="INITIAL",
            user_query=state.query,
            global_requirement="None",
            code="None",
            executor_output="None"
        )
        
        print("🧠 Perception: Analyzing Global Intent...")
        result = self._call_llm(prompt)
        
        # WRITE to Blackboard
        state.update_global_perception(result)
        print(f"   -> Intent: {result.get('result_requirement')}")

    def critique_last_step(self, state):
        """
        Reads: state.global_perception, state.get_last_step()
        Writes: updates state.last_step.perception
        """
        last_step = state.get_last_step()
        if not last_step: return

        prompt = PROMPT_TEMPLATE.format(
            mode="CRITIC",
            user_query=state.query,
            global_requirement=state.global_perception.get("result_requirement"),
            code=last_step.get("code"),
            executor_output=json.dumps(last_step.get("execution_result"))
        )

        print("🧐 Critic: Evaluating execution...")
        result = self._call_llm(prompt)
        
        # WRITE to Blackboard
        state.update_step_critique(result)
        status = "✅ Passed" if result.get("local_goal_achieved") else "❌ Failed"
        print(f"   -> Result: {status} | {result.get('local_reasoning')}")