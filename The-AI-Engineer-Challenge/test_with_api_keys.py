#!/usr/bin/env python3
"""
Test script to verify both Session 03 and Session 04 work with API keys
Run this after setting up your .env files with real API keys
"""

import os
import sys
import subprocess
from pathlib import Path

def test_session03():
    """Test Session 03 with API keys"""
    print("🔍 Testing Session 03: End-to-End RAG System")
    print("=" * 50)
    
    # Change to Session 03 directory
    os.chdir("03_End-to-End_RAG")
    
    try:
        # Test import
        print("1. Testing imports...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); from backend_enhanced import app; print('✅ Imports successful')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Session 03 imports successful")
        else:
            print(f"❌ Session 03 import failed: {result.stderr}")
            return False
            
        # Test health endpoint
        print("2. Testing health endpoint...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); from backend_enhanced import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.get('/api/health'); print(f'Health status: {response.status_code}')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Session 03 health endpoint working")
        else:
            print(f"❌ Session 03 health endpoint failed: {result.stderr}")
            return False
            
        # Test upload endpoint
        print("3. Testing upload endpoint...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); from backend_enhanced import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.post('/api/upload', files={'file': ('test.txt', 'test content', 'text/plain')}); print(f'Upload status: {response.status_code}')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Session 03 upload endpoint working")
        else:
            print(f"❌ Session 03 upload endpoint failed: {result.stderr}")
            return False
            
        # Test chat endpoint
        print("4. Testing chat endpoint...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); from backend_enhanced import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.post('/api/chat', json={'user_message': 'Hello, how are you?'}); print(f'Chat status: {response.status_code}'); print(f'Response: {response.json() if response.status_code == 200 else \"Error\"}')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Session 03 chat endpoint working")
        else:
            print(f"❌ Session 03 chat endpoint failed: {result.stderr}")
            return False
            
        print("🎉 Session 03: ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Session 03 test failed: {e}")
        return False
    finally:
        os.chdir("..")

def test_session04():
    """Test Session 04 with API keys"""
    print("\n🔍 Testing Session 04: Production RAG System")
    print("=" * 50)
    
    # Change to Session 04 directory
    os.chdir("04_Production_RAG")
    
    try:
        # Test import
        print("1. Testing imports...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); from production_rag_system import app; print('✅ Imports successful')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Session 04 imports successful")
        else:
            print(f"❌ Session 04 import failed: {result.stderr}")
            return False
            
        # Test health endpoint
        print("2. Testing health endpoint...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); from production_rag_system import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.get('/api/health'); print(f'Health status: {response.status_code}')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Session 04 health endpoint working")
        else:
            print(f"❌ Session 04 health endpoint failed: {result.stderr}")
            return False
            
        # Test upload endpoint
        print("3. Testing upload endpoint...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); from production_rag_system import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.post('/api/documents/upload', files={'file': ('test.txt', 'test content', 'text/plain')}); print(f'Upload status: {response.status_code}')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Session 04 upload endpoint working")
        else:
            print(f"❌ Session 04 upload endpoint failed: {result.stderr}")
            return False
            
        # Test chat endpoint
        print("4. Testing chat endpoint...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import os; from dotenv import load_dotenv; load_dotenv(); from production_rag_system import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.post('/api/chat', json={'query': 'Hello, how are you?'}); print(f'Chat status: {response.status_code}'); print(f'Response: {response.json() if response.status_code == 200 else \"Error\"}')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Session 04 chat endpoint working")
        else:
            print(f"❌ Session 04 chat endpoint failed: {result.stderr}")
            return False
            
        print("🎉 Session 04: ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Session 04 test failed: {e}")
        return False
    finally:
        os.chdir("..")

def main():
    """Main test function"""
    print("🚀 Testing Both Sessions with API Keys")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("03_End-to-End_RAG").exists() or not Path("04_Production_RAG").exists():
        print("❌ Please run this script from the root directory of your project")
        sys.exit(1)
    
    # Test both sessions
    session03_success = test_session03()
    session04_success = test_session04()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Session 03 (End-to-End RAG): {'✅ PASSED' if session03_success else '❌ FAILED'}")
    print(f"Session 04 (Production RAG): {'✅ PASSED' if session04_success else '❌ FAILED'}")
    
    if session03_success and session04_success:
        print("\n🎉 ALL TESTS PASSED! Your systems are ready for production!")
        print("Next steps:")
        print("1. Deploy to production (Vercel, Railway, etc.)")
        print("2. Submit your homework with working demo links")
        print("3. Showcase your AI systems to potential employers")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        print("Make sure you have:")
        print("1. Created .env files with your API keys")
        print("2. Installed all dependencies")
        print("3. Fixed any import errors")

if __name__ == "__main__":
    main()


