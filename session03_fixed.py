"""
Session 03: End-to-End RAG System - Vercel Compatible Version
===========================================================

Simplified version optimized for Vercel serverless deployment
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import io
import time
from datetime import datetime
import PyPDF2
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# In-memory storage (simplified for serverless)
documents = {}
document_chunks = {}

# Simplified HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Session 03: End-to-End RAG</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; border-radius: 8px; }
        .upload-area:hover { border-color: #007bff; background: #f8f9fa; }
        .chat-container { margin-top: 30px; }
        .chat-messages { height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; background: #fafafa; border-radius: 5px; margin-bottom: 15px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user-message { background: #007bff; color: white; text-align: right; }
        .ai-message { background: #e9ecef; color: #333; }
        .input-group { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        .status { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Session 03: End-to-End RAG System</h1>

        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" accept=".pdf" style="display: none;">
            <p>🔄 Click to upload PDF document or drag and drop</p>
            <small>Upload a PDF to start chatting with your document</small>
        </div>

        <div id="status"></div>

        <div class="chat-container" id="chatContainer" style="display: none;">
            <h3>💬 Chat with your document</h3>
            <div class="chat-messages" id="chatMessages"></div>
            <div class="input-group">
                <input type="text" id="questionInput" placeholder="Ask a question about the document..." onkeypress="if(event.key==='Enter') askQuestion()">
                <button id="askBtn" onclick="askQuestion()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let currentDocumentId = null;

        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) uploadDocument(file);
        });

        function uploadDocument(file) {
            const formData = new FormData();
            formData.append('file', file);

            showStatus('Uploading and processing document...', 'info');

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentDocumentId = data.document_id;
                    showStatus(`Document uploaded successfully! ${data.chunks_count} chunks created.`, 'success');
                    document.getElementById('chatContainer').style.display = 'block';
                    document.getElementById('questionInput').focus();
                } else {
                    showStatus(`Error: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showStatus(`Upload failed: ${error}`, 'error');
            });
        }

        function askQuestion() {
            const questionInput = document.getElementById('questionInput');
            const question = questionInput.value.trim();

            if (!question || !currentDocumentId) return;

            addMessage(question, 'user');
            questionInput.value = '';
            document.getElementById('askBtn').disabled = true;
            questionInput.disabled = true;

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question, document_id: currentDocumentId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addMessage(data.answer, 'ai');
                } else {
                    addMessage(`Error: ${data.error}`, 'ai');
                }
            })
            .catch(error => {
                addMessage(`Error: ${error}`, 'ai');
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

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
    </script>
</body>
</html>
"""

def extract_text_from_pdf(pdf_content):
    """Extract text from PDF bytes."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks."""
    chunks = []
    words = text.split()

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words)
        if chunk.strip():
            chunks.append(chunk.strip())

    return chunks

def search_relevant_chunks(question, document_id, max_chunks=3):
    """Simple keyword-based search for relevant chunks."""
    if document_id not in document_chunks:
        return []

    chunks = document_chunks[document_id]
    question_lower = question.lower()

    # Score chunks based on keyword overlap
    scored_chunks = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in question_lower.split() if word in chunk_lower)
        if score > 0:
            scored_chunks.append((chunk, score))

    # Sort by score and return top chunks
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in scored_chunks[:max_chunks]]

def generate_answer(question, relevant_chunks):
    """Generate answer using OpenAI."""
    if not client:
        return "OpenAI API key not configured. Please add your API key to use chat functionality."

    context = "\n\n".join(relevant_chunks)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Use only the information in the context to answer questions."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ],
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"

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

        # Extract text from PDF
        pdf_content = file.read()
        text = extract_text_from_pdf(pdf_content)

        if not text.strip():
            return jsonify({'success': False, 'error': 'No text found in PDF'})

        # Create chunks
        chunks = chunk_text(text)

        # Store document and chunks
        doc_id = str(int(time.time() * 1000))
        documents[doc_id] = {
            'filename': file.filename,
            'text': text,
            'upload_time': datetime.now().isoformat()
        }
        document_chunks[doc_id] = chunks

        return jsonify({
            'success': True,
            'document_id': doc_id,
            'filename': file.filename,
            'chunks_count': len(chunks)
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
                'answer': "I couldn't find relevant information in the document to answer your question."
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

# Export for Vercel (important!)
if __name__ == '__main__':
    app.run(debug=True)