"""
Session 04: Production RAG System with LangChain
Built progressively on previous sessions:

Course progression:
- Session 1: Prototyping and vibe check ✓
- Session 2: Python RAG with embeddings ✓
- Session 3: Flask web application ✓
- Session 4: Production system with LangChain, ChromaDB, and FastAPI
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# LangChain imports (Session 4 focus)
try:
    from langchain.document_loaders import TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.chains import RetrievalQA
    from langchain.llms import OpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("⚠️ LangChain not available - using fallback implementation")
    LANGCHAIN_AVAILABLE = False

# Fallback imports (if LangChain not available)
import openai
from openai import OpenAI as OpenAIClient
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import tempfile
import PyPDF2
import io

# Initialize FastAPI
app = FastAPI(
    title="Session 04: Production RAG System",
    description="LangChain-powered RAG system building on Sessions 1-3",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class DocumentUpload(BaseModel):
    text: str
    source: str = "upload"

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    success: bool = True

# Global variables
rag_system = None
openai_client = None

def get_openai_client():
    """Get OpenAI client with API key validation"""
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        openai_client = OpenAIClient(api_key=api_key)
    return openai_client

class ProductionRAGSystem:
    """Production RAG system using LangChain when available, fallback otherwise"""

    def __init__(self):
        self.use_langchain = LANGCHAIN_AVAILABLE
        self.documents = []
        self.vectorstore = None
        self.qa_chain = None

        if self.use_langchain:
            self._init_langchain()
        else:
            self._init_fallback()

    def _init_langchain(self):
        """Initialize LangChain components"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY required")

            # Initialize embeddings and LLM
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            self.llm = OpenAI(temperature=0.1, openai_api_key=api_key)

            # Initialize Chroma vector store
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )

            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )

            print("✅ LangChain RAG system initialized")

        except Exception as e:
            print(f"❌ LangChain initialization failed: {e}")
            self.use_langchain = False
            self._init_fallback()

    def _init_fallback(self):
        """Initialize fallback RAG system (Session 2/3 style)"""
        self.embedding_model = "text-embedding-ada-002"
        self.document_store = {
            "documents": [],
            "embeddings": [],
            "metadata": []
        }
        print("✅ Fallback RAG system initialized")

    def add_document(self, text: str, source: str = "upload") -> bool:
        """Add document to the system"""
        try:
            if self.use_langchain:
                return self._add_document_langchain(text, source)
            else:
                return self._add_document_fallback(text, source)
        except Exception as e:
            print(f"Error adding document: {e}")
            return False

    def _add_document_langchain(self, text: str, source: str) -> bool:
        """Add document using LangChain"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

        chunks = text_splitter.split_text(text)

        # Add to vector store
        metadatas = [{"source": source, "chunk": i} for i in range(len(chunks))]
        self.vectorstore.add_texts(chunks, metadatas=metadatas)

        return True

    def _add_document_fallback(self, text: str, source: str) -> bool:
        """Add document using fallback system"""
        client = get_openai_client()

        # Simple chunking
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 800:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Generate embeddings
        for i, chunk in enumerate(chunks):
            try:
                response = client.embeddings.create(
                    input=chunk,
                    model=self.embedding_model
                )
                embedding = response.data[0].embedding

                self.document_store["documents"].append(chunk)
                self.document_store["embeddings"].append(embedding)
                self.document_store["metadata"].append({
                    "source": source,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })
            except Exception as e:
                print(f"Error generating embedding: {e}")
                continue

        return len(chunks) > 0

    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """Query the RAG system"""
        try:
            if self.use_langchain:
                return self._query_langchain(question, top_k)
            else:
                return self._query_fallback(question, top_k)
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "success": False
            }

    def _query_langchain(self, question: str, top_k: int) -> Dict[str, Any]:
        """Query using LangChain"""
        if not self.qa_chain:
            return {
                "answer": "RAG system not properly initialized",
                "sources": [],
                "success": False
            }

        result = self.qa_chain({"query": question})

        # Format sources
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"][:top_k]:
                sources.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity": 0.8  # LangChain doesn't return similarity scores
                })

        return {
            "answer": result["result"],
            "sources": sources,
            "success": True
        }

    def _query_fallback(self, question: str, top_k: int) -> Dict[str, Any]:
        """Query using fallback system"""
        if not self.document_store["documents"]:
            return {
                "answer": "No documents available. Please upload some documents first.",
                "sources": [],
                "success": True
            }

        client = get_openai_client()

        # Get query embedding
        response = client.embeddings.create(
            input=question,
            model=self.embedding_model
        )
        query_embedding = response.data[0].embedding

        # Calculate similarities
        similarities = cosine_similarity(
            [query_embedding],
            self.document_store["embeddings"]
        )[0]

        # Get top results
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        relevant_docs = []
        context_parts = []

        for idx in top_indices:
            if similarities[idx] > 0.6:  # Relevance threshold
                doc_content = self.document_store["documents"][idx]
                relevant_docs.append({
                    "content": doc_content,
                    "similarity": float(similarities[idx]),
                    "metadata": self.document_store["metadata"][idx]
                })
                context_parts.append(doc_content)

        if not context_parts:
            return {
                "answer": "I couldn't find relevant information to answer your question.",
                "sources": [],
                "success": True
            }

        # Generate answer
        context = "\n\n".join(context_parts)
        prompt = f"""Based on the following context, answer the question clearly and concisely.

Context:
{context}

Question: {question}

Answer:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1
        )

        answer = response.choices[0].message.content.strip()

        return {
            "answer": answer,
            "sources": relevant_docs,
            "success": True
        }

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        if self.use_langchain:
            doc_count = self.vectorstore._collection.count() if hasattr(self.vectorstore, '_collection') else 0
            return {
                "system": "LangChain + ChromaDB",
                "document_count": doc_count,
                "status": "ready"
            }
        else:
            return {
                "system": "Fallback (Session 2/3 style)",
                "document_count": len(self.document_store["documents"]),
                "status": "ready"
            }

# Initialize RAG system on startup
@app.on_event("startup")
async def startup_event():
    global rag_system
    rag_system = ProductionRAGSystem()

# Routes
@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Session 04: Production RAG</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .section { margin: 25px 0; padding: 20px; border: 2px solid #e9ecef; border-radius: 10px; background: #f8f9fa; }
            .section h3 { color: #495057; margin-top: 0; }
            textarea { width: 100%; height: 120px; margin: 10px 0; padding: 10px; border: 1px solid #ced4da; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
            button:hover { background: #0056b3; }
            .result { background: #d4edda; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745; border-radius: 5px; }
            .error { background: #f8d7da; border-left-color: #dc3545; }
            .info { background: #d1ecf1; border-left-color: #17a2b8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Session 04: Production RAG System</h1>
                <p>LangChain + ChromaDB + FastAPI | Building on Sessions 1-3</p>
            </div>

            <div class="section">
                <h3>📄 Upload Document</h3>
                <textarea id="documentText" placeholder="Paste your document text here..."></textarea>
                <button onclick="uploadDocument()">Upload Document</button>
                <div id="uploadResult"></div>
            </div>

            <div class="section">
                <h3>❓ Ask Question</h3>
                <textarea id="questionText" placeholder="Ask a question about your documents..."></textarea>
                <button onclick="askQuestion()">Ask Question</button>
                <div id="questionResult"></div>
            </div>

            <div class="section">
                <h3>📊 System Status</h3>
                <button onclick="getStatus()">Check Status</button>
                <div id="statusResult"></div>
            </div>
        </div>

        <script>
            async function uploadDocument() {
                const text = document.getElementById('documentText').value;
                if (!text.trim()) {
                    showResult('uploadResult', 'Please enter document text.', 'error');
                    return;
                }

                try {
                    const response = await fetch('/upload-document', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: text, source: 'web_upload'})
                    });
                    const result = await response.json();

                    if (result.success) {
                        showResult('uploadResult', '✅ Document uploaded successfully!', 'success');
                        document.getElementById('documentText').value = '';
                    } else {
                        showResult('uploadResult', '❌ ' + (result.error || 'Upload failed'), 'error');
                    }
                } catch (error) {
                    showResult('uploadResult', '❌ Error: ' + error.message, 'error');
                }
            }

            async function askQuestion() {
                const question = document.getElementById('questionText').value;
                if (!question.trim()) {
                    showResult('questionResult', 'Please enter a question.', 'error');
                    return;
                }

                showResult('questionResult', '🤔 Processing...', 'info');

                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({question: question, top_k: 3})
                    });
                    const result = await response.json();

                    if (result.success) {
                        let html = `<strong>Answer:</strong><br>${result.answer}<br><br>`;
                        if (result.sources.length > 0) {
                            html += '<strong>Sources:</strong><br>';
                            result.sources.forEach((source, i) => {
                                const similarity = source.similarity ? (source.similarity * 100).toFixed(1) + '%' : 'N/A';
                                html += `<small>${i+1}. Similarity: ${similarity}<br>${source.content.substring(0, 150)}...</small><br><br>`;
                            });
                        }
                        showResult('questionResult', html, 'success');
                    } else {
                        showResult('questionResult', '❌ ' + (result.error || 'Query failed'), 'error');
                    }
                } catch (error) {
                    showResult('questionResult', '❌ Error: ' + error.message, 'error');
                }
            }

            async function getStatus() {
                try {
                    const response = await fetch('/status');
                    const result = await response.json();

                    let html = `
                        <strong>System:</strong> ${result.system}<br>
                        <strong>Documents:</strong> ${result.document_count}<br>
                        <strong>Status:</strong> ${result.status}<br>
                        <strong>API:</strong> FastAPI + ${result.system.includes('LangChain') ? 'LangChain' : 'Fallback'}
                    `;
                    showResult('statusResult', html, 'success');
                } catch (error) {
                    showResult('statusResult', '❌ Error: ' + error.message, 'error');
                }
            }

            function showResult(elementId, message, type) {
                const element = document.getElementById(elementId);
                element.innerHTML = `<div class="result ${type}">${message}</div>`;
            }

            // Load status on page load
            getStatus();
        </script>
    </body>
    </html>
    """

@app.post("/upload-document")
async def upload_document(doc: DocumentUpload):
    try:
        if not doc.text.strip():
            raise HTTPException(status_code=400, detail="No text provided")

        success = rag_system.add_document(doc.text, doc.source)

        if success:
            return {"success": True, "message": "Document uploaded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to process document")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(query: QueryRequest):
    try:
        result = rag_system.query(query.question, query.top_k)
        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    try:
        return rag_system.get_status()
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Session 04 Production RAG",
        "langchain_available": LANGCHAIN_AVAILABLE
    }

if __name__ == "__main__":
    print("🚀 Starting Session 04: Production RAG System")
    print("📚 Building on Sessions 1-3 with LangChain integration")
    print("🌐 Visit: http://localhost:8000")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)