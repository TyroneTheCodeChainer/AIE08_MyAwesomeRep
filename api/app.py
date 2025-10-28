# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
from typing import Optional
import random

# Initialize FastAPI application with a title
app = FastAPI(
    title="AI Engineer Challenge - RAG System API",
    description="Production-ready RAG system with FastAPI and OpenAI integration",
    version="1.0.0"
)

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

# Collection of dad jokes
DAD_JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "I don't trust stairs. They're always up to something.",
    "Why don't programmers like nature? It has too many bugs.",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "What do you call a fake noodle? An impasta!",
    "Why did the coffee file a police report? It got mugged!",
    "What do you call a sleeping bull? A bulldozer!",
    "What kind of cheese do you use to hide a horse? Mascarpone!",
]

# Collection of programming dad jokes
PROGRAMMING_DAD_JOKES = [
    "How do you comfort a JavaScript bug? You console it!",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "Why do programmers always mix up Halloween and Christmas? Because Oct 31 == Dec 25!",
    "Why don't programmers like to go outside? The sun gives them syntax errors!",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
    "Why did the programmer quit his job? He didn't get arrays!",
    "I'm not arguing, I'm just explaining why I'm right in a loop.",
    "Why do programmers hate nature? It has bugs.",
    "There are only 10 types of people in the world: those who understand binary and those who don't.",
]

# Collection of programming quotes
PROGRAMMING_QUOTES = [
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand. - Martin Fowler",
    "The best code is no code at all. And the second best code is self-documenting code. - Jeff Atwood",
    "First, solve the problem. Then, write the code. - John Johnson",
    "Simplicity is the ultimate sophistication. - Leonardo da Vinci",
    "Code is like humor. When you have to explain it, it's bad. - Cory House",
    "Programming isn't about what you know; it's about what you can figure out. - Chris Pine",
    "The only way to learn a new programming language is by writing programs in it. - Dennis Ritchie",
    "Before software can be reusable it first has to be usable. - Ralph Johnson",
    "It's not a bug – it's an undocumented feature. - Anonymous",
    "Always code as if the person who ends up maintaining your code is a violent psychopath who knows where you live. - Martin Golding",
]

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
                    {"role": "developer", "content": request.developer_message},
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

# Define a root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Engineer Challenge RAG System API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "sessions": "/api/sessions",
            "joke": "/api/joke",
            "programming_joke": "/api/joke/programming",
            "programming_quote": "/api/quote/programming"
        }
    }

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "RAG API is running",
        "service": "FastAPI RAG System"
    }

# Session-specific status endpoint
@app.get("/api/sessions")
async def sessions():
    return {
        "message": "Available RAG implementations",
        "sessions": {
            "session_03": {
                "framework": "Flask",
                "features": ["PDF processing", "Vector search", "OpenAI integration"],
                "status": "available",
                "location": "/03_End-to-End_RAG/"
            },
            "session_04": {
                "framework": "FastAPI + LangChain",
                "features": ["ChromaDB", "LangGraph", "LangSmith", "Multi-agent"],
                "status": "available",
                "location": "/04_Production_RAG/"
            }
        },
        "current_api": {
            "framework": "FastAPI",
            "features": ["OpenAI Chat", "Streaming responses", "CORS enabled"],
            "status": "active"
        }
    }

# Define the dad joke endpoint
@app.get("/api/joke")
async def get_dad_joke():
    """
    Get a random dad joke.
    """
    return {
        "joke": random.choice(DAD_JOKES),
        "type": "dad joke"
    }

# Define the programming dad joke endpoint
@app.get("/api/joke/programming")
async def get_programming_dad_joke():
    """
    Get a random programming-related dad joke.
    """
    return {
        "joke": random.choice(PROGRAMMING_DAD_JOKES),
        "type": "programming dad joke"
    }

# Define the programming quote endpoint
@app.get("/api/quote/programming")
async def get_programming_quote():
    """
    Get a random programming quote.
    """
    return {
        "quote": random.choice(PROGRAMMING_QUOTES),
        "type": "programming quote"
    }

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
