#!/usr/bin/env python3
"""
Session 03: Basic Functionality Test
====================================

This script tests the basic functionality without requiring API keys or running servers.
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
        import io
        import tempfile
        print("✅ Basic Python imports successful")
        
        # Test Flask imports
        from flask import Flask
        from flask_cors import CORS
        print("✅ Flask imports successful")
        
        # Test PDF processing
        import PyPDF2
        print("✅ PyPDF2 import successful")
        
        # Test OpenAI import (without initialization)
        from openai import OpenAI
        print("✅ OpenAI import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_rag_class():
    """Test that the RAG class can be instantiated."""
    print("\nTesting RAG class instantiation...")
    
    try:
        # Import the RAG class
        from backend_enhanced import SimpleRAG
        
        # Create an instance
        rag = SimpleRAG()
        print("✅ SimpleRAG class instantiated successfully")
        
        # Test basic methods
        if hasattr(rag, 'add_document'):
            print("✅ add_document method exists")
        if hasattr(rag, 'search_documents'):
            print("✅ search_documents method exists")
        if hasattr(rag, 'get_answer'):
            print("✅ get_answer method exists")
            
        return True
        
    except Exception as e:
        print(f"❌ RAG class error: {e}")
        return False

def test_flask_app():
    """Test that Flask app can be created."""
    print("\nTesting Flask app creation...")
    
    try:
        from backend_enhanced import app
        
        # Test that app exists and is a Flask instance
        if hasattr(app, 'route'):
            print("✅ Flask app created successfully")
            return True
        else:
            print("❌ Flask app not properly initialized")
            return False
            
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'backend_enhanced.py',
        'frontend_enhanced.html',
        'requirements.txt',
        'test_basic_functionality.py'
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
    print("Session 03: Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_rag_class,
        test_flask_app,
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
        print("🎉 All tests passed! Basic functionality is working.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

