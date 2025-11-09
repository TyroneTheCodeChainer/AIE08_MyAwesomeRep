# Session 18: On-Premises RAG Agent

## Overview

This folder contains the implementation of a fully on-premises RAG (Retrieval-Augmented Generation) agent that runs entirely on your local machine without any cloud APIs. The system uses:

- **Ollama** for LLM inference and embeddings
- **Qdrant** for vector storage (via Docker)
- **LangGraph** for agent orchestration
- **D&D Feats Dataset** for knowledge base

## Why On-Premises?

Running AI systems on-premises offers several advantages:

1. **Data Privacy**: Your data never leaves your infrastructure
2. **Cost Control**: No per-token API costs
3. **Offline Operation**: Works without internet connectivity
4. **Customization**: Full control over models and configuration
5. **Compliance**: Easier to meet regulatory requirements

## Architecture

```
User Query
    ↓
┌─────────────────────────┐
│   LangGraph Agent       │
│   (Ollama LLM)          │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│   RAG Tool              │
│   - Retrieve from       │
│     Qdrant              │
│   - Generate response   │
│     with Ollama         │
└─────────────────────────┘
    ↓
Agent Response
```

### Components

1. **LLM**: DeepSeek-R1 (8B) via Ollama
   - Fast inference on consumer hardware
   - Reasoning capabilities
   - Runs completely locally

2. **Embeddings**: mxbai-embed-large via Ollama
   - 1024-dimensional embeddings
   - Optimized for retrieval
   - Local execution

3. **Vector Database**: Qdrant
   - High-performance vector search
   - Runs in Docker
   - Supports gRPC for speed

4. **Agent Framework**: LangGraph
   - Tool-calling capabilities
   - Stateful conversation
   - Flexible routing logic

## Files

### Core Implementation

- **`onprem_rag_agent.py`** - Main agent implementation
  - `create_onprem_agent()`: Creates the LangGraph agent
  - `retrieve_dnd_information()`: RAG tool for D&D knowledge
  - `get_or_create_vectorstore()`: Manages Qdrant vector store
  - `chat_with_agent()`: Interface for chatting with agent

### Testing & Examples

- **`test_onprem_agent.ipynb`** - Interactive testing notebook
  - Step-by-step setup
  - RAG tool testing
  - Agent conversation examples
  - Execution trace inspection

- **`test_ollama.ipynb`** - Basic Ollama testing (from course materials)
- **`qdrant_setup.ipynb`** - Vector store setup example (from course materials)

### Data

- **`data/data/feats.json`** - D&D feats dataset (~5800 entries)

## Setup

### 1. Install Ollama

**macOS:**
```bash
# Download from https://ollama.com/download
# Or use Homebrew
brew install ollama
```

**Windows:**
```bash
# Download from https://ollama.com/download
# Run the installer
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Required Models

```bash
# LLM model (8B parameters, ~4.7GB)
ollama pull deepseek-r1:8b

# Embedding model (~1.5GB)
ollama pull mxbai-embed-large
```

Verify Ollama is running:
```bash
ollama list
```

### 3. Install Qdrant via Docker

```bash
# Pull and run Qdrant
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

Verify Qdrant is running:
```bash
curl http://localhost:6333
```

### 4. Install Python Dependencies

The required dependencies are listed in `pyproject.toml`:

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install jupyter langchain-qdrant langchain langchain-ollama ollama langchain-community numpy unstructured jq
```

### 5. Create Vector Store

**Option A: Using the notebook**
```bash
jupyter notebook qdrant_setup.ipynb
```
Run all cells (takes ~15 minutes)

**Option B: Using the agent code**
```python
from onprem_rag_agent import get_or_create_vectorstore

# This will automatically create the vector store on first run
vectorstore = get_or_create_vectorstore()
```

## Usage

### Command Line

```bash
python onprem_rag_agent.py
```

This will:
1. Check Qdrant connection
2. Connect to or create vector store
3. Create the agent
4. Run test queries

### Jupyter Notebook

```bash
jupyter notebook test_onprem_agent.ipynb
```

Follow the step-by-step instructions in the notebook.

### As a Module

```python
from onprem_rag_agent import create_onprem_agent, chat_with_agent

# Create agent
agent = create_onprem_agent()

# Chat
response = chat_with_agent(agent, "What feats improve strength?")
print(response)
```

### Agent with Tool Inspection

```python
from onprem_rag_agent import create_onprem_agent
from langchain_core.messages import HumanMessage

agent = create_onprem_agent()

# Get full execution details
result = agent.invoke({
    "messages": [HumanMessage(content="Tell me about magic feats")]
})

# Inspect all messages (including tool calls)
for message in result["messages"]:
    print(f"Type: {type(message).__name__}")
    print(f"Content: {message.content}")
    if hasattr(message, "tool_calls"):
        print(f"Tool Calls: {message.tool_calls}")
```

## Configuration

### Environment Variables

```python
import os

# Qdrant connection
os.environ["QDRANT_URL"] = "127.0.0.1:6334"
os.environ["QDRANT_COLLECTION"] = "DnD_Documents"
```

### Model Selection

```python
# Use a different Ollama model
agent = create_onprem_agent(
    model="llama3.1:8b",  # or any other Ollama model
    temperature=0.5
)
```

### Retrieval Settings

```python
from onprem_rag_agent import get_or_create_vectorstore

vectorstore = get_or_create_vectorstore()
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 10,  # Return more documents
        "score_threshold": 0.7  # Only high-quality matches
    }
)
```

## How It Works

### 1. User Query Arrives

```python
query = "What feats improve strength?"
```

### 2. Agent Decides to Use RAG Tool

The LangGraph agent analyzes the query and decides to call the `retrieve_dnd_information` tool.

### 3. RAG Tool Retrieves Context

```python
# Retrieves top 5 relevant documents from Qdrant
docs = retriever.invoke(query)
```

### 4. RAG Tool Generates Response

```python
# Uses local Ollama LLM to generate answer based on context
response = llm.invoke(prompt_with_context)
```

### 5. Agent Returns Result

The final response is sent back to the user.

## Performance

### Hardware Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 10GB free

**Recommended:**
- CPU: 8+ cores
- RAM: 16GB
- Disk: 20GB free
- GPU: Optional but helps significantly

### Speed Benchmarks

On a typical consumer laptop:

- **Query to response**: 5-15 seconds
- **Vector search**: <1 second
- **LLM generation**: 3-10 seconds
- **Initial indexing**: 10-15 minutes (one-time)

With GPU acceleration (e.g., NVIDIA RTX 3060):

- **LLM generation**: 1-3 seconds
- **Overall response**: 2-5 seconds

## Troubleshooting

### Ollama Issues

**Error: "Connection refused"**
```bash
# Make sure Ollama is running
ollama serve
```

**Error: "Model not found"**
```bash
# Pull the required models
ollama pull deepseek-r1:8b
ollama pull mxbai-embed-large
```

### Qdrant Issues

**Error: "Cannot connect to Qdrant"**
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart Qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**Error: "Collection not found"**
```python
# Recreate the vector store
from onprem_rag_agent import get_or_create_vectorstore

vectorstore = get_or_create_vectorstore(recreate=True)
```

### Memory Issues

**Error: "Out of memory"**

1. Use a smaller model:
   ```bash
   ollama pull deepseek-r1:1.5b
   ```

2. Reduce context window:
   ```python
   retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
   ```

### Slow Performance

1. **Enable GPU acceleration** (if available):
   - Ollama automatically uses GPU if available
   - Check with: `ollama ps`

2. **Reduce model size**:
   ```bash
   ollama pull llama3.2:3b  # Smaller, faster model
   ```

3. **Use Qdrant in-memory mode** (for testing):
   ```python
   from qdrant_client import QdrantClient
   client = QdrantClient(":memory:")
   ```

## Customization

### Use Your Own Data

Replace the D&D dataset with your own:

```python
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader

# Load PDFs instead of JSON
loader = DirectoryLoader(
    path="./my_data",
    glob="**/*.pdf",
    loader_cls=PyMuPDFLoader
)
documents = loader.load()

# Create vector store
vectorstore = QdrantVectorStore.from_documents(
    documents,
    embeddings,
    url="127.0.0.1:6334",
    collection_name="My_Collection"
)
```

### Modify the Agent Prompt

Edit the system prompt in `onprem_rag_agent.py`:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "Your custom system prompt here..."),
    ("human", "Context:\n{context}\n\nQuestion: {query}")
])
```

### Add More Tools

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(query: str) -> str:
    """Description of what this tool does."""
    # Your implementation
    return result

# Add to agent
tools = [retrieve_dnd_information, my_custom_tool]
```

## Comparison with Cloud-Based Systems

| Feature | On-Premises | Cloud (OpenAI/Anthropic) |
|---------|------------|--------------------------|
| Data Privacy | ✅ Complete control | ❌ Data sent to third party |
| Cost | 💰 Hardware + electricity | 💰💰 Per-token pricing |
| Latency | ⚡ Fast (local) | 🌐 Network dependent |
| Quality | 📊 Good (8B models) | 📊📊 Excellent (100B+ models) |
| Setup | 🔧 Complex | 🔧 Simple (API key) |
| Scalability | 💻 Hardware limited | ☁️ Unlimited |
| Offline | ✅ Works offline | ❌ Requires internet |
| Customization | ✅ Full control | ⚠️ Limited |

## Advanced: Production Deployment

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ./ollama_models:/root/.ollama
```

### Load Balancing

For high-traffic scenarios, run multiple Ollama instances:

```python
import random
from langchain_ollama import ChatOllama

ollama_urls = [
    "http://localhost:11434",
    "http://localhost:11435",
    "http://localhost:11436"
]

def get_llm():
    url = random.choice(ollama_urls)
    return ChatOllama(model="deepseek-r1:8b", base_url=url)
```

### Monitoring

```python
import time
from functools import wraps

def monitor_latency(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@monitor_latency
def chat_with_agent(agent, message):
    return agent.invoke({"messages": [HumanMessage(content=message)]})
```

## Next Steps

1. **Test the agent** with `test_onprem_agent.ipynb`
2. **Try different models** from Ollama's library
3. **Add your own data** to the vector store
4. **Customize the agent** with additional tools
5. **Deploy to production** using Docker Compose

## Resources

- [Ollama Models](https://ollama.com/library)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama/)

## Summary

This implementation demonstrates how to build a production-ready on-premises RAG agent that:

✅ Runs completely locally without cloud dependencies
✅ Provides data privacy and control
✅ Uses modern agent architecture with LangGraph
✅ Leverages efficient vector search with Qdrant
✅ Can be customized and extended
✅ Works offline

Perfect for organizations that need AI capabilities while maintaining data sovereignty and cost control!
