import asyncio
import yaml
from datetime import datetime
from state import SessionState
from perception import PerceptionAgent
from decision import DecisionAgent
from action.executor import run_user_code
from mcp_servers.multiMCP import MultiMCP

MAX_ITERATIONS = 5
MAX_STEPS = 3

class ExecutorAgent:
    def __init__(self, mcp_instance):
        self.mcp = mcp_instance

    async def execute_pending_step(self, state):
        step = state.get_last_step()
        if not step or step.get("execution_result") is not None or step.get("type") == "FINAL_ANSWER":
            return
        
        print(f"💻 Executor: Running Code for Step {step['index']}...")
        try:
            result = await run_user_code(step["code"], self.mcp)
        except Exception as e:
            result = {"status": "error", "message": str(e)}
        state.update_execution_result(result)

async def coordinator_loop(query):
    # Setup ...
    print("🔧 Coordinator: Initializing...")
    with open("config/mcp_server_config.yaml") as f:
        configs = yaml.safe_load(f)["mcp_servers"]
    mcp = MultiMCP(configs)
    await mcp.initialize()
    tools_str = "\n".join(mcp.tool_description_wrapper())
    
    perception_agent = PerceptionAgent()
    decision_agent = DecisionAgent(tool_descriptions=tools_str)
    executor_agent = ExecutorAgent(mcp)

    session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    state = SessionState(session_id, query)
    print(f"🚀 Session: {session_id}")

    perception_agent.analyze_intent(state)
    if state.global_perception.get("original_goal_achieved"): return

    for iteration_idx in range(MAX_ITERATIONS):
        print(f"\n╔════════════════════════════════════╗")
        print(f"║  ITERATION {iteration_idx + 1} (Strategy {iteration_idx + 1})    ║")
        print(f"╚════════════════════════════════════╝")
        
        if iteration_idx > 0: state.start_new_plan_version()
        strategy_valid = True

        for step_idx in range(MAX_STEPS):
            print(f"\n--- I{iteration_idx+1} : Step {step_idx} ---")

            # A. DECISION
            success = decision_agent.generate_next_step(state)
            if not success:
                print("🛑 Decision failed to generate step.")
                strategy_valid = False
                break 

            # PRINT STRATEGY TO CONSOLE
            current_plan = state.current_plan_text
            print(f"\n📝 CURRENT STRATEGY (I{iteration_idx+1}):")
            for line in current_plan:
                print(f"   {line}")
            
            last_step = state.get_last_step()
            if last_step["type"] == "FINAL_ANSWER":
                print("\n🎉 Decision marked task as COMPLETE.")
                return

            print(f"\n👉 Next Action: {last_step['description']}")

            # B. EXECUTOR
            await executor_agent.execute_pending_step(state)

            # C. CRITIC
            perception_agent.critique_last_step(state)

            if state.data["status"] == "COMPLETED":
                print(f"\n🎉 COORDINATOR: Final Answer Found!\n{state.data['final_answer']}")
                return

            last_step = state.get_last_step()
            if last_step["status"] == "failed":
                print("❌ Step Failed. Abandoning this Strategy.")
                strategy_valid = False
                break
            
            print("✅ Step Succeeded. Proceeding...")

        if not strategy_valid:
            print(f"⚠️ Iteration {iteration_idx + 1} failed. Re-planning...")
        else:
            print(f"⚠️ Max Steps ({MAX_STEPS}) reached. Re-planning...")

    print("\n🛑 Max Iterations reached.")

if __name__ == "__main__":
    q = input("Query: ")
    asyncio.run(coordinator_loop(q))