# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
from typing import Optional
import PyPDF2
import io
import json

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Simple in-memory storage for demo purposes
uploaded_documents = {}

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-3.5-turbo"  # Optional model selection with default
    api_key: str          # OpenAI API key for authentication

class RAGChatRequest(BaseModel):
    user_message: str
    api_key: str
    model: Optional[str] = "gpt-3.5-turbo"
    developer_message: Optional[str] = "You are a helpful research assistant. Answer questions based on the uploaded document context."

# Simple RAG implementation
class SimpleRAG:
    def __init__(self):
        self.documents = {}
    
    def add_document(self, filename: str, text: str):
        # Simple text chunking
        chunks = self._chunk_text(text)
        self.documents[filename] = chunks
    
    def _chunk_text(self, text: str, chunk_size: int = 1000):
        """Simple text chunking by character count"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def search(self, query: str, filename: str = None):
        """Simple keyword-based search"""
        if filename and filename in self.documents:
            chunks = self.documents[filename]
        else:
            # Search all documents
            chunks = []
            for doc_chunks in self.documents.values():
                chunks.extend(doc_chunks)
        
        # Simple keyword matching
        query_words = query.lower().split()
        scored_chunks = []
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            score = sum(1 for word in query_words if word in chunk_lower)
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by score and return top chunks
        scored_chunks.sort(reverse=True)
        return [chunk for _, chunk in scored_chunks[:3]]

# Initialize RAG system
rag_system = SimpleRAG()

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Use environment variable API key if none provided
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Initialize OpenAI client with the provided API key
        client = OpenAI(api_key=api_key)

        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": request.developer_message},
                    {"role": "user", "content": request.user_message}
                ],
                stream=True  # Enable streaming response
            )

            # Iterate through the streaming response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    # Format the response as Server-Sent Events
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
            
            # Send completion signal
            yield "data: [DONE]\n\n"

        # Return streaming response
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PDF Upload endpoint
@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read the uploaded file
        contents = await file.read()
        
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Store the document in RAG system
        rag_system.add_document(file.filename, text)
        uploaded_documents[file.filename] = text
        
        return {"message": f"PDF '{file.filename}' uploaded and processed successfully", "filename": file.filename}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# RAG Chat endpoint
@app.post("/api/rag-chat")
async def rag_chat(request: RAGChatRequest):
    try:
        # Use environment variable API key if none provided
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Search for relevant context
        relevant_chunks = rag_system.search(request.user_message)
        
        if not relevant_chunks:
            context = "No relevant context found in uploaded documents."
        else:
            context = "\n\n".join(relevant_chunks)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request with context
            messages = [
                {"role": "system", "content": f"{request.developer_message}\n\nContext from uploaded documents:\n{context}"},
                {"role": "user", "content": request.user_message}
            ]
            
            stream = client.chat.completions.create(
                model=request.model,
                messages=messages,
                stream=True
            )

            # Iterate through the streaming response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    # Format the response as Server-Sent Events
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
            
            # Send completion signal
            yield "data: [DONE]\n\n"

        # Return streaming response
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
