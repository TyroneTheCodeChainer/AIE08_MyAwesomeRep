# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
import sys
import PyPDF2
import io
import math
from typing import Optional, List
import json

# Simple RAG implementation (inline to avoid import issues)
class SimpleRAG:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.documents = []
        self.embeddings = []
        
    def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at sentence boundary
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > start + chunk_size // 2:  # Only break if we're not too far back
                end = start + break_point + 1
            
            chunks.append(text[start:end])
            start = end - overlap
            
        return chunks
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return [0.0] * 1536  # Default embedding size
    
    def add_documents(self, texts: List[str]):
        """Add documents to the RAG system"""
        self.documents = []
        self.embeddings = []
        
        for text in texts:
            chunks = self.split_text(text)
            for chunk in chunks:
                if chunk.strip():  # Only add non-empty chunks
                    self.documents.append(chunk)
                    # For now, skip embeddings to test basic functionality
                    # embedding = self.get_embedding(chunk)

                    # self.embeddings.append(embedding)
                    self.embeddings.append([0.0] * 1536)  # Placeholder embedding
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if len(a) != len(b):
                return 0.0
            
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
                
            return dot_product / (norm_a * norm_b)
        except:
            return 0.0
    
    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """Retrieve most relevant documents for query"""
        if not self.documents:
            return []
        
        # For now, just return the first k documents for testing
        return self.documents[:k]
    
    def chat(self, query: str, context: str) -> str:
        """Generate response using context"""
        try:
            print(f"Generating response for query: {query[:50]}...")
            print(f"Context length: {len(context)}")
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a specialized dream interpretation assistant with expertise in sleep science, psychology, and neuroscience. Analyze dreams using ONLY the provided scientific research context. Ground your interpretations in established studies about REM sleep, dream content analysis, and psychological theories. If the answer cannot be found in the context, say 'I don't have enough scientific information in the provided research to answer this question.'\n\nScientific Research Context:\n{context}"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            result = response.choices[0].message.content
            print(f"Generated response: {result[:100]}...")
            return result
        except Exception as e:
            print(f"Error in chat generation: {str(e)}")
            return f"Error generating response: {str(e)}"

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API with RAG")

# Global variables for RAG functionality
rag_system = None

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    api_key: str          # OpenAI API key for authentication

# Define the data model for RAG chat requests
class RAGChatRequest(BaseModel):
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    api_key: str          # OpenAI API key for authentication

# Define the data model for PDF upload responses
class PDFUploadResponse(BaseModel):
    message: str
    document_count: int
    success: bool

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize OpenAI client with the provided API key
        client = OpenAI(api_key=request.api_key)
        
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
            
            # Yield each chunk of the response as it becomes available
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # Return a streaming response to the client
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

# Simple test endpoint first
@app.post("/api/test-upload")
async def test_upload(file: UploadFile = File(...)):
    try:
        print(f"Test upload started for file: {file.filename}")
        
        # Just return basic file info
        content = await file.read()
        
        return {
            "message": f"File '{file.filename}' received successfully",
            "filename": file.filename,
            "size": len(content),
            "success": True
        }
        
    except Exception as e:
        print(f"Test upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test upload failed: {str(e)}")

# PDF upload endpoint for RAG functionality
@app.post("/api/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...), api_key: str = ""):
    global rag_system
    
    try:
        print(f"PDF upload started for file: {file.filename}")
        print(f"API key received: {api_key[:10] if api_key else 'None'}...")
        print(f"API key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            print("Error: No API key provided")
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Read PDF content
        pdf_content = await file.read()
        print(f"PDF content read, size: {len(pdf_content)} bytes")
        
        # Simple text extraction without complex processing
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            print(f"PDF reader created, pages: {len(pdf_reader.pages)}")
            
            # Extract text from first page only for testing
            text = ""
            if len(pdf_reader.pages) > 0:
                text = pdf_reader.pages[0].extract_text()
                print(f"First page text length: {len(text)}")
            
            if not text.strip():
                print("Error: No text extracted from PDF")
                raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
            
        except Exception as pdf_error:
            print(f"PDF processing error: {str(pdf_error)}")
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(pdf_error)}")
        
        # Initialize simple RAG system
        print("Initializing simple RAG system...")
        rag_system = SimpleRAG(api_key=api_key)
        
        # Add documents to RAG system
        print("Adding documents to RAG system...")
        rag_system.add_documents([text])
        
        print(f"RAG system initialized with {len(rag_system.documents)} documents")
        
        return PDFUploadResponse(
            message=f"PDF '{file.filename}' uploaded and indexed successfully",
            document_count=len(rag_system.documents),
            success=True
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Unexpected error in PDF upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# RAG chat endpoint
@app.post("/api/rag-chat")
async def rag_chat(request: RAGChatRequest):
    global rag_system
    
    try:
        print(f"RAG chat request received: {request.user_message[:50]}...")
        
        if rag_system is None:
            print("Error: No RAG system initialized")
            raise HTTPException(status_code=400, detail="No PDF has been uploaded yet. Please upload a PDF first.")
        
        print(f"RAG system has {len(rag_system.documents)} documents")
        
        # Retrieve relevant documents
        relevant_docs = rag_system.retrieve(request.user_message, k=3)
        print(f"Retrieved {len(relevant_docs)} relevant documents")
        
        # Create context from relevant documents
        context = "\n\n".join(relevant_docs)
        print(f"Context created, length: {len(context)}")
        
        # Generate response using simple RAG
        response_text = rag_system.chat(request.user_message, context)
        print(f"Response generated: {response_text[:100]}...")
        
        # Create async generator for streaming response
        async def generate():
            # Simulate streaming by yielding chunks
            words = response_text.split()
            for i, word in enumerate(words):
                if i == 0:
                    yield word
                else:
                    yield " " + word
                # Small delay to simulate streaming
                import asyncio
                await asyncio.sleep(0.05)
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Unexpected error in RAG chat: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error in RAG chat: {str(e)}")

# Check if PDF is uploaded
@app.get("/api/rag-status")
async def rag_status():
    global rag_system
    try:
        print(f"RAG status check - rag_system is None: {rag_system is None}")
        if rag_system:
            print(f"RAG system has {len(rag_system.documents)} documents")
        return {
            "pdf_uploaded": rag_system is not None,
            "document_count": len(rag_system.documents) if rag_system else 0
        }
    except Exception as e:
        print(f"Error in RAG status: {str(e)}")
        return {
            "pdf_uploaded": False,
            "document_count": 0
        }

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

