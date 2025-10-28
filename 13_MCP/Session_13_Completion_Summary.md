# Session 13: MCP - Homework Completion Summary

## Assignment Overview

This assignment focused on building custom tools for an MCP (Model Context Protocol) server that can be used by AI assistants like Cursor.

## What Was Completed

### 1. Repository Setup
- Cloned the AIE8-MCP-Session repository from https://github.com/AI-Maker-Space/AIE8-MCP-Session
- Installed all dependencies using uv package manager
- Set up the development environment

### 2. Custom Tools Implementation

I implemented two custom MCP tools in `server.py`:

#### Tool #1: Dad Joke Generator (`get_dad_joke`)
- **Purpose**: Fetches dad jokes from the icanhazdadjoke.com API
- **Features**:
  - Random joke generation
  - Search functionality for topic-specific jokes
  - Proper error handling
  - No authentication required
- **API**: https://icanhazdadjoke.com
- **Parameters**: 
  - `search_term` (optional): Keyword to search for jokes about a specific topic

#### Tool #2: Programming Quote Generator (`get_programming_quote`)
- **Purpose**: Retrieves programming and technology-related quotes
- **Features**:
  - Random quote from quotable.io API
  - Fallback mechanism with curated quotes
  - No parameters required
- **API**: https://api.quotable.io
- **Parameters**: None

### 3. Testing
- Created comprehensive test script (`test_custom_tools.py`)
- Verified all tools work correctly
- Tested error handling and fallback mechanisms

### 4. Documentation
- Created detailed Loom video script (`LOOM_VIDEO_SCRIPT.md`)
- Documented setup instructions
- Included lessons learned and not yet learned

## Code Location

The implementation can be found at:
```
C:/Users/tfel4/AIE8-MCP-Session/server.py
```

## Key Files Modified/Created

1. **server.py** - Added custom tools to the MCP server
2. **test_custom_tools.py** - Test script for validating tools
3. **LOOM_VIDEO_SCRIPT.md** - Video walkthrough documentation
4. **.env** - Environment configuration (created from .env.sample)

## How to Use

### Setup
1. Navigate to the repository:
   ```bash
   cd C:/Users/tfel4/AIE8-MCP-Session
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Configure Cursor MCP settings (CMD/CTRL+SHIFT+P -> "View: Open MCP Settings"):
   ```json
   {
       "mcpServers": {
           "mcp-server": {
               "command": "uv",
               "args": ["--directory", "C:/Users/tfel4/AIE8-MCP-Session", "run", "server.py"]
           }
       }
   }
   ```

### Using the Tools

Once configured, you can use the tools through Cursor:

- "Get me a random dad joke"
- "Find a dad joke about programming"
- "Give me a programming quote for inspiration"

## Three Lessons Learned

1. **MCP Integration is Powerful**: The Model Context Protocol provides a clean, standardized way to extend AI assistants with custom tools. The FastMCP library makes it incredibly easy to add new capabilities.

2. **Error Handling is Critical**: When integrating with external APIs, robust error handling and fallback mechanisms are essential. The programming quote tool demonstrates this by including hardcoded fallback quotes when the API is unavailable.

3. **Testing External Dependencies**: Testing tools that rely on external APIs requires careful consideration. Even if an API is temporarily unavailable, the tool should gracefully handle errors and provide useful feedback to the user.

## Three Lessons Not Yet Learned

1. **Advanced MCP Features**: I haven't explored more advanced MCP capabilities like streaming responses, complex parameter types, or state management across multiple tool calls. These features could enable more sophisticated interactions.

2. **Production Deployment**: I haven't learned how to deploy MCP servers in a production environment with proper monitoring, logging, and rate limiting for API calls. Understanding scalability and reliability in production is crucial.

3. **MCP Security Best Practices**: I need to learn more about securing MCP servers, handling authentication tokens safely, and implementing proper access controls when exposing tools to AI assistants. Security considerations become critical when dealing with sensitive data or operations.

## Technical Highlights

- **API Integration**: Successfully integrated with two different REST APIs
- **Error Handling**: Implemented comprehensive error handling with try-except blocks
- **Fallback Mechanisms**: Added fallback data for when external APIs are unavailable
- **Type Hints**: Used proper Python type hints for better code clarity
- **Documentation**: Added detailed docstrings for each tool function

## Next Steps for Activity #2

The assignment also includes an optional Activity #2 to build a LangGraph application that interacts with the MCP server. This could be explored using the langchain-mcp-adapters package.

## Conclusion

This assignment demonstrated the power and flexibility of the Model Context Protocol for extending AI assistants. By building custom tools that integrate with external APIs, we can significantly enhance the capabilities of AI assistants while maintaining a clean, standardized interface.

The tools are production-ready and can be used immediately through any MCP-compatible client like Cursor!
