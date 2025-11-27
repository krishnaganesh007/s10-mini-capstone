import json
import os
from datetime import datetime

class SessionState:
    def __init__(self, session_id, user_query):
        self.session_id = session_id
        self.filepath = os.path.join("memory", f"{session_id}.json")
        
        self.data = {
            "session_id": session_id,
            "original_query": user_query,
            "perception": {},
            "plan_versions": [], 
            "final_answer": None,
            "status": "ACTIVE"
        }
        self.start_new_plan_version() 
        self.save()

    # --- READ METHODS ---
    @property
    def query(self):
        return self.data["original_query"]

    @property
    def global_perception(self):
        return self.data["perception"]

    @property
    def current_steps(self):
        if not self.data["plan_versions"]: return []
        return self.data["plan_versions"][-1]["steps"]
    
    @property
    def current_plan_text(self):
        if not self.data["plan_versions"]: return []
        return self.data["plan_versions"][-1].get("plan_text", [])

    def get_last_step(self):
        steps = self.current_steps
        return steps[-1] if steps else None

    def get_all_history(self):
        return self.data["plan_versions"]

    # --- WRITE METHODS ---
    def start_new_plan_version(self):
        """Starts a fresh Iteration with empty steps and plan text."""
        self.data["plan_versions"].append({
            "iteration_index": len(self.data["plan_versions"]) + 1,
            "plan_text": [], # <--- NEW FIELD
            "steps": []
        })
        self.save()

    def update_plan_text(self, text_list):
        """Updates the human-readable strategy for the current iteration."""
        if self.data["plan_versions"]:
            self.data["plan_versions"][-1]["plan_text"] = text_list
            self.save()

    def update_global_perception(self, perception_data):
        self.data["perception"] = perception_data
        self.save()

    def add_plan_step(self, step_data):
        self.data["plan_versions"][-1]["steps"].append(step_data)
        self.save()

    def update_execution_result(self, result):
        if self.current_steps:
            self.current_steps[-1]["execution_result"] = result
            self.save()

    def update_step_critique(self, critique_data):
        if self.current_steps:
            last_step = self.current_steps[-1]
            last_step["perception"] = critique_data
            status = "completed" if critique_data.get("local_goal_achieved") else "failed"
            last_step["status"] = status
            
            if critique_data.get("original_goal_achieved"):
                self.data["final_answer"] = critique_data.get("solution_summary")
                self.data["status"] = "COMPLETED"
            self.save()

    def save(self):
        os.makedirs("memory", exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)