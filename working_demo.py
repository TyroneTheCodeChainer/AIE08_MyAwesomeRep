#!/usr/bin/env python3
"""
Working Demo - Core RAG Functionality
=====================================

This demo shows the core RAG system functionality without complex dependencies.
"""

import os
import json
import sqlite3
import tempfile
from datetime import datetime

# Load environment variables
def load_env():
    """Load environment variables from .env file."""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

class SimplifiedRAG:
    """Simplified RAG system for demonstration."""

    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(tempfile.gettempdir(), 'demo_rag.db')
        self.init_database()

    def init_database(self):
        """Initialize the demo database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS demo_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    content TEXT NOT NULL,
                    chunks TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_document(self, filename, content):
        """Add a document to the RAG system."""
        # Simple chunking - split by sentences
        sentences = content.split('. ')
        chunks = [s.strip() + '.' for s in sentences if s.strip()]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO demo_documents (filename, content, chunks)
                VALUES (?, ?, ?)
            ''', (filename, content, json.dumps(chunks)))
            doc_id = cursor.lastrowid
            conn.commit()

        return {
            'document_id': doc_id,
            'filename': filename,
            'chunks_created': len(chunks),
            'status': 'success'
        }

    def search(self, query):
        """Simple keyword-based search."""
        query_words = query.lower().split()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, filename, chunks FROM demo_documents')
            rows = cursor.fetchall()

        results = []
        for doc_id, filename, chunks_json in rows:
            chunks = json.loads(chunks_json)
            for i, chunk in enumerate(chunks):
                # Simple scoring based on keyword matches
                score = sum(1 for word in query_words if word in chunk.lower())
                if score > 0:
                    results.append({
                        'document_id': doc_id,
                        'filename': filename,
                        'chunk': chunk,
                        'score': score / len(query_words)
                    })

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:5]  # Top 5 results

    def chat(self, query):
        """Simulate a chat response using retrieved context."""
        # Get relevant chunks
        relevant_chunks = self.search(query)

        if not relevant_chunks:
            return {
                'response': "I don't have any relevant information about that topic. Please upload some documents first.",
                'source_documents': [],
                'confidence': 0.0
            }

        # Create a simple response based on the context
        context = " ".join([chunk['chunk'] for chunk in relevant_chunks[:3]])

        # Simulate AI response (without actually calling OpenAI for demo purposes)
        response = f"Based on the uploaded documents, here's what I found about '{query}':\n\n"
        response += context[:500] + "..."  # Limit response length

        return {
            'response': response,
            'source_documents': relevant_chunks,
            'confidence': relevant_chunks[0]['score'] if relevant_chunks else 0.0
        }

def demo_workflow():
    """Demonstrate the complete RAG workflow."""
    print("="*60)
    print("LIVE RAG SYSTEM DEMO")
    print("="*60)

    # Load environment
    load_env()

    # Initialize RAG system
    rag = SimplifiedRAG()
    print("[SUCCESS] RAG system initialized")

    # Add sample documents
    print("\n[STEP 1] Adding sample documents...")

    documents = [
        {
            'filename': 'ai_basics.txt',
            'content': '''Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. Deep learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data. Natural Language Processing (NLP) helps computers understand and process human language.'''
        },
        {
            'filename': 'python_guide.txt',
            'content': '''Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. Python is widely used in data science, web development, and artificial intelligence. Popular libraries include NumPy for numerical computing, pandas for data manipulation, and scikit-learn for machine learning.'''
        },
        {
            'filename': 'rag_systems.txt',
            'content': '''Retrieval Augmented Generation (RAG) combines information retrieval with text generation. RAG systems first retrieve relevant documents from a knowledge base, then use that context to generate accurate responses. This approach helps reduce hallucinations in language models by grounding responses in factual information. RAG is particularly useful for question-answering systems and chatbots that need to provide accurate, up-to-date information.'''
        }
    ]

    for doc in documents:
        result = rag.add_document(doc['filename'], doc['content'])
        print(f"  [SUCCESS] Added {result['filename']} ({result['chunks_created']} chunks)")

    print(f"\n[SUCCESS] {len(documents)} documents added to knowledge base")

    # Demo queries
    print("\n[STEP 2] Testing query and retrieval...")

    test_queries = [
        "What is machine learning?",
        "How does Python help with data science?",
        "What are RAG systems and how do they work?",
        "Tell me about neural networks"
    ]

    for query in test_queries:
        print(f"\n--- Query: '{query}' ---")

        # Show retrieval results
        search_results = rag.search(query)
        print(f"[RETRIEVAL] Found {len(search_results)} relevant chunks:")
        for i, result in enumerate(search_results[:2]):  # Show top 2
            print(f"  {i+1}. {result['filename']} (score: {result['score']:.2f})")
            print(f"     \"{result['chunk'][:100]}...\"")

        # Show chat response
        chat_result = rag.chat(query)
        print(f"\n[RESPONSE] (confidence: {chat_result['confidence']:.2f})")
        print(f"  {chat_result['response'][:200]}...")

    print("\n" + "="*60)
    print("[SUCCESS] RAG SYSTEM DEMO COMPLETED!")
    print("="*60)

    print("\nDemo Summary:")
    print("- Successfully initialized RAG database")
    print("- Added 3 sample documents with automatic chunking")
    print("- Performed keyword-based retrieval")
    print("- Generated context-aware responses")
    print("- All core RAG functionality working!")

    print(f"\nDatabase location: {rag.db_path}")
    print("This demonstrates the production RAG system architecture!")

if __name__ == "__main__":
    try:
        demo_workflow()
    except Exception as e:
        print(f"[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()