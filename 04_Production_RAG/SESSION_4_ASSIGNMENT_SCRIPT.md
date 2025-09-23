# Session 4: Production RAG with LangGraph and LangChain - Assignment Script & Answers

## 🎯 **Assignment Overview**
This document contains the complete script and answers for Session 4 assignment, demonstrating the implementation of production-grade RAG systems using LangChain, LangGraph, and local LLMs with Ollama.

---

## 📋 **Ollama Setup and Testing**

### **✅ Ollama Installation and Configuration:**

#### **1. Ollama Installation:**
```bash
# Install Ollama (Windows)
# Download from https://ollama.ai/download
# Run the installer and follow the setup wizard

# Verify installation
ollama --version
```

#### **2. Model Downloads:**
```bash
# Pull required models for the assignment
ollama pull llama2:7b
ollama pull mistral:7b
ollama pull codellama:7b
ollama pull neural-chat:7b

# Verify models are available
ollama list
```

#### **3. Ollama Service Management:**
```bash
# Start Ollama service
ollama serve

# Test model inference
ollama run llama2:7b "Hello, how are you?"

# Test embedding generation
ollama run nomic-embed-text "This is a test embedding"
```

---

## 🏗️ **LangChain and LCEL Implementation**

### **✅ Core LangChain Components:**

#### **1. LangChain Expression Language (LCEL) Setup:**
```python
# Session 4: LangChain and LCEL Implementation
from langchain.llms import Ollama
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import qdrant_client

# Initialize Ollama LLM
llm = Ollama(
    model="llama2:7b",
    base_url="http://localhost:11434"
)

# Initialize Ollama Embeddings
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

# Initialize Qdrant Vector Store
client = qdrant_client.QdrantClient(host="localhost", port=6333)
vectorstore = Qdrant(
    client=client,
    collection_name="dream_research",
    embeddings=embeddings
)
```

#### **2. Document Processing Pipeline:**
```python
# Document loading and preprocessing
def load_and_process_documents(file_path: str):
    """Load and process documents for RAG system"""
    
    # Load document
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create document object
    document = Document(
        page_content=content,
        metadata={"source": file_path, "type": "dream_research"}
    )
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents([document])
    
    # Add to vector store
    vectorstore.add_documents(chunks)
    
    return len(chunks)

# Process dream research documents
chunk_count = load_and_process_documents("data/dream_research_papers.txt")
print(f"Processed {chunk_count} document chunks")
```

#### **3. RAG Chain Implementation:**
```python
# Create RAG chain using LCEL
def create_rag_chain(vectorstore, llm):
    """Create a RAG chain using LangChain Expression Language"""
    
    # Create retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    # Define the RAG chain using LCEL
    rag_chain = (
        {"context": retriever, "question": lambda x: x["question"]}
        | prompt_template
        | llm
        | output_parser
    )
    
    return rag_chain

# Prompt template for dream research
from langchain.prompts import PromptTemplate

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    You are a specialized dream interpretation assistant with expertise in sleep science, psychology, and neuroscience.
    
    Context: {context}
    
    Question: {question}
    
    Please provide a scientifically grounded analysis based on the provided context. Focus on:
    1. REM sleep research findings
    2. Psychological theories of dreaming
    3. Neurological processes during sleep
    4. Evidence-based interpretations
    
    Answer:
    """
)

# Output parser
from langchain.schema.output_parser import StrOutputParser
output_parser = StrOutputParser()

# Create the RAG chain
rag_chain = create_rag_chain(vectorstore, llm)
```

---

## 🔄 **LangGraph Implementation**

### **✅ Graph-Based RAG System:**

#### **1. State Definition:**
```python
# LangGraph State Definition
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

class RAGState(TypedDict):
    """State for the RAG graph"""
    question: str
    context: List[str]
    answer: str
    confidence: float
    sources: List[str]
    error: Optional[str]

# Initialize the graph
workflow = StateGraph(RAGState)
```

#### **2. Node Functions:**
```python
# Define graph nodes
def retrieve_documents(state: RAGState) -> RAGState:
    """Retrieve relevant documents"""
    try:
        question = state["question"]
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.get_relevant_documents(question)
        
        context = [doc.page_content for doc in docs]
        sources = [doc.metadata.get("source", "unknown") for doc in docs]
        
        return {
            **state,
            "context": context,
            "sources": sources
        }
    except Exception as e:
        return {**state, "error": f"Retrieval error: {str(e)}"}

def generate_answer(state: RAGState) -> RAGState:
    """Generate answer using retrieved context"""
    try:
        if state.get("error"):
            return state
            
        context = "\n\n".join(state["context"])
        question = state["question"]
        
        # Create prompt with context
        prompt = f"""
        Context: {context}
        
        Question: {question}
        
        Based on the provided context, provide a comprehensive answer about dream research and sleep science.
        """
        
        # Generate answer
        response = llm.invoke(prompt)
        
        # Calculate confidence (simplified)
        confidence = min(len(state["context"]) / 3, 1.0)
        
        return {
            **state,
            "answer": response,
            "confidence": confidence
        }
    except Exception as e:
        return {**state, "error": f"Generation error: {str(e)}"}

def validate_answer(state: RAGState) -> RAGState:
    """Validate and refine the answer"""
    try:
        if state.get("error"):
            return state
            
        answer = state["answer"]
        confidence = state["confidence"]
        
        # Simple validation rules
        if len(answer) < 50:
            return {**state, "error": "Answer too short"}
        
        if confidence < 0.3:
            return {**state, "error": "Low confidence answer"}
            
        return state
    except Exception as e:
        return {**state, "error": f"Validation error: {str(e)}"}

# Add nodes to the graph
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)
workflow.add_node("validate", validate_answer)
```

#### **3. Graph Construction:**
```python
# Define the graph flow
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "validate")

# Add conditional edge for validation
def should_continue(state: RAGState):
    """Determine if we should continue or end"""
    if state.get("error"):
        return "end"
    return "end"

workflow.add_conditional_edges(
    "validate",
    should_continue,
    {
        "end": END
    }
)

# Compile the graph
app = workflow.compile()
```

---

## 🚀 **Production Deployment Configuration**

### **✅ Production-Ready Setup:**

#### **1. Environment Configuration:**
```python
# Production environment setup
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
PRODUCTION_CONFIG = {
    "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "qdrant_host": os.getenv("QDRANT_HOST", "localhost"),
    "qdrant_port": int(os.getenv("QDRANT_PORT", "6333")),
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
    "timeout": int(os.getenv("TIMEOUT", "30")),
    "log_level": os.getenv("LOG_LEVEL", "INFO")
}
```

#### **2. Error Handling and Monitoring:**
```python
# Production error handling
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionRAG:
    """Production-ready RAG system with monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = Ollama(
            model="llama2:7b",
            base_url=config["ollama_base_url"]
        )
        self.vectorstore = self._init_vectorstore()
        self.app = self._build_graph()
    
    def _init_vectorstore(self):
        """Initialize vector store with error handling"""
        try:
            client = qdrant_client.QdrantClient(
                host=self.config["qdrant_host"],
                port=self.config["qdrant_port"]
            )
            return Qdrant(
                client=client,
                collection_name="dream_research",
                embeddings=OllamaEmbeddings(
                    model="nomic-embed-text",
                    base_url=self.config["ollama_base_url"]
                )
            )
        except Exception as e:
            logger.error(f"Vector store initialization failed: {e}")
            raise
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(RAGState)
        workflow.add_node("retrieve", retrieve_documents)
        workflow.add_node("generate", generate_answer)
        workflow.add_node("validate", validate_answer)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "validate")
        workflow.add_conditional_edges("validate", should_continue, {"end": END})
        
        return workflow.compile()
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system with monitoring"""
        try:
            logger.info(f"Processing query: {question[:100]}...")
            
            result = self.app.invoke({"question": question})
            
            logger.info(f"Query processed successfully. Confidence: {result.get('confidence', 0)}")
            return result
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "question": question,
                "answer": "I apologize, but I encountered an error processing your question.",
                "error": str(e),
                "confidence": 0.0
            }
```

#### **3. Performance Monitoring:**
```python
# Performance monitoring
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper

# Apply monitoring to key functions
@monitor_performance
def process_document_batch(documents: List[str]) -> int:
    """Process a batch of documents with monitoring"""
    total_chunks = 0
    for doc in documents:
        chunks = load_and_process_documents(doc)
        total_chunks += chunks
    return total_chunks
```

---

## 📊 **Assignment Questions and Answers**

### **Question 1: What is the embedding dimension for the nomic-embed-text model?**

**Answer:** The embedding dimension for the nomic-embed-text model is **768**.

```python
# Verification code
from langchain.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

# Test embedding to get dimension
test_embedding = embeddings.embed_query("test")
embedding_dim = len(test_embedding)  # This will be 768
print(f"Embedding dimension: {embedding_dim}")
```

### **Question 2: Explain the key differences between traditional RAG and LangGraph-based RAG systems.**

**Answer:**

#### **Traditional RAG:**
- **Linear Pipeline**: Retrieve → Generate → Output
- **Single Path**: Fixed sequence of operations
- **Limited Control Flow**: No conditional logic or branching
- **Simple State Management**: Basic input/output handling

#### **LangGraph-based RAG:**
- **Graph-Based Architecture**: Multiple nodes with conditional edges
- **Dynamic Control Flow**: Can branch based on conditions
- **State Management**: Persistent state across nodes
- **Error Handling**: Built-in error recovery and validation
- **Monitoring**: Better observability and debugging

**Key Advantages of LangGraph:**
1. **Flexibility**: Can handle complex workflows with multiple decision points
2. **Robustness**: Built-in error handling and recovery mechanisms
3. **Scalability**: Easy to add new nodes and modify workflows
4. **Monitoring**: Better tracking of system performance and issues

### **Question 3: How does Qdrant compare to other vector databases for production RAG systems?**

**Answer:**

#### **Qdrant Advantages:**
- **Performance**: Optimized for high-speed vector search
- **Scalability**: Horizontal scaling capabilities
- **Memory Efficiency**: Efficient memory usage for large datasets
- **Filtering**: Advanced filtering capabilities beyond vector similarity
- **API**: RESTful API with multiple language clients

#### **Comparison with Other Vector DBs:**

| Feature | Qdrant | Pinecone | Weaviate | Chroma |
|---------|--------|----------|----------|--------|
| **Open Source** | ✅ | ❌ | ✅ | ✅ |
| **Self-Hosted** | ✅ | ❌ | ✅ | ✅ |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Filtering** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Ease of Use** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

**Production Considerations:**
- **Cost**: Qdrant is cost-effective for self-hosted solutions
- **Control**: Full control over data and infrastructure
- **Customization**: Easy to customize for specific use cases
- **Community**: Strong open-source community support

---

## 🎥 **Loom Video Script (5 Minutes)**

### **Introduction (30 seconds):**
"Hi everyone! I'm Tyrone, and today I'm walking through my Session 4 assignment where I built a production-grade RAG system using LangChain, LangGraph, and local LLMs with Ollama. This demonstrates how to create scalable, robust RAG systems for production environments."

### **Ollama Setup (1 minute):**
"First, I'll show you how I set up Ollama for local LLM inference. I installed Ollama, pulled the required models like Llama2 and Mistral, and configured the embedding model nomic-embed-text for vector operations."

### **LangChain Implementation (1.5 minutes):**
"Next, I'll demonstrate the LangChain implementation using LCEL (LangChain Expression Language). I'll show how I created the document processing pipeline, vector store integration with Qdrant, and the RAG chain using the pipe operator syntax."

### **LangGraph Workflow (1.5 minutes):**
"Then I'll walk through the LangGraph implementation, showing the state management, node functions for retrieval and generation, and the conditional edges that make the system more robust and production-ready."

### **Production Features (1 minute):**
"Finally, I'll highlight the production features I implemented: error handling, monitoring, performance tracking, and the configuration management that makes this system ready for deployment."

### **Conclusion (30 seconds):**
"This project demonstrates the evolution from simple RAG to production-grade systems, showing how LangGraph and local LLMs can create powerful, scalable solutions for real-world applications."

---

## 📱 **Social Media Post Template**

```
🚀 Exciting News! 🎉

I just completed Session 4 of the AI Engineer Challenge and built a production-grade RAG system using LangChain, LangGraph, and local LLMs! 🤖⚡

🔍 Three Key Takeaways:
1️⃣ LangGraph's graph-based architecture provides incredible flexibility and robustness for complex RAG workflows. 🧠✨
2️⃣ Local LLMs with Ollama offer a perfect balance of performance, privacy, and cost-effectiveness for production systems. 🌱📈
3️⃣ Production RAG systems require careful attention to error handling, monitoring, and scalability - not just the core functionality. 🔄📚

A huge shoutout to @AIMakerspace for the incredible curriculum and resources! 🙌

The system is running locally with Ollama and Qdrant for maximum control and performance.

#LangChain #LangGraph #Ollama #RAG #ProductionAI #AIMakerspace
```

---

## 📝 **Lessons Learned & Not Learned**

### **✅ Three Lessons Learned:**
1. **Graph-Based Architecture**: LangGraph's state management and conditional edges provide much more robust RAG systems than traditional linear pipelines.
2. **Local LLM Benefits**: Ollama makes it easy to run powerful LLMs locally, providing better privacy, cost control, and customization options.
3. **Production Considerations**: Building production RAG systems requires much more than just retrieval and generation - monitoring, error handling, and scalability are crucial.

### **❌ Three Lessons Not Learned:**
1. **Advanced Vector DB Features**: Haven't explored Qdrant's advanced filtering, hybrid search, or distributed deployment capabilities.
2. **Model Fine-tuning**: Haven't implemented fine-tuning of local models for domain-specific RAG applications.
3. **Multi-Modal RAG**: Haven't explored RAG systems that can handle images, audio, or other media types beyond text.

---

## 🎯 **Assignment Completion Status**

- ✅ **Ollama Setup**: Successfully installed and configured Ollama with required models
- ✅ **LangChain Implementation**: Built RAG system using LCEL and Ollama
- ✅ **LangGraph Workflow**: Created graph-based RAG with state management
- ✅ **Qdrant Integration**: Set up vector database for document storage and retrieval
- ✅ **Production Features**: Implemented error handling, monitoring, and configuration
- ✅ **Documentation**: Comprehensive implementation documentation and code comments

**Repository URL**: https://github.com/TyroneTheCodeChainer/AIE08_MyAwesomeRep
**Assignment Branch**: `s04-assignment`
**Local Setup**: Ollama + Qdrant + LangChain + LangGraph
