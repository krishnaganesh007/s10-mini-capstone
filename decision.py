import json
import os
import dotenv
from google import genai

dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("prompts/decision_prompt.txt", "r") as f:
    PROMPT_TEMPLATE = f.read()

class DecisionAgent:
    def __init__(self, tool_descriptions):
        self.model = "gemini-2.0-flash"
        self.tool_descriptions = tool_descriptions

    def _format_full_history(self, all_versions):
        """
        Formats the history of ALL Iterations.
        """
        history_str = ""
        
        for version in all_versions:
            iter_num = version.get("iteration_index", 1)
            steps = version.get("steps", [])
            
            if not steps: continue
            
            history_str += f"\n=== ITERATION {iter_num} ===\n"
            
            for step in steps:
                status = step.get("status", "UNKNOWN")
                
                # Format Result (Truncated)
                result_raw = str(step.get("execution_result", ""))
                result_trunc = result_raw[:1000] + "..." if len(result_raw) > 1000 else result_raw
                
                # Format Perception
                perception = step.get("perception") or {}
                reasoning = perception.get("local_reasoning", "None")
                
                history_str += f"Step {step['index']}: {step.get('description', 'No desc')}\n"
                history_str += f"Status: {status}\n"
                history_str += f"Code: {step['code'][:100]}...\n"
                
                if status == "failed":
                    history_str += f"Output: {result_trunc}\n"
                    history_str += f"Critic: {reasoning}\n"
                else:
                    # On success, still show output (it might contain URLs for next step)
                    history_str += f"Output: {result_trunc}\n"
                
                history_str += "-" * 20 + "\n"
                
        if not history_str:
            return "No previous history. Start Iteration 1."
            
        return history_str

    def generate_next_step(self, state):
        # We pass get_all_history() now, not just current steps
        history_str = self._format_full_history(state.get_all_history())
        
        prompt = PROMPT_TEMPLATE.format(
            goal=state.global_perception.get("result_requirement"),
            tool_descriptions=self.tool_descriptions,
            history_context=history_str
        )

        print("🤔 Decision: Planning...")
        try:
            response = client.models.generate_content(
                model=self.model, contents=prompt
            )
            data = json.loads(self._clean_json(response.text))
            
            next_step_data = data.get("next_step", {})
            if not next_step_data.get("code") and next_step_data.get("type") != "FINAL_ANSWER":
                return False

            new_step = {
                "index": len(state.current_steps),
                "type": next_step_data.get("type", "CODE"),
                "code": next_step_data.get("code", ""),
                "description": next_step_data.get("description", ""),
                "status": "pending",
                "execution_result": None,
                "perception": None
            }
            
            state.add_plan_step(new_step)
            print(f"   -> Plan: {new_step['description']}")
            return True

        except Exception as e:
            print(f"Decision Error: {e}")
            return False

    def _clean_json(self, text):
        text = text.replace("```json", "").replace("```", "").strip()
        s, e = text.find('{'), text.rfind('}')
        return text[s:e+1] if s != -1 else "{}"