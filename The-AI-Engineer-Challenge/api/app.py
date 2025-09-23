"""
AI-Powered RAG (Retrieval-Augmented Generation) Chat System
==========================================================

This is the main backend server for our AI chat application. Think of it as the "brain" 
of our system that handles all the heavy lifting behind the scenes.

WHAT THIS SYSTEM DOES:
- Allows users to chat with an AI assistant
- Lets users upload PDF documents 
- Enables asking questions about the uploaded documents
- Provides intelligent answers based on document content

HOW IT WORKS (Simple Explanation):
1. User uploads a PDF → System reads and stores the text
2. User asks a question → System finds relevant parts of the PDF
3. System combines the relevant text with AI to give a smart answer

This file contains all the server code that makes this magic happen!
"""

# =============================================================================
# IMPORTING NECESSARY TOOLS AND LIBRARIES
# =============================================================================
# These are like toolboxes that give us special abilities:

from fastapi import FastAPI, HTTPException, UploadFile, File
# FastAPI: A modern web framework that makes it easy to create APIs
# Think of it as the foundation that lets our server talk to the internet

from fastapi.responses import StreamingResponse
# StreamingResponse: Allows us to send data in real-time (like a live stream)
# This makes the chat feel instant and responsive

from fastapi.middleware.cors import CORSMiddleware
# CORS: Allows our frontend (the website) to talk to our backend (this server)
# Without this, browsers would block the communication for security

from pydantic import BaseModel
# Pydantic: Helps us validate and structure data
# Like having a bouncer at a club who checks IDs - ensures data is correct

from openai import OpenAI
# OpenAI: The library that connects us to ChatGPT/GPT models
# This is how we get the AI to actually generate responses

import os
# os: Lets us access environment variables (like secret API keys)
# Think of it as a safe way to store passwords and secrets

from typing import Optional
# typing: Helps us specify what type of data we expect
# Like labeling boxes so we know what's inside

import PyPDF2
# PyPDF2: A library that can read PDF files and extract text
# Like having a special reader that can understand PDF documents

import io
# io: Helps us work with data streams (like reading files in memory)
# Think of it as a temporary workspace for processing files

import json
# json: A format for storing and sending data
# Like a universal language that computers use to talk to each other

# =============================================================================
# SETTING UP OUR WEB SERVER
# =============================================================================

# Create our main application - this is like starting up our server
app = FastAPI(title="AI-Powered RAG Chat System")

# Configure CORS (Cross-Origin Resource Sharing)
# This is like setting up security rules that allow our website to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any website (for development)
    allow_credentials=True,  # Allow cookies and authentication
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all types of headers
)

# =============================================================================
# DATA STORAGE (Simple In-Memory Storage)
# =============================================================================
# This is where we store uploaded documents temporarily
# In a real production system, this would be a proper database
uploaded_documents = {}

# =============================================================================
# DATA MODELS (Defining What Data Looks Like)
# =============================================================================
# These are like forms that define what information we expect to receive

class ChatRequest(BaseModel):
    """
    This defines the structure for regular chat messages.
    
    Think of this as a form that users fill out when they want to chat:
    - developer_message: The system prompt (how the AI should behave)
    - user_message: What the user wants to ask
    - model: Which AI model to use (like choosing between different AI assistants)
    - api_key: The secret key to access OpenAI's services
    """
    developer_message: str  # Instructions for how the AI should behave
    user_message: str       # The user's question or message
    model: Optional[str] = "gpt-3.5-turbo"  # Default AI model to use
    api_key: str           # Secret key for OpenAI access

class RAGChatRequest(BaseModel):
    """
    This defines the structure for RAG (document-based) chat messages.
    
    This is like a special form for when users want to ask questions 
    about documents they've uploaded.
    """
    user_message: str  # The user's question about the document
    api_key: str       # Secret key for OpenAI access
    model: Optional[str] = "gpt-3.5-turbo"  # Default AI model
    developer_message: Optional[str] = "You are a helpful research assistant. Answer questions based on the uploaded document context."

# =============================================================================
# RAG SYSTEM (The Document Processing Engine)
# =============================================================================

class SimpleRAG:
    """
    SimpleRAG: Our document processing and search system
    
    This is like having a super-smart librarian who can:
    1. Read and understand documents
    2. Break them into manageable pieces
    3. Find the most relevant parts when you ask questions
    
    HOW IT WORKS:
    - When you upload a PDF, it gets broken into small "chunks" of text
    - When you ask a question, it searches through these chunks
    - It finds the most relevant pieces and gives them to the AI
    - The AI uses this information to give you a smart answer
    """
    
    def __init__(self):
        """
        Initialize the RAG system.
        This is like setting up a new filing cabinet for documents.
        """
        self.documents = {}  # Dictionary to store all uploaded documents
    
    def add_document(self, filename: str, text: str):
        """
        Add a new document to our system.
        
        This is like taking a book, reading it, and filing it away
        in organized sections so we can find information quickly later.
        
        Parameters:
        - filename: The name of the file (like "research_paper.pdf")
        - text: The actual text content extracted from the PDF
        """
        # Break the text into smaller, manageable chunks
        chunks = self._chunk_text(text)
        # Store the chunks with the filename as the key
        self.documents[filename] = chunks
    
    def _chunk_text(self, text: str, chunk_size: int = 1000):
        """
        Break long text into smaller pieces (chunks).
        
        This is like cutting a long article into smaller paragraphs
        so it's easier to read and find specific information.
        
        Parameters:
        - text: The full text to break up
        - chunk_size: How big each chunk should be (default: 1000 characters)
        
        Returns:
        - List of text chunks
        """
        # Split the text into individual words
        words = text.split()
        chunks = []  # List to store our chunks
        current_chunk = []  # Current chunk we're building
        current_length = 0  # How many characters in current chunk
        
        # Go through each word and decide if it fits in current chunk
        for word in words:
            # If adding this word would make chunk too big, start a new chunk
            if current_length + len(word) + 1 > chunk_size and current_chunk:
                # Save the current chunk and start a new one
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                # Add this word to the current chunk
                current_chunk.append(word)
                current_length += len(word) + 1
        
        # Don't forget the last chunk!
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def search(self, query: str, filename: str = None):
        """
        Search for relevant information in our documents.
        
        This is like asking a librarian to find information about a topic.
        The librarian searches through all the books and finds the most
        relevant pages to show you.
        
        Parameters:
        - query: The question or topic to search for
        - filename: Specific document to search (optional)
        
        Returns:
        - List of relevant text chunks
        """
        # Decide which documents to search
        if filename and filename in self.documents:
            # Search only the specified document
            chunks = self.documents[filename]
        else:
            # Search all documents
            chunks = []
            for doc_chunks in self.documents.values():
                chunks.extend(doc_chunks)
        
        # Simple keyword matching (in a real system, this would be more sophisticated)
        query_words = query.lower().split()  # Convert to lowercase and split into words
        scored_chunks = []  # List to store chunks with their relevance scores
        
        # Score each chunk based on how many query words it contains
        for chunk in chunks:
            chunk_lower = chunk.lower()  # Convert chunk to lowercase for comparison
            # Count how many query words appear in this chunk
            score = sum(1 for word in query_words if word in chunk_lower)
            if score > 0:  # Only include chunks that have at least one matching word
                scored_chunks.append((score, chunk))
        
        # Sort chunks by relevance score (highest first)
        scored_chunks.sort(reverse=True)
        # Return the top 3 most relevant chunks
        return [chunk for _, chunk in scored_chunks[:3]]

# Create an instance of our RAG system
rag_system = SimpleRAG()

# =============================================================================
# API ENDPOINTS (The Different Functions Our Server Can Perform)
# =============================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Regular chat endpoint - for general conversation with the AI.
    
    This is like having a conversation with a smart assistant.
    You send a message, and the AI responds based on its general knowledge.
    
    HOW IT WORKS:
    1. User sends a message
    2. We connect to OpenAI's AI service
    3. AI generates a response
    4. We send the response back to the user in real-time
    
    Parameters:
    - request: Contains the user's message and settings
    
    Returns:
    - Streaming response with AI-generated text
    """
    try:
        # Get the API key (either from user or environment variable)
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Connect to OpenAI's service
        client = OpenAI(api_key=api_key)

        # Create a function that generates responses in real-time
        async def generate():
            """
            This function handles the streaming response.
            It's like having a conversation where the AI types its response
            character by character, making it feel more natural.
            """
            # Send the request to OpenAI
            stream = client.chat.completions.create(
                model=request.model,  # Which AI model to use
                messages=[
                    {"role": "system", "content": request.developer_message},  # Instructions for the AI
                    {"role": "user", "content": request.user_message}  # User's question
                ],
                stream=True  # Enable real-time streaming
            )

            # Send each piece of the response as it's generated
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    # Format the response for the frontend
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
            
            # Signal that the response is complete
            yield "data: [DONE]\n\n"

        # Return the streaming response
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        # If something goes wrong, return an error message
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    PDF upload endpoint - allows users to upload PDF documents.
    
    This is like having a document scanner that can read PDFs and
    store their content so you can ask questions about them later.
    
    HOW IT WORKS:
    1. User uploads a PDF file
    2. We extract all the text from the PDF
    3. We break the text into manageable chunks
    4. We store the chunks in our RAG system
    5. We confirm the upload was successful
    
    Parameters:
    - file: The uploaded PDF file
    
    Returns:
    - Confirmation message with filename
    """
    try:
        # Check if the file is actually a PDF
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read the uploaded file into memory
        contents = await file.read()
        
        # Extract text from the PDF using PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""
        
        # Go through each page and extract text
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        # Check if we actually found any text
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Store the document in our RAG system
        rag_system.add_document(file.filename, text)
        uploaded_documents[file.filename] = text
        
        # Return success message
        return {
            "message": f"PDF '{file.filename}' uploaded and processed successfully", 
            "filename": file.filename
        }
    
    except Exception as e:
        # If something goes wrong, return an error message
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/api/rag-chat")
async def rag_chat(request: RAGChatRequest):
    """
    RAG chat endpoint - for asking questions about uploaded documents.
    
    This is like having a conversation with an expert who has read
    all your documents and can answer questions based on their content.
    
    HOW IT WORKS:
    1. User asks a question about uploaded documents
    2. We search through all uploaded documents for relevant information
    3. We combine the relevant information with the user's question
    4. We send this to the AI to generate an informed answer
    5. We stream the response back to the user
    
    Parameters:
    - request: Contains the user's question and settings
    
    Returns:
    - Streaming response with AI-generated answer based on document content
    """
    try:
        # Get the API key
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Search for relevant information in our documents
        relevant_chunks = rag_system.search(request.user_message)
        
        # Prepare the context for the AI
        if not relevant_chunks:
            context = "No relevant context found in uploaded documents."
        else:
            context = "\n\n".join(relevant_chunks)
        
        # Connect to OpenAI
        client = OpenAI(api_key=api_key)
        
        # Create streaming response function
        async def generate():
            """
            Generate AI response based on document content.
            This combines the user's question with relevant document information
            to provide an informed answer.
            """
            # Prepare the messages for the AI
            messages = [
                {
                    "role": "system", 
                    "content": f"{request.developer_message}\n\nContext from uploaded documents:\n{context}"
                },
                {"role": "user", "content": request.user_message}
            ]
            
            # Send request to OpenAI
            stream = client.chat.completions.create(
                model=request.model,
                messages=messages,
                stream=True
            )

            # Stream the response back to the user
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
            
            # Signal completion
            yield "data: [DONE]\n\n"

        # Return the streaming response
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        # Return error if something goes wrong
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint - lets us know if the server is running properly.
    
    This is like checking if a machine is working by pressing a button
    and seeing if it responds. It's used for monitoring and debugging.
    
    Returns:
    - Simple status message confirming the server is working
    """
    return {"status": "ok"}