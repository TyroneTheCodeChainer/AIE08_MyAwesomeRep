# =============================================================================
# EDUCATIONAL RAG (RETRIEVAL-AUGMENTED GENERATION) SYSTEM
# =============================================================================
# This file demonstrates how to build a complete RAG system from scratch
# with extensive comments and explanations for learning purposes.
# 
# WHAT IS RAG?
# RAG = Retrieval + Augmentation + Generation
# 1. RETRIEVAL: Find relevant information from documents
# 2. AUGMENTATION: Add that information to the user's question
# 3. GENERATION: Use AI to create a natural answer
#
# Think of it like a smart librarian who:
# - Finds the right books (Retrieval)
# - Reads the relevant pages (Augmentation) 
# - Writes a helpful answer (Generation)
# =============================================================================

# =============================================================================
# STEP 1: IMPORT NECESSARY LIBRARIES
# =============================================================================
# These are like tools in a toolbox - each one does a specific job

# FastAPI - A modern web framework for building APIs (Application Programming Interfaces)
# An API is like a waiter in a restaurant - it takes your order (request) 
# and brings you food (response) from the kitchen (our RAG system)
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Pydantic - A library for data validation and settings management
# Think of it as a bouncer at a club - it checks if data is in the right format
from pydantic import BaseModel

# OpenAI - The company that created ChatGPT and other AI models
# We'll use their API to get AI responses and create embeddings
from openai import OpenAI

# Standard Python libraries for basic operations
import os          # For environment variables (like API keys)
import sys         # For system-specific parameters
import PyPDF2      # For reading PDF files
import io          # For handling input/output streams
import math        # For mathematical operations
from typing import Optional, List  # For type hints (makes code clearer)
import json        # For handling JSON data

# =============================================================================
# STEP 2: DEFINE DATA STRUCTURES
# =============================================================================
# These are like forms that define what information we expect

class ChatRequest(BaseModel):
    """
    This defines the structure of a chat request from the user.
    Think of it as a form that the user fills out.
    
    Attributes:
        message (str): The user's question or message
        session_id (Optional[str]): A unique identifier for the conversation
    """
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """
    This defines the structure of our response back to the user.
    Like a standardized reply format.
    
    Attributes:
        response (str): The AI's answer to the user's question
        session_id (str): The conversation identifier
        sources (List[str]): Where the information came from
    """
    response: str
    session_id: str
    sources: List[str] = []

# =============================================================================
# STEP 3: THE HEART OF OUR RAG SYSTEM - THE SIMPLERAG CLASS
# =============================================================================
# This class contains all the logic for our RAG system
# Think of it as the brain of our application

class SimpleRAG:
    """
    A simple but complete RAG (Retrieval-Augmented Generation) system.
    
    This class implements the three main components of RAG:
    1. Document storage and chunking
    2. Embedding creation and similarity search
    3. Answer generation using retrieved context
    
    How it works:
    1. User uploads documents (PDFs, text files)
    2. We break documents into smaller chunks (like paragraphs)
    3. We convert each chunk into a mathematical representation (embedding)
    4. When user asks a question, we find the most similar chunks
    5. We use those chunks as context to generate an answer
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the RAG system.
        
        Args:
            api_key (str): Your OpenAI API key for accessing AI models
        
        What happens here:
        - We create a connection to OpenAI's servers
        - We initialize empty lists to store our documents and embeddings
        - Think of this as setting up our workspace
        """
        # Create a client to communicate with OpenAI's servers
        # This is like getting a phone number to call OpenAI
        self.client = OpenAI(api_key=api_key)
        
        # These are our storage containers
        # documents: stores the actual text chunks
        # embeddings: stores the mathematical representations of those chunks
        # Think of documents as books and embeddings as their "fingerprints"
        self.documents = []      # List to store text chunks
        self.embeddings = []     # List to store mathematical representations
    
    def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Break a long document into smaller, manageable pieces called 'chunks'.
        
        Why do we need this?
        - AI models have limits on how much text they can process at once
        - A token is roughly 4 characters, so 1000 characters ≈ 250 tokens
        - Most AI models can handle 4000-8000 tokens at once
        - We need to break long documents into smaller pieces
        
        Args:
            text (str): The long text we want to break up
            chunk_size (int): Maximum size of each chunk (default: 1000 characters)
            overlap (int): How much each chunk overlaps with the next (default: 200 characters)
        
        Returns:
            List[str]: A list of text chunks
        
        The overlap is crucial - it prevents us from losing context at boundaries.
        Think of it like overlapping tiles on a roof to prevent leaks.
        """
        # If the text is already small enough, just return it as-is
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []  # This will store our chunks
        start = 0    # Starting position in the text
        
        # Keep going until we've processed all the text
        while start < len(text):
            # Calculate where this chunk should end
            end = start + chunk_size
            
            # If we've reached the end of the text, take everything remaining
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at a natural boundary (sentence or paragraph)
            # This prevents cutting words or sentences in half
            chunk = text[start:end]
            
            # Look for the last period (end of sentence)
            last_period = chunk.rfind('.')
            
            # Look for the last newline (end of paragraph)
            last_newline = chunk.rfind('\n')
            
            # Choose the better break point (whichever is later)
            break_point = max(last_period, last_newline)
            
            # Only use this break point if it's not too far back
            # (We don't want tiny chunks)
            if break_point > start + chunk_size // 2:
                end = start + break_point + 1
            
            # Add this chunk to our list
            chunks.append(text[start:end])
            
            # Move to the next chunk, but with overlap
            # The overlap ensures we don't lose context between chunks
            start = end - overlap
            
        return chunks
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Convert text into a mathematical representation called an 'embedding'.
        
        What is an embedding?
        - It's a list of numbers that represents the meaning of the text
        - Similar texts have similar embeddings
        - We can use math to find similar texts by comparing embeddings
        - Think of it as creating a unique "fingerprint" for each piece of text
        
        Args:
            text (str): The text we want to convert to an embedding
        
        Returns:
            List[float]: A list of 1536 numbers representing the text
        
        Why 1536 numbers?
        - This is the size of OpenAI's text-embedding-3-small model
        - More numbers = more detail, but also more storage and computation
        - 1536 is a good balance between accuracy and efficiency
        """
        try:
            # Send the text to OpenAI's embedding model
            # This is like asking an expert to create a detailed description
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # The specific model to use
                input=text                       # The text to convert
            )
            
            # Extract the embedding from the response
            # The response contains the list of numbers we need
            return response.data[0].embedding
            
        except Exception as e:
            # If something goes wrong, print the error and return a default embedding
            # This prevents our system from crashing
            print(f"Error getting embedding: {e}")
            return [0.0] * 1536  # Default embedding (all zeros)
    
    def add_documents(self, texts: List[str]):
        """
        Add documents to our RAG system by chunking them and creating embeddings.
        
        This is like adding books to a library:
        1. We break each book into chapters (chunks)
        2. We create a catalog entry for each chapter (embedding)
        3. We store both the chapter and its catalog entry
        
        Args:
            texts (List[str]): List of documents to add to the system
        
        What happens:
        1. Clear any existing documents (start fresh)
        2. For each document:
           a. Split it into chunks
           b. For each chunk:
              - Add it to our documents list
              - Create an embedding for it
              - Add the embedding to our embeddings list
        """
        # Start fresh - clear any existing documents
        self.documents = []
        self.embeddings = []
        
        # Process each document
        for text in texts:
            # Break the document into chunks
            chunks = self.split_text(text)
            
            # Process each chunk
            for chunk in chunks:
                # Only add non-empty chunks (skip blank lines, etc.)
                if chunk.strip():
                    # Store the actual text
                    self.documents.append(chunk)
                    
                    # Create an embedding for this chunk
                    # This is like creating a detailed catalog entry
                    embedding = self.get_embedding(chunk)
                    self.embeddings.append(embedding)
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Calculate how similar two embeddings are using cosine similarity.
        
        What is cosine similarity?
        - It measures the angle between two vectors (lists of numbers)
        - If two vectors point in the same direction, they're similar
        - If they point in opposite directions, they're different
        - The result is a number between -1 and 1:
          * 1 = identical
          * 0 = no relationship
          * -1 = opposite
        
        Args:
            a (List[float]): First embedding
            b (List[float]): Second embedding
        
        Returns:
            float: Similarity score between -1 and 1
        
        Real-world analogy:
        - Like measuring how similar two people's music tastes are
        - If they like the same songs, similarity is high
        - If they like completely different music, similarity is low
        """
        try:
            # Check if the embeddings are the same size
            if len(a) != len(b):
                return 0.0
            
            # Calculate the dot product (how much the vectors align)
            # This is like counting how many songs both people like
            dot_product = sum(x * y for x, y in zip(a, b))
            
            # Calculate the magnitude (length) of each vector
            # This normalizes for the size of the vectors
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            
            # If either vector has zero length, they're not similar
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            # Calculate the cosine similarity
            # This gives us a number between -1 and 1
            return dot_product / (norm_a * norm_b)
            
        except:
            # If anything goes wrong, return 0 (no similarity)
            return 0.0
    
    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """
        Find the most relevant document chunks for a given question.
        
        This is like a librarian finding the most relevant books for your question.
        
        Args:
            query (str): The user's question
            k (int): How many relevant chunks to return (default: 3)
        
        Returns:
            List[str]: The most relevant document chunks
        
        How it works:
        1. Convert the question into an embedding
        2. Compare it with all stored document embeddings
        3. Find the most similar ones
        4. Return the corresponding document chunks
        """
        # If we don't have any documents, return empty list
        if not self.documents:
            return []
        
        # Convert the question into an embedding
        # This is like creating a "search fingerprint" for the question
        query_embedding = self.get_embedding(query)
        
        # Calculate similarity between the question and each document
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            # Calculate how similar this document is to the question
            similarity = self.cosine_similarity(query_embedding, doc_embedding)
            # Store both the similarity score and the document index
            similarities.append((similarity, i))
        
        # Sort by similarity (highest first)
        # This puts the most relevant documents at the top
        similarities.sort(reverse=True)
        
        # Return the top k most relevant document chunks
        relevant_docs = []
        for similarity, doc_index in similarities[:k]:
            # Only include documents with reasonable similarity
            if similarity > 0.1:  # Threshold to filter out irrelevant docs
                relevant_docs.append(self.documents[doc_index])
        
        return relevant_docs
    
    def chat(self, query: str) -> str:
        """
        Generate an answer to a user's question using the RAG system.
        
        This is the main function that ties everything together:
        1. Find relevant information (Retrieval)
        2. Add it to the question (Augmentation)
        3. Generate an answer (Generation)
        
        Args:
            query (str): The user's question
        
        Returns:
            str: The AI's answer based on the retrieved context
        
        The RAG Process:
        1. RETRIEVAL: Find relevant document chunks
        2. AUGMENTATION: Combine the question with the context
        3. GENERATION: Use AI to create a natural answer
        """
        # STEP 1: RETRIEVAL - Find relevant information
        # This is like asking a librarian to find relevant books
        relevant_docs = self.retrieve(query)
        
        # If we don't find any relevant information, say so
        if not relevant_docs:
            return "I don't have enough information to answer that question. Please try uploading some relevant documents first."
        
        # STEP 2: AUGMENTATION - Combine question with context
        # This is like giving a lawyer all the relevant case files
        context = "\n\n".join(relevant_docs)
        
        # Create a detailed prompt that includes both the context and the question
        # This is like writing a detailed brief for the AI
        prompt = f"""You are a helpful AI assistant. Answer the question based on the provided context.

Context (information from documents):
{context}

Question: {query}

Instructions:
- Answer based only on the information provided in the context above
- If the context doesn't contain enough information to answer the question, say so
- Be helpful, accurate, and concise
- If you're not sure about something, say so rather than guessing

Answer:"""
        
        try:
            # STEP 3: GENERATION - Use AI to create the answer
            # This is like having an expert write a response based on the brief
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # The AI model to use
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,  # Limit response length
                temperature=0.7  # Control creativity (0 = very focused, 1 = very creative)
            )
            
            # Extract the answer from the response
            return response.choices[0].message.content
            
        except Exception as e:
            # If something goes wrong, return an error message
            return f"Sorry, I encountered an error while generating a response: {str(e)}"

# =============================================================================
# STEP 4: CREATE THE WEB API USING FASTAPI
# =============================================================================
# This creates a web server that can receive requests and send responses
# Think of it as creating a restaurant that serves RAG responses

# Create the FastAPI application
# This is like opening a restaurant
app = FastAPI(
    title="Educational RAG System",
    description="A complete RAG system with extensive comments for learning",
    version="1.0.0"
)

# Add CORS middleware
# This allows web browsers to make requests to our API
# Without this, browsers would block requests for security reasons
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any website (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize our RAG system
# This is like setting up the kitchen in our restaurant
rag_system = SimpleRAG(api_key=os.getenv("OPENAI_API_KEY"))

# =============================================================================
# STEP 5: DEFINE API ENDPOINTS (THE MENU)
# =============================================================================
# These are the different "dishes" our API can serve
# Each endpoint handles a specific type of request

@app.get("/")
async def root():
    """
    Welcome endpoint - the first thing users see.
    
    This is like the host greeting you when you enter the restaurant.
    """
    return {
        "message": "Welcome to the Educational RAG System!",
        "description": "This system can answer questions based on uploaded documents.",
        "endpoints": {
            "upload": "/api/upload-pdf - Upload a PDF document",
            "chat": "/api/chat - Ask questions about uploaded documents",
            "status": "/api/status - Check system status"
        }
    }

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF document.
    
    This is like bringing ingredients to the kitchen.
    
    Args:
        file (UploadFile): The PDF file to upload
    
    Returns:
        dict: Success message and processing results
    
    What happens:
    1. Check if the file is a PDF
    2. Read the file content
    3. Extract text from the PDF
    4. Process the text into chunks
    5. Create embeddings for each chunk
    6. Store everything in our RAG system
    """
    # Check if the file is a PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported. Please upload a .pdf file."
        )
    
    try:
        # Read the file content
        # This is like reading the recipe from a cookbook
        content = await file.read()
        
        # Extract text from the PDF
        # This is like extracting the actual recipe from the cookbook
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        
        # Go through each page and extract text
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                text += page_text + "\n"  # Add newline between pages
            except Exception as e:
                print(f"Error extracting text from page {page_num}: {e}")
                continue
        
        # If we couldn't extract any text, return an error
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the PDF. The file might be corrupted or contain only images."
            )
        
        # Process the document into our RAG system
        # This is like preparing the ingredients for cooking
        rag_system.add_documents([text])
        
        # Return success message with statistics
        return {
            "message": "PDF processed successfully!",
            "filename": file.filename,
            "text_length": len(text),
            "chunks_created": len(rag_system.documents),
            "status": "ready_for_questions"
        }
        
    except Exception as e:
        # If something goes wrong, return an error
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask questions about uploaded documents.
    
    This is like ordering food from the menu.
    
    Args:
        request (ChatRequest): The user's question and session info
    
    Returns:
        ChatResponse: The AI's answer and metadata
    
    What happens:
    1. Receive the user's question
    2. Use our RAG system to find relevant information
    3. Generate an answer based on that information
    4. Return the answer along with source information
    """
    try:
        # Generate an answer using our RAG system
        # This is like the chef preparing the meal
        answer = rag_system.chat(request.message)
        
        # Get the sources (relevant document chunks)
        # This is like listing the ingredients used in the dish
        sources = rag_system.retrieve(request.message, k=3)
        
        # Return the response
        return ChatResponse(
            response=answer,
            session_id=request.session_id or "default",
            sources=sources
        )
        
    except Exception as e:
        # If something goes wrong, return an error
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

@app.get("/api/status")
async def get_status():
    """
    Check the status of the RAG system.
    
    This is like checking if the kitchen is ready to serve.
    
    Returns:
        dict: System status and statistics
    """
    return {
        "status": "operational",
        "documents_loaded": len(rag_system.documents),
        "embeddings_created": len(rag_system.embeddings),
        "system_ready": len(rag_system.documents) > 0,
        "message": "System is ready to answer questions!" if rag_system.documents else "Please upload a document first."
    }

# =============================================================================
# STEP 6: RUN THE APPLICATION
# =============================================================================
# This starts the web server so it can receive requests

if __name__ == "__main__":
    """
    This runs when the script is executed directly.
    It starts the web server on your local machine.
    """
    import uvicorn
    
    # Start the server
    # This is like opening the restaurant for business
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,       # Use port 8000
        reload=True      # Automatically restart when code changes (for development)
    )

# =============================================================================
# EDUCATIONAL NOTES
# =============================================================================
"""
This RAG system demonstrates several key concepts:

1. DOCUMENT PROCESSING:
   - How to break large documents into manageable chunks
   - Why chunking is necessary (AI model limits)
   - How overlap prevents loss of context

2. EMBEDDINGS:
   - How to convert text into mathematical representations
   - Why embeddings are useful for similarity search
   - How to calculate similarity between texts

3. RETRIEVAL:
   - How to find relevant information for a question
   - Why similarity search works better than keyword search
   - How to rank results by relevance

4. GENERATION:
   - How to combine retrieved context with user questions
   - How to create effective prompts for AI models
   - How to handle errors gracefully

5. WEB API:
   - How to create a web service that others can use
   - How to handle file uploads and data validation
   - How to structure responses consistently

This system can be extended in many ways:
- Add support for more file types (Word, PowerPoint, etc.)
- Implement more sophisticated chunking strategies
- Add user authentication and session management
- Implement caching for better performance
- Add monitoring and logging
- Deploy to cloud platforms for scalability
"""
