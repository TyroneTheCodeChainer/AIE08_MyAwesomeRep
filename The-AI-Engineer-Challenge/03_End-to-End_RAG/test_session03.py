#!/usr/bin/env python3
"""
Session 03: Comprehensive Test Script
====================================

This script tests all the functionality of our RAG system to make sure
everything works correctly. It's like a quality control check for our code.

WHAT THIS SCRIPT TESTS:
1. Backend server can start and respond to health checks
2. PDF upload functionality works correctly
3. RAG chat can process questions and return answers
4. Regular chat works without document context
5. Error handling works for invalid inputs
6. File size validation works correctly

HOW TO USE:
1. Make sure your backend is running (python backend_enhanced.py)
2. Run this script: python test_session03.py
3. Check the results to see if everything passes

TECHNICAL DETAILS:
- Uses the 'requests' library to make HTTP calls to our backend
- Tests all API endpoints with various inputs
- Validates responses and error handling
- Provides detailed feedback on what works and what doesn't
"""

import requests
import json
import os
import sys
import time
from io import BytesIO

# =============================================================================
# CONFIGURATION - Settings for our tests
# =============================================================================

# Backend server URL - where our Flask server is running
BACKEND_URL = 'http://localhost:5000'

# Test PDF content - we'll create a simple PDF for testing
TEST_PDF_CONTENT = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World! This is a test PDF.) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""

# =============================================================================
# TEST FUNCTIONS - Individual tests for each feature
# =============================================================================

def test_backend_health():
    """
    Test 1: Backend Health Check
    
    This test makes sure our backend server is running and responding.
    It's like checking if the restaurant is open before trying to order food.
    """
    print("🔍 Testing backend health...")
    
    try:
        # Make a request to the health endpoint
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                print("✅ Backend is running and healthy")
                return True
            else:
                print("❌ Backend returned unexpected status")
                return False
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print("   Start it with: python backend_enhanced.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_pdf_upload():
    """
    Test 2: PDF Upload Functionality
    
    This test uploads a PDF file to our backend and checks if it's processed correctly.
    It's like testing if the librarian can properly file a new book.
    """
    print("🔍 Testing PDF upload...")
    
    try:
        # Create a test PDF file
        files = {'file': ('test.pdf', BytesIO(TEST_PDF_CONTENT), 'application/pdf')}
        
        # Upload the PDF
        response = requests.post(f"{BACKEND_URL}/api/upload-pdf", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'message' in data and 'chunks_added' in data:
                print(f"✅ PDF uploaded successfully: {data['message']}")
                print(f"   Chunks created: {data['chunks_added']}")
                return True
            else:
                print("❌ PDF upload returned unexpected response")
                return False
        else:
            print(f"❌ PDF upload failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PDF upload error: {e}")
        return False

def test_rag_chat():
    """
    Test 3: RAG Chat Functionality
    
    This test asks a question about the uploaded document and checks if the AI
    can answer based on the document content. This is the core RAG functionality.
    """
    print("🔍 Testing RAG chat...")
    
    try:
        # Ask a question about the test document
        question = "What does the test PDF say?"
        
        response = requests.post(f"{BACKEND_URL}/api/rag-chat", 
                               json={'user_message': question},
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                print(f"✅ RAG chat successful")
                print(f"   Question: {question}")
                print(f"   Answer: {data['response']}")
                if 'source_documents' in data:
                    print(f"   Source documents used: {len(data['source_documents'])}")
                return True
            else:
                print("❌ RAG chat returned unexpected response")
                return False
        else:
            print(f"❌ RAG chat failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ RAG chat error: {e}")
        return False

def test_regular_chat():
    """
    Test 4: Regular Chat Functionality
    
    This test checks if regular chat (without document context) works.
    This is like testing if the AI can answer general questions.
    """
    print("🔍 Testing regular chat...")
    
    try:
        # Ask a general question
        question = "What is the capital of France?"
        
        response = requests.post(f"{BACKEND_URL}/api/chat", 
                               json={'user_message': question},
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                print(f"✅ Regular chat successful")
                print(f"   Question: {question}")
                print(f"   Answer: {data['response']}")
                return True
            else:
                print("❌ Regular chat returned unexpected response")
                return False
        else:
            print(f"❌ Regular chat failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Regular chat error: {e}")
        return False

def test_error_handling():
    """
    Test 5: Error Handling
    
    This test checks if our system handles errors gracefully.
    It's like testing if the restaurant can handle a customer who orders
    something that's not on the menu.
    """
    print("🔍 Testing error handling...")
    
    try:
        # Test 1: Upload a non-PDF file
        print("   Testing non-PDF upload...")
        files = {'file': ('test.txt', BytesIO(b'This is not a PDF'), 'text/plain')}
        response = requests.post(f"{BACKEND_URL}/api/upload-pdf", files=files, timeout=5)
        
        if response.status_code == 400:
            print("   ✅ Correctly rejected non-PDF file")
        else:
            print(f"   ❌ Should have rejected non-PDF file, got status: {response.status_code}")
            return False
        
        # Test 2: Send empty message to RAG chat
        print("   Testing empty message...")
        response = requests.post(f"{BACKEND_URL}/api/rag-chat", 
                               json={'user_message': ''},
                               timeout=5)
        
        if response.status_code == 400:
            print("   ✅ Correctly rejected empty message")
        else:
            print(f"   ❌ Should have rejected empty message, got status: {response.status_code}")
            return False
        
        print("✅ Error handling works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_file_size_validation():
    """
    Test 6: File Size Validation
    
    This test checks if our system properly rejects files that are too large.
    It's like testing if the restaurant can handle a customer who orders
    more food than they can possibly eat.
    """
    print("🔍 Testing file size validation...")
    
    try:
        # Create a large file (simulate 6MB file)
        large_content = b'A' * (6 * 1024 * 1024)  # 6MB of 'A' characters
        
        files = {'file': ('large.pdf', BytesIO(large_content), 'application/pdf')}
        
        response = requests.post(f"{BACKEND_URL}/api/upload-pdf", files=files, timeout=10)
        
        if response.status_code == 413:  # 413 = Payload Too Large
            print("✅ Correctly rejected oversized file")
            return True
        else:
            print(f"❌ Should have rejected oversized file, got status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ File size validation test failed: {e}")
        return False

# =============================================================================
# MAIN TEST RUNNER - Run all tests and report results
# =============================================================================

def run_all_tests():
    """
    Run all tests and provide a comprehensive report.
    This is like running a complete quality control check on our system.
    """
    print("🚀 Starting Session 03 Comprehensive Tests")
    print("=" * 50)
    
    # List of all tests to run
    tests = [
        ("Backend Health", test_backend_health),
        ("PDF Upload", test_pdf_upload),
        ("RAG Chat", test_rag_chat),
        ("Regular Chat", test_regular_chat),
        ("Error Handling", test_error_handling),
        ("File Size Validation", test_file_size_validation),
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
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your RAG system is working perfectly!")
        print("   You can now use it to upload PDFs and chat with them.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        print("   Make sure your backend is running and all dependencies are installed.")
    
    return passed == total

# =============================================================================
# RUN THE TESTS
# =============================================================================

if __name__ == '__main__':
    """
    This is the entry point for our test script.
    When you run this file, it will execute all the tests.
    """
    print("Session 03 RAG System - Comprehensive Test Suite")
    print("This will test all functionality of your RAG system.")
    print("Make sure your backend is running first!")
    print()
    
    # Check if requests library is available
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' library not found.")
        print("   Install it with: pip install requests")
        sys.exit(1)
    
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)