"""
Session 03: End-to-End RAG System for Vercel Deployment
======================================================

This is the main application file for Session 03 - End-to-End RAG system
that allows users to upload PDFs and chat with them.

Features:
- PDF upload and processing
- Text chunking and indexing
- Question-answering with RAG
- Flask-based web interface
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import io
import json
import time
from datetime import datetime
import PyPDF2
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load environment variables
def load_env():
    """Load environment variables from .env file if it exists."""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# In-memory storage for demo (in production, use a proper database)
documents = {}
document_chunks = {}

def extract_text_from_pdf(pdf_content):
    """Extract text from PDF content."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())

    return chunks

def search_relevant_chunks(query, doc_id, top_k=3):
    """Simple keyword-based search for relevant chunks."""
    if doc_id not in document_chunks:
        return []

    query_words = set(query.lower().split())
    chunks = document_chunks[doc_id]

    # Score chunks based on keyword overlap
    scored_chunks = []
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(query_words.intersection(chunk_words))
        if score > 0:
            scored_chunks.append((chunk, score))

    # Sort by score and return top_k
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in scored_chunks[:top_k]]

def generate_answer(query, context_chunks):
    """Generate answer using OpenAI with context."""
    if not client:
        return "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."

    context = "\n\n".join(context_chunks)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. If the answer is not in the context, say so clearly."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# HTML Template for the frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session 03: End-to-End RAG System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .upload-area {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #764ba2;
            background-color: #f8f9ff;
        }
        .upload-area.dragover {
            border-color: #764ba2;
            background-color: #f0f2ff;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .chat-container {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 8px;
            background-color: #fafafa;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background-color: #667eea;
            color: white;
            text-align: right;
        }
        .bot-message {
            background-color: white;
            border: 1px solid #ddd;
        }
        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .input-group input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        .status {
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }
        .status.success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .status.error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .status.info {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        .document-info {
            background-color: #e9f7fe;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Session 03: End-to-End RAG System</h1>
        <p>Upload a PDF document and chat with it using AI-powered retrieval</p>
    </div>

    <div class="container">
        <h2>📄 Document Upload</h2>
        <div class="upload-area" id="uploadArea">
            <p>📎 Drag and drop a PDF file here, or click to select</p>
            <input type="file" id="fileInput" accept=".pdf" style="display: none;">
            <button class="btn" onclick="document.getElementById('fileInput').click()">Choose PDF File</button>
        </div>

        <div id="status"></div>
        <div id="documentInfo" style="display: none;"></div>
    </div>

    <div class="container" id="chatContainer" style="display: none;">
        <h2>💬 Chat with Your Document</h2>
        <div class="chat-container" id="chatMessages"></div>
        <div class="input-group">
            <input type="text" id="questionInput" placeholder="Ask a question about your document..." onkeypress="handleKeyPress(event)">
            <button class="btn" onclick="askQuestion()" id="askBtn">Ask Question</button>
        </div>
    </div>

    <script>
        let currentDocumentId = null;

        // File upload handling
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                handleFileUpload(files[0]);
            } else {
                showStatus('Please upload a PDF file only.', 'error');
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });

        function handleFileUpload(file) {
            const formData = new FormData();
            formData.append('file', file);

            showStatus('Uploading and processing PDF...', 'info');

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentDocumentId = data.document_id;
                    showStatus('Document uploaded successfully!', 'success');
                    showDocumentInfo(data);
                    document.getElementById('chatContainer').style.display = 'block';
                } else {
                    showStatus('Error: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showStatus('Error uploading file: ' + error.message, 'error');
            });
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
        }

        function showDocumentInfo(data) {
            const infoDiv = document.getElementById('documentInfo');
            infoDiv.innerHTML = `
                <div class="document-info">
                    <h3>📋 Document Information</h3>
                    <p><strong>Filename:</strong> ${data.filename}</p>
                    <p><strong>Chunks created:</strong> ${data.chunks_count}</p>
                    <p><strong>Processing time:</strong> ${data.processing_time}ms</p>
                </div>
            `;
            infoDiv.style.display = 'block';
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                askQuestion();
            }
        }

        function askQuestion() {
            const questionInput = document.getElementById('questionInput');
            const question = questionInput.value.trim();

            if (!question) {
                showStatus('Please enter a question.', 'error');
                return;
            }

            if (!currentDocumentId) {
                showStatus('Please upload a document first.', 'error');
                return;
            }

            // Add user message to chat
            addMessage(question, 'user');
            questionInput.value = '';

            // Disable input while processing
            document.getElementById('askBtn').disabled = true;
            questionInput.disabled = true;

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    document_id: currentDocumentId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addMessage(data.answer, 'bot');
                } else {
                    addMessage('Error: ' + data.error, 'bot');
                }
            })
            .catch(error => {
                addMessage('Error: ' + error.message, 'bot');
            })
            .finally(() => {
                document.getElementById('askBtn').disabled = false;
                questionInput.disabled = false;
                questionInput.focus();
            });
        }

        function addMessage(message, sender) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = message;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle PDF upload and processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'})

        start_time = time.time()

        # Extract text from PDF
        pdf_content = file.read()
        text = extract_text_from_pdf(pdf_content)

        if not text.strip():
            return jsonify({'success': False, 'error': 'No text found in PDF'})

        # Create chunks
        chunks = chunk_text(text)

        # Store document and chunks
        doc_id = str(int(time.time() * 1000))  # Simple ID generation
        documents[doc_id] = {
            'filename': file.filename,
            'text': text,
            'upload_time': datetime.now().isoformat()
        }
        document_chunks[doc_id] = chunks

        processing_time = int((time.time() - start_time) * 1000)

        return jsonify({
            'success': True,
            'document_id': doc_id,
            'filename': file.filename,
            'chunks_count': len(chunks),
            'processing_time': processing_time
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat questions about uploaded documents."""
    try:
        data = request.json
        question = data.get('question', '').strip()
        document_id = data.get('document_id', '')

        if not question:
            return jsonify({'success': False, 'error': 'No question provided'})

        if not document_id or document_id not in documents:
            return jsonify({'success': False, 'error': 'Document not found'})

        # Search for relevant chunks
        relevant_chunks = search_relevant_chunks(question, document_id)

        if not relevant_chunks:
            return jsonify({
                'success': True,
                'answer': "I couldn't find relevant information in the document to answer your question. Please try rephrasing or asking about different topics covered in the document."
            })

        # Generate answer
        answer = generate_answer(question, relevant_chunks)

        return jsonify({
            'success': True,
            'answer': answer,
            'chunks_used': len(relevant_chunks)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'documents_loaded': len(documents),
        'openai_configured': OPENAI_API_KEY is not None
    })

# Export the app for Vercel
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)