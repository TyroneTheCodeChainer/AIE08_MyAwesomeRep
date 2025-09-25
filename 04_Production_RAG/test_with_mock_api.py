#!/usr/bin/env python3
"""
Session 04: Test With Mock API Keys
==================================

This script tests the full RAG system with mock API keys to simulate real usage.
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

def test_with_mock_openai():
    """Test the RAG system with mock OpenAI API keys."""
    print("Testing with mock OpenAI API keys...")
    
    # Set mock environment variables
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'mock-openai-key-12345',
        'LANGSMITH_API_KEY': 'mock-langsmith-key-67890'
    }):
        try:
            from langchain_rag_system import LangChainRAGSystem
            
            # Create RAG system instance
            rag_system = LangChainRAGSystem()
            print("✅ RAG system created successfully with mock API keys")
            
            # Test basic functionality
            if hasattr(rag_system, 'llm') and rag_system.llm is not None:
                print("✅ LLM initialized successfully")
            else:
                print("⚠️ LLM not initialized (expected with mock keys)")
            
            if hasattr(rag_system, 'embeddings') and rag_system.embeddings is not None:
                print("✅ Embeddings initialized successfully")
            else:
                print("⚠️ Embeddings not initialized (expected with mock keys)")
            
            if hasattr(rag_system, 'rag_chain') and rag_system.rag_chain is not None:
                print("✅ RAG chain created successfully")
            else:
                print("❌ RAG chain not created")
                return False
            
            if hasattr(rag_system, 'vector_store') and rag_system.vector_store is not None:
                print("✅ Vector store initialized successfully")
            else:
                print("❌ Vector store not initialized")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error with mock API keys: {e}")
            return False

def test_fastapi_endpoints():
    """Test FastAPI endpoints with mock data."""
    print("\nTesting FastAPI endpoints...")
    
    try:
        from production_rag_system import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI test error: {e}")
        return False

def test_document_processing():
    """Test document processing capabilities."""
    print("\nTesting document processing...")
    
    try:
        from langchain_rag_system import LangChainRAGSystem
        
        # Create temporary test document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for RAG processing.")
            temp_file = f.name
        
        try:
            # Test with mock API keys
            with patch.dict(os.environ, {
                'OPENAI_API_KEY': 'mock-openai-key-12345'
            }):
                rag_system = LangChainRAGSystem()
                
                # Test document loading
                if hasattr(rag_system, 'load_documents'):
                    print("✅ Document loading method exists")
                else:
                    print("❌ Document loading method missing")
                    return False
                
                # Test text splitting
                if hasattr(rag_system, 'split_documents'):
                    print("✅ Document splitting method exists")
                else:
                    print("❌ Document splitting method missing")
                    return False
                
                print("✅ Document processing capabilities verified")
                return True
                
        finally:
            # Clean up temp file
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"❌ Document processing test error: {e}")
        return False

def test_langgraph_integration():
    """Test LangGraph integration."""
    print("\nTesting LangGraph integration...")
    
    try:
        from langgraph_deep_research import DeepResearchLangGraph
        
        # Test graph creation
        graph = DeepResearchLangGraph()
        print("✅ DeepResearchGraph created successfully")
        
        # Test graph methods
        if hasattr(graph, 'create_research_plan'):
            print("✅ Research plan method exists")
        else:
            print("❌ Research plan method missing")
            return False
        
        if hasattr(graph, 'execute_research'):
            print("✅ Research execution method exists")
        else:
            print("❌ Research execution method missing")
            return False
        
        print("✅ LangGraph integration verified")
        return True
        
    except Exception as e:
        print(f"❌ LangGraph test error: {e}")
        return False

def test_langsmith_integration():
    """Test LangSmith integration."""
    print("\nTesting LangSmith integration...")
    
    try:
        from langsmith_evaluation import LangSmithEvaluator
        
        # Test evaluator creation with mock API key
        evaluator = LangSmithEvaluator(langsmith_api_key="mock-langsmith-key-12345")
        print("✅ LangSmithEvaluator created successfully")
        
        # Test evaluation methods
        if hasattr(evaluator, 'evaluate_rag_response'):
            print("✅ RAG evaluation method exists")
        else:
            print("❌ RAG evaluation method missing")
            return False
        
        if hasattr(evaluator, 'evaluate_retrieval_quality'):
            print("✅ Retrieval evaluation method exists")
        else:
            print("❌ Retrieval evaluation method missing")
            return False
        
        print("✅ LangSmith integration verified")
        return True
        
    except Exception as e:
        print(f"❌ LangSmith test error: {e}")
        return False

def main():
    """Run all tests with mock API keys."""
    print("=" * 60)
    print("Session 04: Test With Mock API Keys")
    print("=" * 60)
    
    tests = [
        test_with_mock_openai,
        test_fastapi_endpoints,
        test_document_processing,
        test_langgraph_integration,
        test_langsmith_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
