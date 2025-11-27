# Agent has to do the following:
# Step 1: Initiate the mcp servers and keep them ready
# Step 2: Get the user input
# Step 3: Create a new session

# Step 4: Call the search module and get memories (long term memory) matching with the user query
# Step 4.1: Now send the user query to perception and ask it to generate the current perception state
# Step 4.2: If it has answered, then exit and produce the results and save in session memory
# Step 4.3: If not, send the perception output to decision module to get the next steps

# Step 5: Decision module will return the plan text and the python code to be executed
# Step 5.1 : Take the first code and run the executor to get the results --> Then send output to critic --> update the session with the result
# Step 5.2 : Take the second code and run the executor to get the results --> Then send output to critic --> update the session with the result
# Step 5.3 : Take the third code and run the executor to get the results --> Then send output to critic --> update the session with the result

# Step 6: If the "FINAL ANSWER" is found in the decision plan, then exit and produce the results and save in session memory
# Step 6.1: If not, repeat from Step 4.2
# Step 6.2: Continue this loop until either FINAL ANSWER is found or max iterations reached (say 5)

# Now writing the code for agent.py

# agent.py
import asyncio
from perception import generate_perception_response, parse_response_to_obj, extract_json_text
from decision import generate_plan
from action.executor import run_user_code
import json
import os
from datetime import datetime
import yaml
from mcp_servers.multiMCP import MultiMCP
import logging


MAX_ITERATIONS = 5

# Define all the necessary functions here (if any)

# Function to create a new session:
# def create_new_session():
#     """Checks if a new session ID is needed or creates one."""

#     return "session-" + datetime.now().strftime("%Y%m%d-%H%M%S")

    


# def write_to_memory(filename: str, data: dict) -> None:
#     """Writes the given data to a JSON file in the memory folder."""
#     memory_folder = "memory"
#     os.makedirs(memory_folder, exist_ok=True)
#     filepath = os.path.join(memory_folder, filename)
#     with open(filepath, "w", encoding="utf-8") as file:
#         json.dump(data, file, indent=4, ensure_ascii=False)


# def log_event(session_id: str, event_type: str, content: str) -> None:
#     """Logs an event to the session log file."""
#     log_folder = "logs"
#     os.makedirs(log_folder, exist_ok=True)
#     log_filepath = os.path.join(log_folder, f"{session_id}.log")
#     logging.basicConfig(filename=log_filepath, level=logging.INFO,
#                         format='%(asctime)s - %(levelname)s - %(message)s')
#     logging.info(f"{event_type}: {content}")

import os
import logging

def log_event(session_id: str, event_type: str, content: str) -> None:
    """Logs an event to both terminal and file."""

    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)
    log_filepath = os.path.join(log_folder, f"{session_id}.log")

    logger = logging.getLogger(session_id)
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers
    if not logger.handlers:

        # 1. File handler
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)

        # 2. Terminal (console) handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)

        # Add both handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Log the message
    logger.info(f"{event_type}: {content}")



# 1. Initialize MCP servers
with open("config/mcp_server_config.yaml") as f:
    configs = yaml.safe_load(f)["mcp_servers"]

async def _init(configs):
    m = MultiMCP(configs)
    await m.initialize()
    return m

mcp = asyncio.run(_init(configs))

tool_descriptions_list = mcp.tool_description_wrapper()
tool_descriptions = "\n".join(f"- `{desc.strip()}`" for desc in tool_descriptions_list)
tool_descriptions = "\n\n### The ONLY Available Tools\n\n---\n\n" + tool_descriptions



# # Let's just build the main agent loop
# def agent_loop(query):
     
#     # 2. Create a new session
#     session_id = "session-" + datetime.now().strftime("%Y%m%d-%H%M%S")
#     print(f"Created new session: {session_id}")
#     log_event(session_id, "SESSION_START", f"New session started for query: {query}")
#     iteration = 0

#     # 3. Start the agent loop
#     while iteration < MAX_ITERATIONS:
#         iteration += 1
#         print(f"\n--- Iteration {iteration} ---")

#         # 4. Get perception output
#         raw_response = generate_perception_response(query)
#         json_text = extract_json_text(raw_response)
#         perception_data = parse_response_to_obj(json_text)
#         log_event(session_id, "PERCEPTION_OUTPUT", perception_data)

#         # Check if perception has provided a final answer
#         if "final_answer" in perception_data:
#             final_answer = perception_data["final_answer"]
#             print(f"Final Answer from Perception: {final_answer}")
#             log_event(session_id, "FINAL_ANSWER", final_answer)
#             break

#         # 5. Get decision steps
#         perception_output_str = json.dumps(perception_data)
#         decision_steps = generate_plan("\n Perception output: \n" + perception_output_str + tool_descriptions )
#         log_event(session_id, "DECISION_STEPS", decision_steps)

#         # Extract and execute code from decision steps
#         # For simplicity, let's assume decision_steps contains executable code snippets
#         code_snippets = decision_steps.split("```python")
#         for snippet in code_snippets[1:]:  # Skip the first split part
#             code = snippet.split("```")[0].strip()
#             print(f"Executing code:\n{code}")
#             execution_result = asyncio.run(run_user_code(code, mcp))
#             log_event(session_id, "CODE_EXECUTION_RESULT", execution_result)

#             # Here you would normally send the execution result back to perception or critic
#             # For this example, we will just print it
#             print(f"Execution Result: {execution_result}")
        
#         # 6. Send execution result back to perception for next iteration


#     else:
#         print("Max iterations reached without finding a final answer.")
#         log_event(session_id, "MAX_ITERATIONS_REACHED", "No final answer found.")


import asyncio
import json
import os
from datetime import datetime

def write_session(session_filename: str, session_data: dict):
    """Write the entire session dictionary to a single JSON file."""
    folder = os.path.dirname(session_filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(session_filename, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=4, ensure_ascii=False)



# --- helper to call critic with only executor output (inline version) ---
def call_critic_with_executor_output(
    executor_result: dict,
    user_query: str,
    previous_perception: dict = None,
    session: dict = None,
    session_filename: str = None,
    max_executor_chars: int = 2000
):
    """
    Send only the executor output (and minimal context) to the Perception agent in CRITIC mode,
    parse the response JSON, optionally append to session, and return (raw_critic_text, parsed_obj).
    Assumes these functions exist in module scope:
      - generate_perception_response(prompt: str) -> str
      - extract_json_text(raw: str) -> str
      - parse_response_to_obj(json_text: str) -> dict
      - write_session(session_filename, session)  # optional
    """
    try:
        exec_str_full = json.dumps(executor_result, default=str)
    except Exception:
        exec_str_full = str(executor_result)

    if len(exec_str_full) > max_executor_chars:
        exec_str = "[TRUNCATED] " + exec_str_full[-max_executor_chars:]
    else:
        exec_str = exec_str_full

    critic_prompt = (
        "You are a Perception/Critic Agent. Evaluate whether the original goal is achieved\n"
        "based on the executor output below. Provide output in the exact JSON schema expected.\n\n"
        "user_query: " + json.dumps(user_query) + "\n\n"
        "previous_perception: " + (json.dumps(previous_perception) if previous_perception else "null") + "\n\n"
        "executor_output: " + exec_str + "\n"
    )

    raw_critic = generate_perception_response(critic_prompt)

    try:
        json_text = extract_json_text(raw_critic)
        parsed = parse_response_to_obj(json_text)
    except Exception as e:
        parsed = {
            "entities": [],
            "result_required": "",
            "original_goal_achieved": False,
            "reasoning": f"Failed to parse critic response: {e}",
            "local_goal_achieved": False,
            "local_reasoning": "parsing_error",
            "_raw_critic": raw_critic
        }

    if session is not None:
        session.setdefault("perception", {}).setdefault("critic_raw", []).append(raw_critic)
        session["perception"].setdefault("critic", []).append(parsed)
        session.setdefault("executor", []).append({
            "iteration": len(session.get("executor", [])),
            "raw_output": executor_result
        })
        session.setdefault("run_log", []).append({"ts": datetime.utcnow().isoformat(), "event": "critic_called"})
        if session_filename:
            try:
                write_session(session_filename, session)
            except Exception:
                # persist failure should not break loop
                pass

    return raw_critic, parsed


# --- Main agent loop (synchronous, uses asyncio.run for async executor calls) ---
def agent_loop(query):
    # 2. Create a new session
    session_id = "session-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f"Created new session: {session_id}")
    log_event(session_id, "SESSION_START", f"New session started for query: {query}")

    # Minimal session state (stored in a single file if desired)
    session = {
        "session_id": session_id,
        "start_timestamp": datetime.utcnow().isoformat(),
        "original_query": query,
        "perception": {"initial": None, "initial_raw": None, "critic": [], "critic_raw": []},
        "plan_versions": [],
        "executor": [],
        "run_log": [],
        "complete": False,
        "final_answer": None
    }
    session_filename = os.path.join("memory", f"{session_id}.json")
    try:
        os.makedirs("memory", exist_ok=True)
        write_session(session_filename, session)
    except Exception:
        # If write_session isn't available or fails, continue without persistent snapshot
        pass

    iteration = 0

    # 3. Start the agent loop
    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # 4. Get perception output
        raw_response = generate_perception_response(query)
        try:
            json_text = extract_json_text(raw_response)
            perception_data = parse_response_to_obj(json_text)
        except Exception as e:
            perception_data = {
                "entities": [],
                "result_required": query,
                "original_goal_achieved": False,
                "reasoning": f"Perception parse error: {e}",
                "local_goal_achieved": False,
                "local_reasoning": "parsing_error"
            }

        session["perception"]["initial_raw"] = raw_response
        session["perception"]["initial"] = perception_data
        session["run_log"].append({"ts": datetime.utcnow().isoformat(), "event": "perception_obtained"})
        log_event(session_id, "PERCEPTION_OUTPUT", json.dumps(perception_data, ensure_ascii=False))

        # Check if perception has provided a final answer
        if perception_data.get("final_answer") or perception_data.get("original_goal_achieved"):
            final_answer = perception_data.get("final_answer") or perception_data.get("result_required")
            print(f"Final Answer from Perception: {final_answer}")
            log_event(session_id, "FINAL_ANSWER", final_answer)
            session["complete"] = True
            session["final_answer"] = final_answer
            try:
                write_session(session_filename, session)
            except Exception:
                pass
            break

        # 5. Get decision steps
        perception_output_str = json.dumps(perception_data, ensure_ascii=False)
        decision_steps = generate_plan("\n Perception output: \n" + perception_output_str + tool_descriptions)
        log_event(session_id, "DECISION_STEPS", decision_steps)
        session.setdefault("plan_versions", []).append({"iteration": iteration, "raw": decision_steps})

        # Extract and execute code from decision steps
        code_snippets = decision_steps.split("```python")
        for snippet in code_snippets[1:]:  # Skip the first split part
            code = snippet.split("```")[0].strip()
            print(f"Executing code:\n{code}")

            # execute the code using the async executor (synchronous caller)
            try:
                execution_result = asyncio.run(run_user_code(code, mcp))
            except RuntimeError as e:
                # if asyncio.run cannot be used (running loop), raise informative error
                execution_result = {"status": "error", "error": f"asyncio.run error: {e}"}
            except Exception as e:
                execution_result = {"status": "error", "error": str(e)}

            # record execution result
            session.setdefault("executor", []).append({
                "iteration": iteration,
                "code": code,
                "raw_output": execution_result
            })
            log_event(session_id, "CODE_EXECUTION_RESULT", json.dumps(execution_result, default=str))

            # Print execution outcome
            print(f"Execution Result: {execution_result}")

            # 6. Send execution result back to perception (critic) for next iteration
            raw_critic, parsed_critic = call_critic_with_executor_output(
                executor_result=execution_result,
                user_query=query,
                previous_perception=perception_data,
                session=session,
                session_filename=session_filename
            )

            log_event(session_id, "CRITIC_OUTPUT", json.dumps(parsed_critic, ensure_ascii=False))
            print("Critic parsed:", parsed_critic)

            # If critic reports original goal achieved, stop
            if parsed_critic.get("original_goal_achieved"):
                session["complete"] = True
                session["final_answer"] = parsed_critic.get("solution_summary") or parsed_critic.get("result_required") or execution_result.get("result")
                session["end_timestamp"] = datetime.utcnow().isoformat()
                try:
                    write_session(session_filename, session)
                except Exception:
                    pass
                log_event(session_id, "SESSION_COMPLETE", "original_goal_achieved by critic")
                print("Original goal achieved by critic. Ending session.")
                return

        # persist session snapshot each iteration
        try:
            write_session(session_filename, session)
        except Exception:
            pass

    else:
        print("Max iterations reached without finding a final answer.")
        log_event(session_id, "MAX_ITERATIONS_REACHED", "No final answer found.")
        try:
            write_session(session_filename, session)
        except Exception:
            pass




if __name__ == "__main__":
    user_query = input("Enter your query about perception: ")
    agent_loop(user_query)

