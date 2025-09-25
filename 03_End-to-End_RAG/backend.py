"""
Session 03: Clean RAG Backend
============================

A simple, working RAG backend using Flask that properly handles CORS.
This is built from scratch applying all lessons learned.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import PyPDF2
import io
import json
from openai import OpenAI
import tempfile

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes - this is the key fix!
CORS(app, origins="*", allow_headers="*", methods=["GET", "POST", "OPTIONS"])

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simple in-memory storage for documents
documents = {}

class SimpleRAG:
    """Simple RAG implementation that actually works."""
    
    def __init__(self):
        self.documents = {}
    
    def add_document(self, filename, text):
        """Add document to RAG system."""
        # Simple chunking - split by paragraphs
        chunks = text.split('\n\n')
        self.documents[filename] = [chunk.strip() for chunk in chunks if chunk.strip()]
        return len(self.documents[filename])
    
    def search(self, query, filename=None):
        """Simple keyword search."""
        if filename and filename in self.documents:
            chunks = self.documents[filename]
        else:
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
        
        # Return top 3 most relevant chunks
        scored_chunks.sort(reverse=True)
        return [chunk for _, chunk in scored_chunks[:3]]

# Initialize RAG system
rag = SimpleRAG()

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "RAG Backend is running"})

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload and process PDF file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Check file size (5MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({"error": f"File too large. Maximum size is 5MB. Your file is {file_size / (1024*1024):.1f}MB"}), 413
        
        # Read PDF content
        pdf_content = file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        # Extract text
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            return jsonify({"error": "No text found in PDF"}), 400
        
        # Add to RAG system
        chunks_added = rag.add_document(file.filename, text)
        
        return jsonify({
            "message": f"PDF '{file.filename}' uploaded successfully",
            "filename": file.filename,
            "chunks_added": chunks_added,
            "file_size_mb": f"{file_size / (1024*1024):.2f}MB"
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500

@app.route('/api/rag-chat', methods=['POST'])
def rag_chat():
    """Chat with RAG system."""
    try:
        data = request.get_json()
        user_message = data.get('user_message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Search for relevant documents
        relevant_chunks = rag.search(user_message)
        
        if not relevant_chunks:
            return jsonify({
                "response": "No documents have been uploaded yet. Please upload a PDF first.",
                "source_documents": []
            })
        
        # Prepare context
        context = "\n\n".join(relevant_chunks)
        
        # Create messages for OpenAI
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
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            "response": ai_response,
            "source_documents": relevant_chunks
        })
        
    except Exception as e:
        return jsonify({"error": f"Error during chat: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def regular_chat():
    """Regular chat without RAG."""
    try:
        data = request.get_json()
        user_message = data.get('user_message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Create messages for OpenAI
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
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({"response": ai_response})
        
    except Exception as e:
        return jsonify({"error": f"Error during chat: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
