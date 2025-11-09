# Session 17: Agentic RAG Implementation

## Overview

This folder contains the implementation of an Agentic RAG (Retrieval-Augmented Generation) application using Together AI's open source endpoints. The implementation follows the architecture from Sessions 14 and 15 but replaces OpenAI models with Together AI alternatives.

## Files

### Core Implementation

- **`agentic_rag.py`** - Main RAG implementation using Together AI
  - Uses `ChatTogether` for language generation
  - Uses `TogetherEmbeddings` for document embeddings
  - Implements LangGraph for the retrieval and generation pipeline
  - Built on Qdrant for in-memory vector storage

### Testing & Examples

- **`test_agentic_rag.ipynb`** - Jupyter notebook for testing the RAG system
  - Interactive testing with multiple queries
  - Tool interface testing
  - Custom query support

- **`endpoint_slammer.ipynb`** - Endpoint testing (from course materials)
  - Tests Together AI endpoints with concurrent requests
  - Validates endpoint availability and performance

### Data

- **`data/howpeopleuseai.pdf`** - PDF document for RAG testing
- **`data/AIE8_Projects_with_Domains.csv`** - Projects data

## Architecture

The RAG system follows this flow:

1. **Document Loading**: PDFs are loaded from the `data` directory
2. **Text Splitting**: Documents are split into ~750 token chunks
3. **Embedding**: Chunks are embedded using Together AI's embedding model
4. **Vector Storage**: Embeddings stored in Qdrant (in-memory)
5. **Retrieval**: Top 5 relevant chunks retrieved for each query
6. **Generation**: Together AI LLM generates response based on context

## Dependencies

The application requires the following packages (see `pyproject.toml`):

```
jupyter>=1.1.1
openai>=1.100.2
together>=1.5.25
langchain-together>=0.3.0
langchain-community>=0.3.0
langchain-core>=0.3.0
langgraph>=0.3.0
qdrant-client>=1.15.0
pymupdf>=1.25.0
langchain-text-splitters>=0.3.0
tiktoken>=0.9.0
```

## Setup

### 1. Install Dependencies

Due to OneDrive file locking issues with `uv sync`, you may need to install manually:

```bash
# Option 1: Use the main repository venv
cd ..
uv pip install langchain-together langchain-community langchain-core langgraph qdrant-client pymupdf langchain-text-splitters tiktoken

# Option 2: Create a new venv outside of OneDrive
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install together langchain-together langchain-community langchain-core langgraph qdrant-client pymupdf langchain-text-splitters tiktoken
```

### 2. Set Environment Variables

```python
import os
import getpass

# Required: Together API key
os.environ["TOGETHER_API_KEY"] = getpass.getpass("Enter your Together API key: ")

# Optional: Use custom endpoint from endpoint_slammer.ipynb
os.environ["TOGETHER_MODEL_ENDPOINT"] = "your-username/openai/gpt-oss-20b-identifier"

# Or use default model
os.environ["TOGETHER_MODEL_ENDPOINT"] = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"

# Data directory
os.environ["RAG_DATA_DIR"] = "data"
```

### 3. Run the Application

**Option A: Python Script**
```bash
python agentic_rag.py
```

**Option B: Jupyter Notebook**
```bash
jupyter notebook test_agentic_rag.ipynb
```

**Option C: Import as Module**
```python
from agentic_rag import _get_rag_graph, retrieve_information

# Build RAG graph
graph = _get_rag_graph()

# Test query
result = graph.invoke({"question": "How are people using AI?"})
print(result["response"])
```

## Usage Examples

### Basic Query

```python
from agentic_rag import _get_rag_graph

graph = _get_rag_graph()
result = graph.invoke({"question": "What are the main AI applications?"})
print(result["response"])
```

### Using as a Tool

```python
from agentic_rag import retrieve_information

response = retrieve_information.invoke({
    "query": "What challenges do people face with AI?"
})
print(response)
```

## Model Options

### Chat Models (Together AI)
- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` (default)
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`
- Your custom endpoint from `endpoint_slammer.ipynb`

### Embedding Models
- `togethercomputer/m2-bert-80M-8k-retrieval` (default)
- `BAAI/bge-large-en-v1.5`
- `sentence-transformers/all-MiniLM-L6-v2`

## Customization

### Change Chunk Size

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Increase from 750
    chunk_overlap=200,  # Increase overlap
    length_function=_tiktoken_len
)
```

### Change Retrieval Parameters

```python
retriever = qdrant_vectorstore.as_retriever(
    search_kwargs={"k": 10}  # Retrieve more documents
)
```

### Change Generation Parameters

```python
generator_llm = ChatTogether(
    model=model_endpoint,
    temperature=0.5,  # More deterministic
    max_tokens=1024   # Longer responses
)
```

## Comparison with OpenAI Version

| Feature | OpenAI (Session 14/15) | Together AI (This Implementation) |
|---------|----------------------|-----------------------------------|
| Chat Model | `ChatOpenAI` | `ChatTogether` |
| Embedding | `OpenAIEmbeddings` | `TogetherEmbeddings` |
| Default Model | `gpt-4.1-nano` | `Meta-Llama-3.1-8B-Instruct-Turbo` |
| Cost | Pay per token | Free tier + paid options |
| Speed | Fast | Varies by model |
| Custom Endpoints | No | Yes (via Together AI) |

## Notes

- The RAG system uses in-memory Qdrant, so data is not persisted between runs
- Documents are loaded from the `data` directory on each run
- Token counting uses tiktoken's `gpt-4o` encoding
- Responses are constrained to only use information from the retrieved context

## Troubleshooting

### Import Errors
- Ensure all dependencies are installed
- Try installing in a fresh virtual environment outside OneDrive

### Empty Responses
- Check that PDF files exist in the `data` directory
- Verify Together API key is set correctly
- Ensure the model endpoint is valid

### Slow Performance
- Consider using a smaller embedding model
- Reduce chunk count by increasing chunk size
- Use a faster chat model

## Next Steps

1. Test with different queries in `test_agentic_rag.ipynb`
2. Experiment with different Together AI models
3. Compare performance with OpenAI version (Session 14/15)
4. Optional: Use RAGAS to evaluate the system (Advanced Build)
