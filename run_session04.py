#!/usr/bin/env python3
"""
Simple launcher for Session 04 Production RAG System
Run this from AIE08_MyAwesomeRep directory
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Session 04: Production RAG System")
    print("=" * 50)

    # Change to correct directory
    session04_dir = os.path.join(os.getcwd(), "04_Production_RAG")

    if not os.path.exists(session04_dir):
        print("❌ Error: 04_Production_RAG directory not found")
        print(f"Current directory: {os.getcwd()}")
        print("Make sure you're running this from AIE08_MyAwesomeRep")
        return

    backend_file = os.path.join(session04_dir, "langchain_rag_system.py")

    if not os.path.exists(backend_file):
        print("❌ Error: langchain_rag_system.py not found")
        return

    print(f"📁 Session 04 directory: {session04_dir}")
    print(f"📄 Backend file: {backend_file}")
    print("🌐 Server will start on: http://localhost:8000")
    print("   (Also try: http://127.0.0.1:8000)")
    print("   (API docs at: http://localhost:8000/docs)")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        # Change to the session directory and run
        os.chdir(session04_dir)
        subprocess.run([sys.executable, "langchain_rag_system.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()