#!/usr/bin/env python3
"""
Simple FastAPI Server for Session 04 - Self-contained and working
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("🔧 Installing FastAPI packages...")

    packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-multipart==0.0.6",
        "openai==1.50.0",
        "scikit-learn==1.3.0",
        "numpy==1.24.3"
    ]

    try:
        python_exe = r"C:\Python311\python.exe"
        if os.path.exists(python_exe):
            for package in packages:
                print(f"Installing {package}...")
                subprocess.run([python_exe, "-m", "pip", "install", package],
                             check=False, capture_output=True)
            return python_exe
        else:
            subprocess.run([sys.executable, "-m", "pip", "install"] + packages,
                         check=False, capture_output=True)
            return sys.executable
    except Exception as e:
        print(f"⚠️ Package installation issue: {e}")
        return sys.executable

def create_simple_fastapi_app():
    """Create a simple FastAPI application"""
    app_code = '''
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Session 04: Simple Production RAG", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class DocumentUpload(BaseModel):
    text: str

class QueryRequest(BaseModel):
    question: str

# In-memory storage
documents = []

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Session 04: Production RAG</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            .section { margin: 25px 0; padding: 20px; border: 2px solid #e9ecef; border-radius: 10px; background: #f8f9fa; }
            textarea { width: 100%; height: 120px; margin: 10px 0; padding: 10px; border: 1px solid #ced4da; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            .result { background: #d4edda; padding: 15px; margin: 15px 0; border-left: 4px solid #28a745; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Session 04: Production RAG System</h1>
            <p><strong>Status:</strong> ✅ FastAPI Server Running!</p>
            <p><strong>URL:</strong> http://localhost:8000</p>
            <p><strong>API Docs:</strong> <a href="/docs">/docs</a></p>

            <div class="section">
                <h3>📄 Upload Document</h3>
                <textarea id="documentText" placeholder="Paste your document text here..."></textarea>
                <button onclick="uploadDocument()">Upload Document</button>
                <div id="uploadResult"></div>
            </div>

            <div class="section">
                <h3>❓ Ask Question</h3>
                <textarea id="questionText" placeholder="Ask a question about your documents..."></textarea>
                <button onclick="askQuestion()">Ask Question</button>
                <div id="questionResult"></div>
            </div>

            <div class="section">
                <h3>📊 System Status</h3>
                <button onclick="getStatus()">Check Status</button>
                <div id="statusResult"></div>
            </div>
        </div>

        <script>
            async function uploadDocument() {
                const text = document.getElementById('documentText').value;
                try {
                    const response = await fetch('/upload-document', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: text})
                    });
                    const result = await response.json();
                    document.getElementById('uploadResult').innerHTML =
                        `<div class="result">✅ ${result.message}</div>`;
                } catch (error) {
                    document.getElementById('uploadResult').innerHTML =
                        `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }

            async function askQuestion() {
                const question = document.getElementById('questionText').value;
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({question: question})
                    });
                    const result = await response.json();
                    document.getElementById('questionResult').innerHTML =
                        `<div class="result"><strong>Answer:</strong> ${result.answer}</div>`;
                } catch (error) {
                    document.getElementById('questionResult').innerHTML =
                        `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }

            async function getStatus() {
                try {
                    const response = await fetch('/status');
                    const result = await response.json();
                    document.getElementById('statusResult').innerHTML =
                        `<div class="result">
                            <strong>Documents:</strong> ${result.document_count}<br>
                            <strong>Status:</strong> ${result.status}
                        </div>`;
                } catch (error) {
                    document.getElementById('statusResult').innerHTML =
                        `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/upload-document")
async def upload_document(doc: DocumentUpload):
    documents.append(doc.text)
    return {"message": f"Document uploaded successfully! Total documents: {len(documents)}"}

@app.post("/query")
async def query_documents(query: QueryRequest):
    if not documents:
        return {"answer": "No documents uploaded yet. Please upload some documents first."}

    # Simple keyword search
    best_match = ""
    for doc in documents:
        if any(word.lower() in doc.lower() for word in query.question.split()):
            best_match = doc[:300] + "..." if len(doc) > 300 else doc
            break

    if best_match:
        answer = f"Based on your documents: {best_match}\\n\\nThis relates to your question: {query.question}"
    else:
        answer = f"I found {len(documents)} documents but couldn't find specific information about: {query.question}"

    return {"answer": answer}

@app.get("/status")
async def get_status():
    return {
        "status": "healthy",
        "document_count": len(documents),
        "service": "Session 04 Production RAG"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 Starting Session 04: Production RAG System")
    print("🌐 Visit: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📱 Press Ctrl+C to stop")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
'''

    return app_code

def main():
    print("🚀 Simple FastAPI Server Setup")
    print("=" * 35)

    # Install packages
    python_exe = install_requirements()

    # Create app file
    app_code = create_simple_fastapi_app()
    app_file = "temp_fastapi_app.py"

    with open(app_file, 'w') as f:
        f.write(app_code)

    print(f"✅ Created {app_file}")
    print("🌐 Starting FastAPI server...")
    print("📱 Visit: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 35)

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