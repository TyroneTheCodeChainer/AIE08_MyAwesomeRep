#!/usr/bin/env python3
"""
Demo Launcher for Session 04 Production RAG System
=================================================

This script launches the production RAG system and provides demo instructions.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    print("[INFO] Checking requirements...")

    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'numpy', 'sqlite3'
    ]

    missing = []
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package}")

    if missing:
        print(f"\n⚠️  Missing packages: {missing}")
        print("Install with: pip install -r session04_requirements.txt")
        return False

    print("✅ All requirements satisfied!")
    return True

def check_api_key():
    """Check if OpenAI API key is configured."""
    print("\n🔑 Checking API key...")

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY environment variable or update .env file")
        return False

    print("✅ OpenAI API key configured!")
    return True

def start_server():
    """Start the production RAG server."""
    print("\n🚀 Starting Production RAG Server...")
    print("📍 Server will start at: http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("\n" + "="*50)

    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, 'session04_production_rag_system.py'
        ], cwd=Path.cwd())

        # Wait a moment for server to start
        time.sleep(3)

        print("🎉 Server should be running!")
        print("\nDemo URLs:")
        print("• Main API: http://localhost:8000")
        print("• Health Check: http://localhost:8000/api/health")
        print("• API Docs: http://localhost:8000/docs")
        print("• Interactive API: http://localhost:8000/redoc")

        # Open browser to API docs
        try:
            webbrowser.open('http://localhost:8000/docs')
            print("\n🌐 Opening API documentation in browser...")
        except:
            print("\n💡 Manually open http://localhost:8000/docs in your browser")

        print("\n" + "="*50)
        print("🎯 DEMO READY!")
        print("="*50)
        print("\nNext steps:")
        print("1. Upload a document via /api/documents/upload")
        print("2. Chat with your documents via /api/chat")
        print("3. Check health via /api/health")
        print("\nPress Ctrl+C to stop the server")

        # Keep the script running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

    return True

def main():
    """Main demo launcher."""
    print("🎬 Session 04 Production RAG Demo Launcher")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('session04_production_rag_system.py'):
        print("❌ session04_production_rag_system.py not found!")
        print("Please run this script from the main AIE08_MyAwesomeRep directory")
        return False

    # Run checks
    if not check_requirements():
        return False

    if not check_api_key():
        return False

    # Start the demo
    return start_server()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Demo launch failed. Check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Demo completed successfully!")
        sys.exit(0)