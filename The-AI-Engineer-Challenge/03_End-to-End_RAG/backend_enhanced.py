"""
Session 03: Enhanced RAG Backend with Comprehensive Comments
===========================================================

This is a complete RAG (Retrieval Augmented Generation) system that allows users to:
1. Upload PDF documents
2. Ask questions about those documents
3. Get AI-powered answers based on the document content

WHAT IS RAG?
RAG stands for "Retrieval Augmented Generation". Think of it like having a smart librarian:
- You give the librarian (our system) some books (PDF documents)
- When you ask a question, the librarian finds the most relevant parts of the books
- Then the librarian uses those relevant parts to give you a complete answer

This is much better than regular AI because it can use YOUR specific documents to answer questions,
not just general knowledge from the internet.

HOW THIS SYSTEM WORKS:
1. User uploads a PDF file
2. System extracts all text from the PDF
3. System breaks the text into small "chunks" (like paragraphs)
4. When user asks a question, system finds the most relevant chunks
5. System sends those chunks + the question to OpenAI's AI
6. AI gives an answer based on the specific document content
"""

# =============================================================================
# IMPORT STATEMENTS - These bring in the tools we need
# =============================================================================

from flask import Flask, request, jsonify, send_from_directory
# Flask is a web framework - it helps us create a web server that can handle
# requests from web browsers and send back responses

from flask_cors import CORS
# CORS stands for "Cross-Origin Resource Sharing" - this allows our frontend
# (running in a web browser) to talk to our backend (running on the server)
# Without CORS, browsers block this communication for security reasons

import os
# This helps us read environment variables (like API keys) from the system

import PyPDF2
# This library helps us read PDF files and extract text from them

import io
# This helps us work with data in memory (like PDF content)

import json
# This helps us format data to send back to the frontend

from openai import OpenAI
# This is the official library for talking to OpenAI's AI models

import tempfile
# This helps us create temporary files if needed

# =============================================================================
# SETUP - Initialize our web server and AI client
# =============================================================================

# Create our Flask web application
# Think of this as creating a restaurant - we're setting up the kitchen
app = Flask(__name__)

# Enable CORS for all routes - this is CRUCIAL for making it work!
# This tells the browser "it's okay to let our frontend talk to this backend"
# The "*" means "allow any website to connect" - in production, you'd be more specific
CORS(app, origins="*", allow_headers="*", methods=["GET", "POST", "OPTIONS"])

# Initialize OpenAI client - this is how we talk to the AI
# We get the API key from environment variables (stored securely on the server)
# Lazy initialization to avoid import-time errors
openai_client = None

def get_openai_client():
    """Get OpenAI client with lazy initialization."""
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        openai_client = OpenAI(api_key=api_key)
    return openai_client

# Simple in-memory storage for documents
# This is like a filing cabinet where we store all the document chunks
# In a real production system, you'd use a database instead
documents = {}

# =============================================================================
# RAG SYSTEM CLASS - The brain of our document processing
# =============================================================================

class SimpleRAG:
    """
    Simple RAG implementation that actually works.
    
    This class is like a smart librarian that can:
    1. Take documents and break them into searchable pieces
    2. Find the most relevant pieces when you ask a question
    3. Keep track of all the documents you've uploaded
    """
    
    def __init__(self):
        """
        Initialize the RAG system.
        This is like setting up a new filing system - we start with empty shelves.
        """
        self.documents = {}  # Empty dictionary to store our document chunks
    
    def add_document(self, filename, text):
        """
        Add a document to our RAG system.
        
        Think of this like a librarian taking a new book and:
        1. Breaking it into chapters and paragraphs
        2. Writing down what each section is about
        3. Filing it in the right place so it can be found later
        
        Args:
            filename (str): The name of the file (like "research_paper.pdf")
            text (str): The full text content of the document
            
        Returns:
            int: Number of chunks created from the document
        """
        # Simple chunking - split by paragraphs
        # This is like breaking a book into chapters
        # We split wherever we see two newlines in a row (paragraph breaks)
        chunks = text.split('\n\n')
        
        # Clean up the chunks - remove empty ones and extra whitespace
        # This is like removing blank pages from our filing system
        self.documents[filename] = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        # Return how many chunks we created
        return len(self.documents[filename])
    
    def search(self, query, filename=None):
        """
        Search for relevant document chunks based on a question.
        
        This is like asking the librarian "find me information about X"
        and the librarian searches through all the books to find the most relevant parts.
        
        Args:
            query (str): The question or search term
            filename (str, optional): If specified, only search in this specific document
            
        Returns:
            list: List of the most relevant text chunks
        """
        # Decide which documents to search in
        if filename and filename in self.documents:
            # Search only in the specified document
            chunks = self.documents[filename]
        else:
            # Search in all documents
            chunks = []
            for doc_chunks in self.documents.values():
                chunks.extend(doc_chunks)
        
        # Simple keyword matching
        # This is like the librarian looking for specific words in the books
        query_words = query.lower().split()  # Break the question into individual words
        scored_chunks = []  # List to store chunks with their relevance scores
        
        # Go through each chunk and see how relevant it is
        for chunk in chunks:
            chunk_lower = chunk.lower()  # Convert to lowercase for comparison
            
            # Count how many words from the query appear in this chunk
            # More matches = more relevant
            score = sum(1 for word in query_words if word in chunk_lower)
            
            # If this chunk has any matches, add it to our list
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by relevance (highest score first)
        # This is like the librarian putting the most relevant books on top
        scored_chunks.sort(reverse=True)
        
        # Return the top 3 most relevant chunks
        return [chunk for _, chunk in scored_chunks[:3]]

# =============================================================================
# CREATE OUR RAG SYSTEM INSTANCE
# =============================================================================

# Initialize RAG system - this creates our smart librarian
rag = SimpleRAG()

# =============================================================================
# API ENDPOINTS - These are the "doors" to our system
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    
    This is like a "ping" - it tells us if the server is running.
    When someone visits this URL, we respond with "I'm alive and working!"
    """
    return jsonify({"status": "ok", "message": "RAG Backend is running"})

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """
    Upload and process PDF file.
    
    This is like bringing a book to the librarian:
    1. Check if the book is valid (is it a PDF? Is it not too big?)
    2. Read the book and extract all the text
    3. Break it into searchable chunks
    4. File it away for later searching
    
    The frontend sends the PDF file here, and we process it.
    """
    try:
        # Check if a file was actually sent
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        # Get the file from the request
        file = request.files['file']
        
        # Check if a file was selected (not just an empty form)
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if it's a PDF file
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Check file size (5MB limit)
        # This prevents people from uploading huge files that would crash our server
        file.seek(0, 2)  # Move to the end of the file
        file_size = file.tell()  # Get the file size in bytes
        file.seek(0)  # Move back to the beginning
        
        # Convert 5MB to bytes and check if file is too big
        if file_size > 5 * 1024 * 1024:  # 5MB = 5 * 1024 * 1024 bytes
            return jsonify({
                "error": f"File too large. Maximum size is 5MB. Your file is {file_size / (1024*1024):.1f}MB"
            }), 413
        
        # Read PDF content
        # This is like opening the book and reading all the pages
        pdf_content = file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        # This is like copying all the text from the book
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        # Check if we actually found any text
        if not text.strip():
            return jsonify({"error": "No text found in PDF"}), 400
        
        # Add the document to our RAG system
        # This is like giving the book to the librarian to file away
        chunks_added = rag.add_document(file.filename, text)
        
        # Send back a success message with details
        return jsonify({
            "message": f"PDF '{file.filename}' uploaded successfully",
            "filename": file.filename,
            "chunks_added": chunks_added,
            "file_size_mb": f"{file_size / (1024*1024):.2f}MB"
        })
        
    except Exception as e:
        # If anything goes wrong, send back an error message
        return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500

@app.route('/api/rag-chat', methods=['POST'])
def rag_chat():
    """
    Chat with RAG system.
    
    This is like asking the librarian a question:
    1. Take the user's question
    2. Search through all the documents for relevant information
    3. Send the question + relevant information to the AI
    4. Get back an answer based on the specific documents
    
    This is the "magic" part - the AI can answer questions about YOUR specific documents!
    """
    try:
        # Get the user's message from the request
        data = request.get_json()
        user_message = data.get('user_message', '')
        
        # Check if they actually asked something
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Search for relevant documents
        # This is like asking the librarian "find me information about X"
        relevant_chunks = rag.search(user_message)
        
        # If no documents have been uploaded yet, tell the user
        if not relevant_chunks:
            return jsonify({
                "response": "No documents have been uploaded yet. Please upload a PDF first.",
                "source_documents": []
            })
        
        # Prepare context for the AI
        # This is like giving the AI the relevant book passages to read
        context = "\n\n".join(relevant_chunks)
        
        # Create messages for OpenAI
        # We're setting up a conversation with the AI:
        # 1. First, we tell it what to do (system message)
        # 2. Then we give it the relevant document content (context)
        # 3. Finally, we ask our question
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant. Answer questions based on the provided context. If the answer is not in the context, say so.\n\nContext:\n{context}"
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        # Get response from OpenAI
        # This is like asking a very smart person to read the relevant passages
        # and answer your question based on that information
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # The AI model to use
            messages=messages,      # The conversation we set up
            max_tokens=500,         # Limit response length
            temperature=0.7         # How creative vs. factual the response should be
        )
        
        # Extract the AI's response
        ai_response = response.choices[0].message.content
        
        # Send back the answer along with which documents were used
        return jsonify({
            "response": ai_response,
            "source_documents": relevant_chunks  # Show which parts of documents were used
        })
        
    except Exception as e:
        # If anything goes wrong, send back an error message
        return jsonify({"error": f"Error during chat: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def regular_chat():
    """
    Regular chat without RAG.
    
    This is like talking to a regular AI assistant without any specific documents.
    It can answer general questions but can't use your uploaded documents.
    """
    try:
        # Get the user's message
        data = request.get_json()
        user_message = data.get('user_message', '')
        
        # Check if they actually asked something
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Create messages for OpenAI
        # This is a simple conversation without any document context
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        # Get response from OpenAI
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract and return the response
        ai_response = response.choices[0].message.content
        return jsonify({"response": ai_response})
        
    except Exception as e:
        # If anything goes wrong, send back an error message
        return jsonify({"error": f"Error during chat: {str(e)}"}), 500

# =============================================================================
# START THE SERVER
# =============================================================================

if __name__ == '__main__':
    """
    This is the "start button" for our server.
    When we run this file, it starts the web server and makes it available
    for the frontend to connect to.
    
    debug=True means it will restart automatically when we make changes
    host='0.0.0.0' means it accepts connections from any IP address
    port=5000 means it runs on port 5000 (like a specific door number)
    """
    app.run(debug=True, host='0.0.0.0', port=5000)