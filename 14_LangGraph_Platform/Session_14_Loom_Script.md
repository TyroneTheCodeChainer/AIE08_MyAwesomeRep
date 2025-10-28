# Session 14: LangGraph Platform - Loom Video Script

## Introduction (30 seconds)

Hello! In this video, I'll be demonstrating my Session 14 assignment on building and serving agentic graphs with LangGraph Platform. This assignment explores how to create, serve, and visualize AI agents using LangGraph's local development server and Studio interface.

## Assignment Overview (1 minute)

For this assignment, I:
1. Set up the environment with necessary API keys (OpenAI, Tavily)
2. Analyzed two different agent architectures: `simple_agent` and `agent_with_helpfulness`
3. Answered questions about graph architecture and interrupt patterns
4. Prepared to demonstrate both graphs using LangGraph Studio

The project includes:
- **Simple Agent**: A basic tool-using agent with conditional routing
- **Agent with Helpfulness**: An enhanced agent with quality control loops

## Question 1: Graph Architecture Comparison (2 minutes)

### Simple Agent Flow
The `simple_agent` follows a straightforward pattern:
- Agent calls the model with bound tools
- If tool calls are needed → routes to Action node → executes tools → back to Agent
- If no tool calls → terminates

### Agent with Helpfulness Flow
The `agent_with_helpfulness` adds a quality control layer:
- Agent calls the model with bound tools
- If tool calls needed → Action node → back to Agent
- If no tool calls → **Helpfulness evaluator node**

**Key Insight: The Helpfulness Evaluator**
- Sits **after** the agent produces a final response
- Uses a separate GPT-4.1-mini model to evaluate response quality
- Acts as a quality gate with three possible outcomes:
  1. "HELPFULNESS:Y" → End (response is good)
  2. "HELPFULNESS:N" → Continue back to agent (try again)
  3. Message count > 10 → End (safety limit to prevent infinite loops)

This creates a self-improvement loop where the agent can refine its responses based on quality assessment.

## Question 2: Before vs After Interrupts (1.5 minutes)

### Before Interrupts
Used when you need to **prevent or approve** an action before it happens:
- Human-in-the-loop approval (e.g., before expensive API calls)
- Input validation and modification
- Dynamic routing decisions
- Budget and safety checks

Think of it as: "**Should this happen?**"

### After Interrupts
Used when you need to **review or validate** results after they're produced:
- Output review and editing
- Quality assurance checks
- Debugging and state inspection
- Conditional continuation based on actual results
- Gathering additional context

Think of it as: "**How did this go?**"

**Key Distinction**: Before = prevention/approval of intent, After = review/validation of results

The `agent_with_helpfulness` demonstrates a programmatic "after" pattern - it automatically evaluates quality after the agent responds.

## Live Demonstration (3-4 minutes)

### Starting the LangGraph Server

```bash
cd 14_LangGraph_Platform
uv run langgraph dev
```

The server starts on `http://localhost:2024` and exposes our two assistants.

### Opening LangGraph Studio

Navigate to: `https://smith.langchain.com/studio?baseUrl=http://localhost:2024`

### Demo 1: Simple Agent
1. Select the "Simple Agent" assistant
2. Enter query: "What is the MuonClip optimizer, and what paper did it first appear in?"
3. Observe the flow:
   - Agent node calls the model
   - Model decides to use Arxiv or Tavily search tools
   - Action node executes the tool
   - Agent processes results
   - Final response returned

### Demo 2: Agent with Helpfulness
1. Select the "Agent with Helpfulness Check" assistant
2. Enter the same query
3. Observe the enhanced flow:
   - Agent node → tool calls → action node → agent response
   - **Helpfulness node evaluates the response**
   - Decision: Continue or End based on quality
4. Show how the helpfulness check can loop back if needed

### Activity #1: Debugging with Interrupts

1. Select `agent_with_helpfulness`
2. Set a **Before** interrupt on the "action" node
   - This pauses before tool execution
   - Can modify tool inputs or skip execution
3. Set an **After** interrupt on the "helpfulness" node
   - This pauses after quality evaluation
   - Can modify the decision or state
4. Run a query and demonstrate:
   - Pausing at the before interrupt
   - Inspecting/modifying state
   - Continuing execution
   - Pausing at the after interrupt
   - Reviewing the helpfulness decision

### Testing via SDK

```bash
uv run test_served_graph.py
```

This demonstrates calling the graph programmatically via the LangGraph SDK, showing how to:
- Create a sync client
- Stream responses from the graph
- Handle different event types

## Code Structure Review (1 minute)

Quick walkthrough of the project structure:
- `langgraph.json`: Defines graphs and assistants
- `app/graphs/simple_agent.py`: Basic tool-using agent
- `app/graphs/agent_with_helpfulness.py`: Enhanced agent with quality loop
- `app/state.py`: Shared agent state schema
- `app/models.py`: Model configuration
- `app/tools.py`: Tool belt (Tavily, Arxiv, RAG)
- `app/rag.py`: RAG implementation for document search

## Three Lessons Learned (1 minute)

1. **Graph Composition Patterns**: LangGraph's node-based architecture makes it easy to add quality control loops and conditional routing. The helpfulness evaluator pattern shows how to create self-improving agents without complex logic.

2. **Interrupts Enable Human-in-the-Loop**: Before and After interrupts provide powerful debugging and approval workflows. They're essential for production systems where you need human oversight or want to modify execution mid-stream.

3. **LangGraph Studio for Visualization**: Being able to see the graph execution in real-time with node-by-node streaming is invaluable for understanding agent behavior and debugging complex flows. The visual representation makes it much easier to reason about conditional logic.

## Three Lessons Not Yet Learned (1 minute)

1. **Production Deployment**: I haven't explored deploying LangGraph applications to production environments using LangGraph Cloud or other hosting solutions. Understanding scaling, monitoring, and production best practices would be valuable.

2. **Advanced State Management**: I haven't deeply explored complex state patterns like sub-graphs, parallel execution branches, or state checkpointing for long-running agents. These patterns would be important for more sophisticated applications.

3. **Custom Tool Development**: While I used pre-built tools (Tavily, Arxiv), I haven't created custom tools that integrate with external APIs, databases, or services. The optional MCP integration challenge would help develop this skill.

## Conclusion (30 seconds)

This assignment demonstrated the power of LangGraph for building and serving agentic applications. The platform's development server, Studio visualization, and SDK make it easy to iterate on agent architectures and add sophisticated control flows like quality evaluation loops.

The comparison between the simple agent and the helpfulness-enhanced agent shows how we can progressively add capabilities while maintaining clean, modular code structure.

Thank you for watching!

---

## Submission Checklist

- ✅ GitHub URL to README.md on s14-assignment branch
- ✅ Loom video URL
- ✅ Three lessons learned / not yet learned
- ⬜ Optional: Social media posts for extra credit
