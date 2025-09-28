"""
Session 03: End-to-End RAG System
Built on Session 2 foundations with Flask web interface

Course progression:
- Session 1: Prototyping and vibe check
- Session 2: Python RAG with embeddings and vector search
- Session 3: Web application with Flask
- Session 4: Production system with LangChain
"""

import os
import json
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import openai
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import PyPDF2
import io

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = None

def get_openai_client():
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Please set OPENAI_API_KEY environment variable")
        client = OpenAI(api_key=api_key)
    return client

# In-memory storage (building on Session 2 concepts)
document_store = {
    "documents": [],
    "embeddings": [],
    "metadata": []
}

class SimpleRAG:
    """Simple RAG implementation building on Session 2 foundations"""

    def __init__(self):
        self.embedding_model = "text-embedding-ada-002"

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI API"""
        try:
            client = get_openai_client()
            response = client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []

    def add_document(self, text: str, source: str = "upload"):
        """Add document to vector store"""
        if len(text.strip()) < 10:
            return False

        # Chunk text (simple sentence splitting)
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 500:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Generate embeddings for chunks
        for i, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk)
            if embedding:
                document_store["documents"].append(chunk)
                document_store["embeddings"].append(embedding)
                document_store["metadata"].append({
                    "source": source,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })

        return True

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant documents"""
        if not document_store["documents"]:
            return []

        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []

        # Calculate similarities
        similarities = cosine_similarity(
            [query_embedding],
            document_store["embeddings"]
        )[0]

        # Get top results
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.7:  # Similarity threshold
                results.append({
                    "content": document_store["documents"][idx],
                    "similarity": float(similarities[idx]),
                    "metadata": document_store["metadata"][idx]
                })

        return results

    def generate_answer(self, query: str, context_docs: List[Dict]) -> str:
        """Generate answer using retrieved context"""
        if not context_docs:
            return "I don't have relevant information to answer that question."

        # Prepare context
        context = "\n\n".join([doc["content"] for doc in context_docs])

        # Create prompt
        prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {query}

Answer:"""

        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"

# Initialize RAG system
rag_system = SimpleRAG()

# HTML Template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Session 03: RAG System</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        textarea { width: 100%; height: 100px; margin: 10px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
        .error { border-left-color: #dc3545; background: #f8d7da; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Session 03: End-to-End RAG System</h1>
        <p>Building on Session 2's Python RAG foundations with a web interface.</p>

        <div class="section">
            <h3>📄 Upload Document</h3>
            <form id="uploadForm">
                <textarea id="documentText" placeholder="Paste your document text here..."></textarea>
                <button type="button" onclick="uploadDocument()">Upload Document</button>
            </form>
            <div id="uploadResult"></div>
        </div>

        <div class="section">
            <h3>❓ Ask Question</h3>
            <form id="questionForm">
                <textarea id="questionText" placeholder="Ask a question about your documents..."></textarea>
                <button type="button" onclick="askQuestion()">Ask Question</button>
            </form>
            <div id="questionResult"></div>
        </div>

        <div class="section">
            <h3>📊 System Status</h3>
            <button type="button" onclick="getStatus()">Check Status</button>
            <div id="statusResult"></div>
        </div>
    </div>

    <script>
        async function uploadDocument() {
            const text = document.getElementById('documentText').value;
            if (!text.trim()) {
                showResult('uploadResult', 'Please enter some document text.', 'error');
                return;
            }

            try {
                const response = await fetch('/upload-document', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                });
                const result = await response.json();

                if (result.success) {
                    showResult('uploadResult', '✅ Document uploaded successfully!', 'success');
                    document.getElementById('documentText').value = '';
                } else {
                    showResult('uploadResult', '❌ ' + result.error, 'error');
                }
            } catch (error) {
                showResult('uploadResult', '❌ Error: ' + error.message, 'error');
            }
        }

        async function askQuestion() {
            const question = document.getElementById('questionText').value;
            if (!question.trim()) {
                showResult('questionResult', 'Please enter a question.', 'error');
                return;
            }

            showResult('questionResult', '🤔 Thinking...', 'info');

            try {
                const response = await fetch('/ask-question', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                const result = await response.json();

                if (result.success) {
                    let html = `<strong>Answer:</strong> ${result.answer}<br><br>`;
                    if (result.sources && result.sources.length > 0) {
                        html += '<strong>Sources:</strong><br>';
                        result.sources.forEach((source, i) => {
                            html += `<small>${i+1}. Similarity: ${(source.similarity * 100).toFixed(1)}% - ${source.content.substring(0, 100)}...</small><br>`;
                        });
                    }
                    showResult('questionResult', html, 'success');
                } else {
                    showResult('questionResult', '❌ ' + result.error, 'error');
                }
            } catch (error) {
                showResult('questionResult', '❌ Error: ' + error.message, 'error');
            }
        }

        async function getStatus() {
            try {
                const response = await fetch('/status');
                const result = await response.json();

                let html = `
                    <strong>Documents:</strong> ${result.document_count}<br>
                    <strong>Total chunks:</strong> ${result.chunk_count}<br>
                    <strong>OpenAI connected:</strong> ${result.openai_status ? '✅' : '❌'}<br>
                    <strong>System:</strong> ${result.status}
                `;
                showResult('statusResult', html, 'success');
            } catch (error) {
                showResult('statusResult', '❌ Error: ' + error.message, 'error');
            }
        }

        function showResult(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="result ${type === 'error' ? 'error' : ''}">${message}</div>`;
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload-document', methods=['POST'])
def upload_document():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({"success": False, "error": "No text provided"})

        if len(text) < 10:
            return jsonify({"success": False, "error": "Text too short (minimum 10 characters)"})

        success = rag_system.add_document(text, "web_upload")

        if success:
            return jsonify({"success": True, "message": "Document uploaded successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to process document"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/ask-question', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()

        if not question:
            return jsonify({"success": False, "error": "No question provided"})

        # Search for relevant documents
        relevant_docs = rag_system.search(question, top_k=3)

        # Generate answer
        answer = rag_system.generate_answer(question, relevant_docs)

        return jsonify({
            "success": True,
            "answer": answer,
            "sources": relevant_docs
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/status')
def status():
    try:
        # Test OpenAI connection
        openai_status = False
        try:
            get_openai_client()
            openai_status = True
        except:
            pass

        return jsonify({
            "status": "online",
            "document_count": len(set(doc["metadata"]["source"] for doc in [{"metadata": m} for m in document_store["metadata"]])) if document_store["metadata"] else 0,
            "chunk_count": len(document_store["documents"]),
            "openai_status": openai_status
        })

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "Session 03 RAG System"})

if __name__ == '__main__':
    print("🚀 Starting Session 03: End-to-End RAG System")
    print("📚 Built on Session 2 foundations")
    print("🌐 Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)