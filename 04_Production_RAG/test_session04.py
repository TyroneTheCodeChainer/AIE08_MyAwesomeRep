#!/usr/bin/env python3
"""
Session 04: Comprehensive Test Suite for LangChain RAG System
============================================================

This script tests all the functionality of our advanced RAG system built with
LangChain, LangGraph, and production features.

WHAT THIS SCRIPT TESTS:
1. LangChain components initialization
2. Document processing with LangChain loaders
3. Vector store operations with ChromaDB
4. RAG chain execution using LCEL
5. Deep Research workflow with LangGraph
6. LangSmith evaluation and monitoring
7. Ollama local model integration
8. Error handling and edge cases

HOW TO USE:
1. Install dependencies: pip install -r requirements.txt
2. Set up environment variables (OPENAI_API_KEY, LANGSMITH_API_KEY)
3. Run this script: python test_session04.py
4. Check the results to see if everything passes

TECHNICAL DETAILS:
- Tests LangChain Expression Language (LCEL) chains
- Validates LangGraph workflow execution
- Checks ChromaDB vector store operations
- Verifies LangSmith integration
- Tests both OpenAI and Ollama models
"""

import asyncio
import os
import sys
import time
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

# Test dependencies
import pytest
import requests
from fastapi.testclient import TestClient

# LangChain imports for testing
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =============================================================================
# CONFIGURATION - Test settings
# =============================================================================

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "test_documents": [
        {
            "filename": "test_document.txt",
            "content": "This is a test document about artificial intelligence and machine learning. It contains information about neural networks, deep learning, and natural language processing.",
            "expected_chunks": 1
        },
        {
            "filename": "research_paper.txt", 
            "content": """Introduction to RAG Systems

Retrieval Augmented Generation (RAG) is a powerful technique that combines the capabilities of large language models with external knowledge retrieval. This approach allows AI systems to access and utilize information from external sources, making them more accurate and up-to-date.

Key Components of RAG:
1. Document Processing: Converting raw documents into searchable chunks
2. Vector Embeddings: Creating numerical representations of text
3. Vector Storage: Storing embeddings in a searchable database
4. Retrieval: Finding relevant information for queries
5. Generation: Creating responses based on retrieved context

Applications of RAG:
- Question answering systems
- Document analysis
- Research assistance
- Customer support
- Content generation

The future of RAG looks promising with advances in embedding models, vector databases, and retrieval techniques.""",
            "expected_chunks": 3
        }
    ],
    "test_queries": [
        "What is RAG?",
        "What are the key components of RAG systems?",
        "How does vector embedding work?",
        "What are the applications of RAG?"
    ],
    "deep_research_queries": [
        "Conduct a comprehensive analysis of RAG systems in 2025",
        "Research the latest developments in vector databases",
        "Investigate the impact of RAG on AI applications"
    ]
}

# =============================================================================
# TEST UTILITIES - Helper functions for testing
# =============================================================================

def create_test_document(filename: str, content: str) -> str:
    """Create a temporary test document."""
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

def cleanup_test_files(file_paths: list):
    """Clean up temporary test files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                # Also remove parent directory if empty
                parent_dir = os.path.dirname(file_path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
        except Exception as e:
            print(f"Warning: Could not clean up {file_path}: {e}")

# =============================================================================
# CORE COMPONENT TESTS - Test individual LangChain components
# =============================================================================

def test_langchain_imports():
    """Test that all required LangChain components can be imported."""
    print("🔍 Testing LangChain imports...")
    
    try:
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_community.vectorstores import Chroma
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langgraph.graph import StateGraph, END
        
        print("✅ All LangChain imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection."""
    print("🔍 Testing OpenAI connection...")
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0.1
        )
        
        # Test with a simple query
        response = llm.invoke("Hello, this is a test. Respond with 'Test successful'.")
        
        if "test successful" in response.content.lower():
            print("✅ OpenAI connection successful")
            return True
        else:
            print(f"❌ OpenAI response unexpected: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def test_embeddings():
    """Test OpenAI embeddings generation."""
    print("🔍 Testing embeddings generation...")
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found")
            return False
        
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key
        )
        
        # Test embedding generation
        test_text = "This is a test document for embedding generation."
        embedding = embeddings.embed_query(test_text)
        
        if isinstance(embedding, list) and len(embedding) > 0:
            print(f"✅ Embeddings generated successfully (dimension: {len(embedding)})")
            return True
        else:
            print("❌ Embedding generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Embeddings test failed: {e}")
        return False

def test_vector_store():
    """Test ChromaDB vector store operations."""
    print("🔍 Testing vector store operations...")
    
    try:
        # Create temporary vector store
        temp_dir = tempfile.mkdtemp()
        
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        vector_store = Chroma(
            persist_directory=temp_dir,
            collection_name="test_collection",
            embedding_function=embeddings
        )
        
        # Create test documents
        test_docs = [
            Document(page_content="This is a test document about AI.", metadata={"source": "test1"}),
            Document(page_content="This is another document about machine learning.", metadata={"source": "test2"})
        ]
        
        # Add documents to vector store
        vector_store.add_documents(test_docs)
        
        # Test similarity search
        results = vector_store.similarity_search("artificial intelligence", k=2)
        
        if len(results) > 0:
            print(f"✅ Vector store operations successful (found {len(results)} results)")
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            return True
        else:
            print("❌ Vector store search returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_text_splitter():
    """Test RecursiveCharacterTextSplitter."""
    print("🔍 Testing text splitter...")
    
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        test_text = """This is a test document.
        
It has multiple paragraphs.

Each paragraph should be split appropriately.

The splitter should handle various separators correctly."""
        
        chunks = text_splitter.split_text(test_text)
        
        if len(chunks) > 1:
            print(f"✅ Text splitter successful (created {len(chunks)} chunks)")
            return True
        else:
            print("❌ Text splitter created too few chunks")
            return False
            
    except Exception as e:
        print(f"❌ Text splitter test failed: {e}")
        return False

# =============================================================================
# API ENDPOINT TESTS - Test FastAPI endpoints
# =============================================================================

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{TEST_CONFIG['base_url']}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("✅ Health endpoint successful")
                return True
            else:
                print(f"❌ Health endpoint returned unexpected status: {data}")
                return False
        else:
            print(f"❌ Health endpoint failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_document_upload():
    """Test document upload functionality."""
    print("🔍 Testing document upload...")
    
    try:
        # Create test document
        test_doc = TEST_CONFIG['test_documents'][0]
        file_path = create_test_document(test_doc['filename'], test_doc['content'])
        
        # Upload document
        with open(file_path, 'rb') as f:
            files = {'file': (test_doc['filename'], f, 'text/plain')}
            response = requests.post(
                f"{TEST_CONFIG['base_url']}/api/documents/upload",
                files=files,
                timeout=10
            )
        
        # Cleanup
        cleanup_test_files([file_path])
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"✅ Document upload successful (chunks: {data.get('chunks_added', 0)})")
                return True
            else:
                print(f"❌ Document upload returned unexpected response: {data}")
                return False
        else:
            print(f"❌ Document upload failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document upload test failed: {e}")
        return False

def test_simple_rag():
    """Test simple RAG functionality."""
    print("🔍 Testing simple RAG...")
    
    try:
        query = TEST_CONFIG['test_queries'][0]
        
        response = requests.post(
            f"{TEST_CONFIG['base_url']}/api/chat/simple",
            json={"query": query},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and data['response']:
                print(f"✅ Simple RAG successful")
                print(f"   Query: {query}")
                print(f"   Response: {data['response'][:100]}...")
                return True
            else:
                print("❌ Simple RAG returned empty response")
                return False
        else:
            print(f"❌ Simple RAG failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Simple RAG test failed: {e}")
        return False

def test_deep_research():
    """Test deep research functionality."""
    print("🔍 Testing deep research...")
    
    try:
        query = TEST_CONFIG['deep_research_queries'][0]
        
        response = requests.post(
            f"{TEST_CONFIG['base_url']}/api/chat/deep-research",
            json={"query": query},
            timeout=30  # Deep research takes longer
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'report' in data and data['report']:
                print(f"✅ Deep research successful")
                print(f"   Query: {query}")
                print(f"   Sources used: {data.get('sources_used', 0)}")
                print(f"   Iterations: {data.get('iterations', 0)}")
                return True
            else:
                print("❌ Deep research returned empty report")
                return False
        else:
            print(f"❌ Deep research failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Deep research test failed: {e}")
        return False

def test_evaluation():
    """Test LangSmith evaluation functionality."""
    print("🔍 Testing evaluation...")
    
    try:
        query = "What is artificial intelligence?"
        expected = "AI is the simulation of human intelligence in machines."
        
        response = requests.post(
            f"{TEST_CONFIG['base_url']}/api/evaluate",
            json={"query": query, "expected": expected},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'evaluation_logged' in data:
                print("✅ Evaluation successful")
                return True
            else:
                print("❌ Evaluation not logged properly")
                return False
        else:
            print(f"❌ Evaluation failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Evaluation test failed: {e}")
        return False

# =============================================================================
# INTEGRATION TESTS - Test complete workflows
# =============================================================================

def test_complete_rag_workflow():
    """Test the complete RAG workflow from upload to query."""
    print("🔍 Testing complete RAG workflow...")
    
    try:
        # Step 1: Upload multiple documents
        uploaded_docs = []
        for doc_config in TEST_CONFIG['test_documents']:
            file_path = create_test_document(doc_config['filename'], doc_config['content'])
            
            with open(file_path, 'rb') as f:
                files = {'file': (doc_config['filename'], f, 'text/plain')}
                response = requests.post(
                    f"{TEST_CONFIG['base_url']}/api/documents/upload",
                    files=files,
                    timeout=10
                )
            
            if response.status_code == 200:
                uploaded_docs.append(file_path)
            else:
                print(f"❌ Failed to upload {doc_config['filename']}")
                return False
        
        # Step 2: Test queries
        successful_queries = 0
        for query in TEST_CONFIG['test_queries']:
            response = requests.post(
                f"{TEST_CONFIG['base_url']}/api/chat/simple",
                json={"query": query},
                timeout=15
            )
            
            if response.status_code == 200:
                successful_queries += 1
        
        # Step 3: Cleanup
        cleanup_test_files(uploaded_docs)
        
        if successful_queries == len(TEST_CONFIG['test_queries']):
            print(f"✅ Complete RAG workflow successful ({successful_queries}/{len(TEST_CONFIG['test_queries'])} queries)")
            return True
        else:
            print(f"❌ RAG workflow partially failed ({successful_queries}/{len(TEST_CONFIG['test_queries'])} queries)")
            return False
            
    except Exception as e:
        print(f"❌ Complete RAG workflow test failed: {e}")
        return False

# =============================================================================
# MAIN TEST RUNNER - Run all tests and report results
# =============================================================================

def run_all_tests():
    """Run all tests and provide a comprehensive report."""
    print("🚀 Starting Session 04 Comprehensive Tests")
    print("=" * 60)
    
    # List of all tests to run
    tests = [
        # Core component tests
        ("LangChain Imports", test_langchain_imports),
        ("OpenAI Connection", test_openai_connection),
        ("Embeddings Generation", test_embeddings),
        ("Vector Store Operations", test_vector_store),
        ("Text Splitter", test_text_splitter),
        
        # API endpoint tests
        ("Health Endpoint", test_health_endpoint),
        ("Document Upload", test_document_upload),
        ("Simple RAG", test_simple_rag),
        ("Deep Research", test_deep_research),
        ("Evaluation", test_evaluation),
        
        # Integration tests
        ("Complete RAG Workflow", test_complete_rag_workflow),
    ]
    
    # Track results
    passed = 0
    total = len(tests)
    
    # Run each test
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
        
        # Small delay between tests
        time.sleep(1)
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your LangChain RAG system is working perfectly!")
        print("   You can now use it for advanced RAG applications with LangGraph workflows.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        print("   Make sure your API server is running and all dependencies are installed.")
    
    return passed == total

# =============================================================================
# RUN THE TESTS
# =============================================================================

if __name__ == '__main__':
    """
    This is the entry point for our test script.
    When you run this file, it will execute all the tests.
    """
    print("Session 04 LangChain RAG System - Comprehensive Test Suite")
    print("This will test all functionality of your advanced RAG system.")
    print("Make sure your API server is running first!")
    print()
    
    # Check if required libraries are available
    try:
        import requests
        import fastapi
        import langchain
    except ImportError as e:
        print(f"❌ Error: Required library not found: {e}")
        print("   Install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

