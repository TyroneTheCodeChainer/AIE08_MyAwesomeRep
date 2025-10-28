<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading">Session 14: Build & Serve Agentic Graphs with LangGraph</h1>

| 🤓 Pre-work | 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|


# Build 🏗️

Run the repository and complete the following:

- 🤝 Breakout Room Part #1 — Building and serving your LangGraph Agent Graph
  - Task 1: Getting Dependencies & Environment
    - Configure `.env` (OpenAI, Tavily, optional LangSmith)
  - Task 2: Serve the Graph Locally
    - `uv run langgraph dev` (API on http://localhost:2024)
  - Task 3: Call the API from a different terminal
    - `uv run test_served_graph.py` (sync SDK example)
  - Task 4: Explore assistants (from `langgraph.json`)
    - `agent` → `simple_agent` (tool-using agent)
    - `agent_helpful` → `agent_with_helpfulness` (separate helpfulness node)

- 🤝 Breakout Room Part #2 — Using LangGraph Studio to visualize the graph
  - Task 1: Open Studio while the server is running
    - https://smith.langchain.com/studio?baseUrl=http://localhost:2024
  - Task 2: Visualize & Stream
    - Start a run and observe node-by-node updates
  - Task 3: Compare Flows
    - Contrast `agent` vs `agent_helpful` (tool calls vs helpfulness decision)

## Activities and Questions 🏗️ &❓

#### ❓ Question 1:

Compare the `agent` and `agent_helpful` assistants defined in `langgraph.json`. Where does the helpfulness evaluator fit in the graph, and under what condition should execution route back to the agent vs. terminate?

##### ✅ Answer:

**Comparison of the two assistants:**

The `agent` assistant (using `simple_agent` graph) follows a straightforward flow:
- **Agent Node** → calls the model with tool binding
- **Conditional routing**: If tool calls are present → **Action Node** (executes tools) → back to Agent
- If no tool calls → **END** (terminates)

The `agent_helpful` assistant (using `agent_with_helpfulness` graph) adds a quality control loop:
- **Agent Node** → calls the model with tool binding
- **Conditional routing**:
  - If tool calls present → **Action Node** → back to Agent
  - If no tool calls → **Helpfulness Node** (evaluates response quality)
- **Helpfulness Node**: Uses a separate GPT-4.1-mini model to evaluate if the agent's response is helpful relative to the initial query
- **Conditional routing from Helpfulness**:
  - If "HELPFULNESS:Y" (helpful) → **END**
  - If "HELPFULNESS:N" (not helpful) → **continue** back to Agent for another attempt
  - If loop limit exceeded (>10 messages) → **END** (safety mechanism)

**Where the helpfulness evaluator fits:**
The helpfulness evaluator sits **after the agent node** but only when the agent produces a final response (no tool calls). It acts as a quality gate between the agent's response and termination.

**Routing conditions:**
- **Route back to agent**: When helpfulness evaluation returns "N" (unhelpful response), giving the agent another chance to provide a better answer
- **Terminate**: When helpfulness evaluation returns "Y" (helpful response) OR when the safety limit of 10 messages is exceeded to prevent infinite loops

#### 🏗️ Activity #1 Debugging A Graph

Select the `agent_with_helpfulness` and set one or more interrupts (at least one `Before` and one `After`). Try changing values and continuing the turn. 

#### ❓ Question 2:

What are your thoughts on when you would use a Before interrupt vs. an After interrupt?

##### ✅ Answer:

**Before Interrupts** are ideal for:

1. **Human-in-the-loop approval**: When you need user approval before executing an action (e.g., before calling expensive APIs, before making database changes, or before executing potentially risky tool calls)
2. **Input validation**: Pausing to validate or modify inputs before they're processed by a node
3. **Dynamic routing decisions**: Allowing a human to override the graph's conditional logic and choose a different path
4. **Budget/safety checks**: Stopping execution before a node runs to verify constraints (cost limits, rate limits, safety boundaries)

**After Interrupts** are ideal for:

1. **Output review and editing**: Pausing after a node completes to review and potentially modify its output before continuing (e.g., editing an AI-generated response before sending it)
2. **Quality assurance**: Inspecting the results of an operation to ensure they meet quality standards before proceeding
3. **Debugging and inspection**: Examining the state after a node executes to understand what happened
4. **Conditional continuation**: Deciding whether to continue the workflow based on the actual results produced
5. **Gathering additional context**: After seeing results, a human might add supplementary information before the next step

**Key Distinction:**
- **Before** = "Should this happen?" (prevention, approval, modification of intent)
- **After** = "How did this go?" (review, validation, modification of results)

In practice, the `agent_with_helpfulness` graph demonstrates a programmatic version of an "after" concept - it evaluates the agent's output quality after completion and decides whether to continue or stop, though this is automated rather than requiring human intervention.



<details>
<summary>🚧 Advanced Build 🚧 (OPTIONAL - <i>open this section for the requirements</i>)</summary>

- Create and deploy a locally hosted MCP server with FastMCP.
- Extend your tools in `tools.py` to allow your LangGraph to consume the MCP Server.
</details>

# Ship 🚢

- Running local server (`langgraph dev`)
- Short demo showing both assistants responding

# Share 🚀
- Walk through your graph in Studio
- Share 3 lessons learned and 3 lessons not learned

# Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:
1. Create a branch of your `AIE8` repo to track your changes. Example command: `git checkout -b s14-assignment`
2. Complete the Tasks listed in the Breakout Room sections of `Build 🏗️`
3. Complete the activities and questions in `Activities and Questions 🏗️ &❓` by editing the file and replacing "_(enter answer here)_" with your responses
3. Commit, and push your completed notebook to your `origin` repository. _NOTE: Do not merge it into your main branch._
4. Record a Loom video reviewing the content of your completed notebook
5. Make sure to include all of the following on your Homework Submission Form:
    + The GitHub URL to the `README.md` file _on your assignment branch (not main)_
    + The URL to your Loom Video
    + Your Three Lessons Learned/Not Yet Learned
    + The URLs to any social media posts (LinkedIn, X, Discord, etc.) ⬅️ _easy Extra Credit points!_


### OPTIONAL: 🚧 Advanced Build Assignment 🚧
<details>
  <summary>(<i>Open this section for the submission instructions.</i>)</summary>

Follow these steps to prepare and submit your homework assignment:
1. Create a branch of your `AIE8` repo to track your changes. Example command: `git checkout -b s14-assignment`
2. Create your MCP server
3. Add it to the existing graph's tools
4. Deploy it ***locally***
5. Validate the graph uses the MCP server's tools
6. Commit, and push your changes to your `origin` repository. _NOTE: Do not merge it into your main branch._
7. Record a Loom video reviewing the content of your completed notebook.
8. Make sure to include all of the following on your Homework Submission Form:
    + The GitHub URL to the notebook you created for the Advanced Build Assignment _on your assignment branch_
    + The URL to your Loom Video
    + Your Three Lessons Learned/Not Yet Learned
    + The URLs to any social media posts (LinkedIn, X, Discord, etc.) ⬅️ _easy Extra Credit points!_

</details>
