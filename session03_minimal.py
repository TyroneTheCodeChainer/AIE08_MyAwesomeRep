"""
Session 03: Ultra-Minimal RAG System for Vercel
===============================================
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Simple in-memory storage
documents = {}

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Session 03: End-to-End RAG</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; text-align: center; }
        .upload { margin: 20px 0; padding: 20px; border: 2px dashed #ccc; text-align: center; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .chat { margin-top: 20px; }
        .messages { height: 200px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
        input[type="text"] { width: 70%; padding: 8px; }
    </style>
</head>
<body>
    <h1>📚 Session 03: End-to-End RAG System</h1>

    <div class="upload">
        <p>🔄 Simple RAG Demo</p>
        <input type="file" id="fileInput" accept=".pdf">
        <button onclick="uploadFile()">Upload PDF</button>
    </div>

    <div id="status"></div>

    <div class="chat" style="display:none;" id="chatSection">
        <h3>💬 Chat</h3>
        <div class="messages" id="messages"></div>
        <input type="text" id="questionInput" placeholder="Ask a question...">
        <button onclick="askQuestion()">Send</button>
    </div>

    <script>
        let docId = null;

        function uploadFile() {
            const file = document.getElementById('fileInput').files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            document.getElementById('status').innerHTML = 'Processing...';

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    docId = data.document_id;
                    document.getElementById('status').innerHTML = 'Document uploaded!';
                    document.getElementById('chatSection').style.display = 'block';
                } else {
                    document.getElementById('status').innerHTML = 'Error: ' + data.error;
                }
            });
        }

        function askQuestion() {
            const question = document.getElementById('questionInput').value;
            if (!question || !docId) return;

            const messages = document.getElementById('messages');
            messages.innerHTML += '<div><strong>You:</strong> ' + question + '</div>';

            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: question, document_id: docId})
            })
            .then(response => response.json())
            .then(data => {
                messages.innerHTML += '<div><strong>AI:</strong> ' + data.answer + '</div>';
                messages.scrollTop = messages.scrollHeight;
            });

            document.getElementById('questionInput').value = '';
        }
    </script>
</body>
</html>"""

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file'})

        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'})

        # Simple mock processing
        doc_id = str(len(documents) + 1)
        documents[doc_id] = {
            'filename': file.filename,
            'content': 'Mock content from ' + file.filename
        }

        return jsonify({
            'success': True,
            'document_id': doc_id,
            'filename': file.filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat."""
    try:
        data = request.json
        question = data.get('question', '')
        doc_id = data.get('document_id', '')

        if not question:
            return jsonify({'success': False, 'error': 'No question'})

        if doc_id not in documents:
            return jsonify({'success': False, 'error': 'Document not found'})

        # Simple response (demo mode)
        answer = f"This is a demo response about your question: '{question}'. In a full implementation, this would use OpenAI to analyze the uploaded document '{documents[doc_id]['filename']}'."

        return jsonify({
            'success': True,
            'answer': answer
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'docs': len(documents)})

if __name__ == '__main__':
    app.run(debug=True)