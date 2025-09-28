#!/usr/bin/env python3
"""
Simple launcher for Session 03 RAG System
Run this from AIE08_MyAwesomeRep directory
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Session 03: End-to-End RAG System")
    print("=" * 50)

    # Change to correct directory
    session03_dir = os.path.join(os.getcwd(), "03_End-to-End_RAG")

    if not os.path.exists(session03_dir):
        print("❌ Error: 03_End-to-End_RAG directory not found")
        print(f"Current directory: {os.getcwd()}")
        print("Make sure you're running this from AIE08_MyAwesomeRep")
        return

    backend_file = os.path.join(session03_dir, "backend_enhanced.py")

    if not os.path.exists(backend_file):
        print("❌ Error: backend_enhanced.py not found")
        return

    print(f"📁 Session 03 directory: {session03_dir}")
    print(f"📄 Backend file: {backend_file}")
    print("🌐 Server will start on: http://localhost:5000")
    print("   (Also try: http://127.0.0.1:5000)")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        # Change to the session directory and run
        os.chdir(session03_dir)
        subprocess.run([sys.executable, "backend_enhanced.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()