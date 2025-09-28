#!/usr/bin/env python3
"""
Session 04: Test Without Full RAG System
=======================================

This script tests the components without instantiating the full RAG system.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing imports...")
    
    try:
        # Test basic Python imports
        import json
        import asyncio
        import logging
        from datetime import datetime
        from typing import List, Dict, Any
        print("✅ Basic Python imports successful")
        
        # Test FastAPI imports
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        print("✅ FastAPI imports successful")
        
        # Test LangChain imports
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        print("✅ LangChain core imports successful")
        
        # Test LangChain OpenAI (without initialization)
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        print("✅ LangChain OpenAI imports successful")
        
        # Test LangChain Community
        from langchain_community.vectorstores import FAISS, Chroma
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        print("✅ LangChain Community imports successful")
        
        # Test LangGraph
        from langgraph.graph import StateGraph, END
        print("✅ LangGraph imports successful")
        
        # Test LangSmith
        from langsmith import Client
        print("✅ LangSmith imports successful")
        
        # Test ChromaDB
        import chromadb
        print("✅ ChromaDB import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config_class():
    """Test that configuration class can be instantiated."""
    print("\nTesting configuration class...")
    
    try:
        from langchain_rag_system import LangChainConfig
        
        # Create an instance
        config = LangChainConfig()
        print("✅ LangChainConfig class instantiated successfully")
        
        # Test basic attributes
        if hasattr(config, 'OPENAI_MODEL'):
            print("✅ OPENAI_MODEL attribute exists")
        if hasattr(config, 'EMBEDDING_MODEL'):
            print("✅ EMBEDDING_MODEL attribute exists")
        
        print(f"OpenAI API Key set: {bool(config.OPENAI_API_KEY)}")
        print(f"LangSmith API Key set: {bool(config.LANGSMITH_API_KEY)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Config class error: {e}")
        return False

def test_chromadb_functionality():
    """Test ChromaDB basic functionality."""
    print("\nTesting ChromaDB functionality...")
    
    try:
        import chromadb
        
        # Create a simple ChromaDB client
        client = chromadb.Client()
        print("✅ ChromaDB client created successfully")
        
        # Test creating a collection
        collection = client.create_collection("test_collection")
        print("✅ ChromaDB collection created successfully")
        
        # Test adding documents
        collection.add(
            documents=["This is a test document"],
            ids=["1"]
        )
        print("✅ ChromaDB document added successfully")
        
        # Test querying
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )
        print("✅ ChromaDB query successful")
        print(f"Query results: {len(results['documents'][0])} documents found")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB functionality error: {e}")
        return False

def test_fastapi_app():
    """Test that FastAPI app can be created."""
    print("\nTesting FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        
        app = FastAPI(title="Test RAG API")
        print("✅ FastAPI app created successfully")
        
        # Test adding a simple route
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}
        
        print("✅ FastAPI route added successfully")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'langchain_rag_system.py',
        'langgraph_deep_research.py',
        'langsmith_evaluation.py',
        'production_rag_system.py',
        'requirements.txt',
        'test_without_rag_system.py',
        'Dockerfile',
        'docker-compose.yml'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)
    
    return len(missing_files) == 0

def main():
    """Run all tests."""
    print("=" * 50)
    print("Session 04: Test Without Full RAG System")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_class,
        test_chromadb_functionality,
        test_fastapi_app,
        test_file_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Core functionality is working.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

