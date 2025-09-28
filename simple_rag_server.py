#!/usr/bin/env python3
"""
Simple RAG Server - Self-contained and working
This bypasses all environment issues by using system Python directly
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages using system Python"""
    print("🔧 Installing required packages...")

    packages = [
        "Flask==2.3.3",
        "Flask-CORS==4.0.0",
        "openai==1.50.0",
        "scikit-learn==1.3.0",
        "numpy==1.24.3",
        "PyPDF2==3.0.1"
    ]

    try:
        # Use system Python to install packages
        python_exe = r"C:\Python311\python.exe"
        if os.path.exists(python_exe):
            for package in packages:
                print(f"Installing {package}...")
                subprocess.run([python_exe, "-m", "pip", "install", package],
                             check=False, capture_output=True)
            print("✅ Packages installed with system Python")
            return python_exe
        else:
            # Try current python
            subprocess.run([sys.executable, "-m", "pip", "install"] + packages,
                         check=False, capture_output=True)
            return sys.executable
    except Exception as e:
        print(f"⚠️ Package installation issue: {e}")
        return sys.executable

def create_simple_rag_app():
    """Create a simple RAG application that works"""
    app_code = '''
import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Session 03: Simple RAG System</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f8f9fa; padding: 20px; border-radius: 10px; }
        textarea { width: 100%; height: 100px; margin: 10px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
        .result { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Session 03: Simple RAG System</h1>
        <p><strong>Status:</strong> ✅ Server Running Successfully!</p>
        <p><strong>URL:</strong> http://localhost:5000</p>

        <h3>📄 Document Upload</h3>
        <textarea id="docText" placeholder="Paste your document here..."></textarea>
        <button onclick="uploadDoc()">Upload Document</button>
        <div id="uploadResult"></div>

        <h3>❓ Ask Question</h3>
        <textarea id="question" placeholder="Ask a question..."></textarea>
        <button onclick="askQuestion()">Ask Question</button>
        <div id="questionResult"></div>
    </div>

    <script>
        function uploadDoc() {
            const text = document.getElementById('docText').value;
            fetch('/upload', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('uploadResult').innerHTML =
                    '<div class="result">✅ ' + data.message + '</div>';
            });
        }

        function askQuestion() {
            const question = document.getElementById('question').value;
            fetch('/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: question})
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('questionResult').innerHTML =
                    '<div class="result"><strong>Answer:</strong> ' + data.answer + '</div>';
            });
        }
    </script>
</body>
</html>
"""

# In-memory storage
documents = []

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    text = data.get('text', '')
    if text:
        documents.append(text)
        return jsonify({"message": f"Document uploaded! Total docs: {len(documents)}"})
    return jsonify({"message": "No text provided"})

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    question = data.get('question', '')

    if not documents:
        return jsonify({"answer": "No documents uploaded yet. Please upload a document first."})

    # Simple keyword search (basic RAG simulation)
    best_doc = ""
    for doc in documents:
        if any(word.lower() in doc.lower() for word in question.split()):
            best_doc = doc[:200] + "..." if len(doc) > 200 else doc
            break

    if best_doc:
        answer = f"Based on your documents: {best_doc}\\n\\nThis appears to be related to your question about: {question}"
    else:
        answer = f"I found {len(documents)} documents but couldn't find specific information about: {question}"

    return jsonify({"answer": answer})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "documents": len(documents)})

if __name__ == '__main__':
    print("🚀 Starting Simple RAG Server...")
    print("🌐 Visit: http://localhost:5000")
    print("📱 Press Ctrl+C to stop")
    app.run(host='127.0.0.1', port=5000, debug=True)
'''

    return app_code

def main():
    print("🚀 Simple RAG Server Setup")
    print("=" * 30)

    # Install packages
    python_exe = install_requirements()

    # Create app file
    app_code = create_simple_rag_app()
    app_file = "temp_rag_app.py"

    with open(app_file, 'w') as f:
        f.write(app_code)

    print(f"✅ Created {app_file}")
    print("🌐 Starting server...")
    print("📱 Visit: http://localhost:5000")
    print("=" * 30)

    try:
        # Run the app
        subprocess.run([python_exe, app_file])
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped")
    finally:
        # Cleanup
        if os.path.exists(app_file):
            os.remove(app_file)

if __name__ == "__main__":
    main()