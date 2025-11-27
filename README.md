The idea is to follow the architecture described in this image
![alt text](image-1.png)


This is how the simluation of logs look:
![alt text](image.png)

and by going through the approach mentioned in this document:
https://canvas.instructure.com/courses/12633376/pages/session-10-multi-agent-systems-and-distributed-ai-coordination-mini-capstone?module_item_id=143480089

The flow is user_query -> perception (does as per the prompt) -> decision (decides steps and writes code) -> executor (executes code) -> perception (now a new prompt and a critic role to be given but the output will be in the same structure) -> decision and so on until it achieves the final goal.




The architecture is going to have a few things:
- Strategy:
    - Conservative
    - Exploratory

- Model manager: Supply the right tools (for example, when text generation is picked, use gemini. For text embeddings, we need to use nomic)

- RAG integration -- Basically memory
    - It needs to have FAISS included
    - Chunking startegy should be included
    - Retrieval should use some strategy

- What's great about this architecture is that the architecture is going to be STATEFUL but the LLM is going to be STATELESS. That is, we always make only one call to the LLM to get the desired output. But preserve the context in such as way that we carry the context forward

- It would mainly have 4 components:
    - Perception - The goal of this is to understand the user intent and identify the following components (ERORLL):
        - Entities
        - Result Required
        - Original Goal Achieved
        - Reasoning
        - Local Goal Achieved
        - Local Reasoning
    - Decision - Decision will have to essentially come up with the plan to execute the tool calls. This would include:
        - Select the right server
        - Select the right tool
        - Make a plan
        - Then using Python Sandbox - execute the plan
        - What if it doesn't need python sandbox to execute?
    - Memory - Essentially this will carry all the info to remember and make the architecture statful
    - Action/ execution - This will ensure the tools are executed
    - Orchestrator - In this case agent_loop is going to act as the orchestrator as it will manage the context, store results etc etc...



Let's look at a query and how it should be processed as per the architecrtue:

# Let's play a simulation now:
Query goes as follows: 
'summarize Maulin Shah's comments on Tesla. Find the information locally first'

What did Maulin Shah's say about Tesla?

Step 1: Search the recent conversations to find if this question or a variant of the same question has been asked.

Step 2: Run perception extract the output
a. Now perception is running in the intent detection mode
[perception] for initial query understanding

Entities: [Maulin Shah, Tesla]
Result required: The comment made by Maulin Shan on Tesla
Original goal achieved : False
Reasoning: The query requires searching information in various documents and on the internet.
Local Goal Achieved: False 
Local Reasoning: The query is understood but requires extenal information to proceed
Last tooluse Summary: Not ready yet
solution_summary: Not ready yet

Step 3: Now this is sent to decision :





