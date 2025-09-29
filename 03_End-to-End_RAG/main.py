"""
Session 03: End-to-End RAG System - Production Implementation
============================================================

Complete RAG system using FastAPI, OpenAI, and aimakerspace library.
Implements PDF upload, indexing, and context-aware chat functionality.

Requirements Fulfilled:
- PDF upload and processing using aimakerspace
- RAG chat with document context
- Dream Research Mode specialization
- Vercel deployment ready
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import io
import tempfile
from typing import List, Dict, Any, Optional
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import aimakerspace components as required by homework
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter
from aimakerspace.openai_utils.chatmodel import ChatOpenAI
from aimakerspace.openai_utils.embedding import EmbeddingModel

# Create FastAPI app
app = FastAPI(
    title="Session 03: End-to-End RAG System",
    description="Complete RAG implementation with PDF processing and Dream Research Mode",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    user_message: str
    dream_mode: bool = False

class ChatResponse(BaseModel):
    response: str
    source_documents: List[str] = []
    context_used: bool = False

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_added: int
    file_size_mb: str

# Global RAG system components
rag_system = None
vector_db = None
chat_model = None
embedding_model = None

def initialize_rag_system():
    """Initialize the RAG system with aimakerspace components"""
    global rag_system, vector_db, chat_model, embedding_model

    try:
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Initialize aimakerspace components
        embedding_model = EmbeddingModel()
        chat_model = ChatOpenAI()
        vector_db = VectorDatabase()

        print("RAG system initialized successfully with aimakerspace")
        return True

    except Exception as e:
        print(f"RAG system initialization failed: {e}")
        return False

class SimpleRAGSystem:
    """Simple RAG implementation using aimakerspace library"""

    def __init__(self):
        self.documents = []
        self.chunks = []
        self.embeddings = []
        self.vector_db = VectorDatabase()
        self.chat_model = ChatOpenAI()
        self.embedding_model = EmbeddingModel()
        self.text_splitter = CharacterTextSplitter()

    def add_document(self, filename: str, text: str) -> int:
        """Add document to RAG system using aimakerspace"""
        try:
            # Split text into chunks using aimakerspace
            chunks = self.text_splitter.split_text(text)

            # Create embeddings and add to vector database
            for i, chunk in enumerate(chunks):
                # Generate embedding for chunk
                embedding = self.embedding_model.get_embedding(chunk)

                # Add to vector database
                self.vector_db.insert(
                    vector=embedding,
                    text=chunk,
                    metadata={"filename": filename, "chunk_id": i}
                )

            self.documents.append(filename)
            return len(chunks)

        except Exception as e:
            print(f"Error adding document: {e}")
            # Fallback to simple implementation
            chunks = text.split('\n\n')
            self.chunks.extend([chunk.strip() for chunk in chunks if chunk.strip()])
            return len(chunks)

    def search(self, query: str, k: int = 3) -> List[str]:
        """Search for relevant documents"""
        try:
            # Use vector database for semantic search
            query_embedding = self.embedding_model.get_embedding(query)
            results = self.vector_db.search(query_embedding, k=k)
            return [result["text"] for result in results]

        except Exception as e:
            print(f"Error in search: {e}")
            # Fallback to keyword search
            query_words = query.lower().split()
            scored_chunks = []

            for chunk in self.chunks:
                chunk_lower = chunk.lower()
                score = sum(1 for word in query_words if word in chunk_lower)
                if score > 0:
                    scored_chunks.append((score, chunk))

            scored_chunks.sort(reverse=True)
            return [chunk for _, chunk in scored_chunks[:k]]

    def generate_response(self, query: str, context: List[str], dream_mode: bool = False) -> str:
        """Generate response using context and chat model"""
        try:
            if not context:
                return "No relevant documents found. Please upload a PDF document first."

            # Prepare context
            context_text = "\n\n".join(context)

            # Create specialized prompt for dream research mode
            if dream_mode:
                system_message = """You are a specialized dream interpretation assistant with expertise in sleep science,
                psychology, and neuroscience. You analyze dreams using scientifically validated research and provide
                insights based on REM sleep studies, Jungian psychology, and cognitive science. Always ground your
                interpretations in established research while being empathetic and supportive."""
            else:
                system_message = "You are a helpful assistant. Answer questions based on the provided context."

            # Create prompt
            prompt = f"""System: {system_message}

Context: {context_text}

Question: {query}

Please provide a comprehensive answer based on the provided context. If the answer is not in the context, say so."""

            # Use aimakerspace chat model
            messages = [{"role": "user", "content": prompt}]
            response = self.chat_model.run(messages)
            return response

        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"

# Initialize global RAG system
rag_system = SimpleRAGSystem()

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global rag_system
    initialize_rag_system()

# API Endpoints

@app.get("/")
async def read_root():
    """Root endpoint with system information"""
    return {
        "message": "Session 03: End-to-End RAG System",
        "description": "Complete RAG implementation with PDF processing and Dream Research Mode",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "PDF upload and processing",
            "Semantic document search",
            "Context-aware chat responses",
            "Dream Research Mode specialization"
        ]
    }

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    try:
        # Check if API key is configured
        api_key = os.getenv("OPENAI_API_KEY")
        api_configured = bool(api_key and api_key != "your_openai_api_key_here")

        return {
            "status": "ok",
            "message": "RAG Backend is running",
            "rag_system_initialized": rag_system is not None,
            "openai_api_configured": api_configured,
            "documents_loaded": len(rag_system.documents) if rag_system else 0
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/upload-pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file using aimakerspace"""
    try:
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Check file size (5MB limit)
        content = await file.read()
        file_size = len(content)

        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 5MB. Your file is {file_size / (1024*1024):.1f}MB"
            )

        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")

        # Add to RAG system using aimakerspace
        chunks_added = rag_system.add_document(file.filename, text)

        return UploadResponse(
            message=f"PDF '{file.filename}' uploaded and processed successfully",
            filename=file.filename,
            chunks_added=chunks_added,
            file_size_mb=f"{file_size / (1024*1024):.2f}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/api/rag-chat", response_model=ChatResponse)
async def rag_chat(request: ChatRequest):
    """Chat with RAG system using uploaded documents"""
    try:
        user_message = request.user_message
        dream_mode = request.dream_mode

        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")

        # Search for relevant documents
        relevant_chunks = rag_system.search(user_message, k=3)

        if not relevant_chunks:
            return ChatResponse(
                response="No documents have been uploaded yet. Please upload a PDF first.",
                source_documents=[],
                context_used=False
            )

        # Generate response using aimakerspace
        response = rag_system.generate_response(user_message, relevant_chunks, dream_mode)

        return ChatResponse(
            response=response,
            source_documents=relevant_chunks,
            context_used=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during chat: {str(e)}")

@app.post("/api/chat")
async def regular_chat(request: ChatRequest):
    """Regular chat without RAG (for comparison)"""
    try:
        user_message = request.user_message

        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")

        # Use chat model directly without context
        messages = [{"role": "user", "content": f"You are a helpful AI assistant. {user_message}"}]
        response = rag_system.chat_model.run(messages)

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during chat: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Endpoint {request.url.path} not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Required for Vercel deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)