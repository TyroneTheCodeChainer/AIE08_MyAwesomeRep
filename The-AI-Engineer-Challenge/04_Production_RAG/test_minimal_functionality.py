#!/usr/bin/env python3
"""
Session 04: Minimal Functionality Test
=====================================

This script tests the minimal functionality without requiring API keys or full RAG system.
It validates that the code can be imported and basic classes can be instantiated.
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
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        print("✅ LangChain Community imports successful")
        
        # Test LangGraph
        from langgraph.graph import StateGraph, END
        print("✅ LangGraph imports successful")
        
        # Test LangSmith
        from langsmith import Client
        print("✅ LangSmith imports successful")
        
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
            
        return True
        
    except Exception as e:
        print(f"❌ Config class error: {e}")
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
        'test_minimal_functionality.py',
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

def test_docker_config():
    """Test that Docker configuration files are valid."""
    print("\nTesting Docker configuration...")
    
    try:
        # Check Dockerfile exists and has basic content
        if os.path.exists('Dockerfile'):
            with open('Dockerfile', 'r') as f:
                content = f.read()
                if 'FROM python' in content and 'COPY requirements.txt' in content:
                    print("✅ Dockerfile has basic structure")
                else:
                    print("❌ Dockerfile missing basic structure")
                    return False
        else:
            print("❌ Dockerfile missing")
            return False
        
        # Check docker-compose.yml exists
        if os.path.exists('docker-compose.yml'):
            print("✅ docker-compose.yml exists")
        else:
            print("❌ docker-compose.yml missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Docker config error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Session 04: Minimal Functionality Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_class,
        test_fastapi_app,
        test_file_structure,
        test_docker_config
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
        print("🎉 All tests passed! Minimal functionality is working.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

