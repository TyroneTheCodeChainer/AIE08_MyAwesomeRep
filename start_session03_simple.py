#!/usr/bin/env python3
"""
Simple Session 03 Startup - Guaranteed to work
"""
import os
import sys

def main():
    print("🚀 Starting Session 03: End-to-End RAG System")
    print("=" * 50)

    # Change to session directory
    session_dir = os.path.join(os.getcwd(), "03_End-to-End_RAG")

    if not os.path.exists(session_dir):
        print("❌ 03_End-to-End_RAG directory not found")
        print(f"Current dir: {os.getcwd()}")
        return

    os.chdir(session_dir)
    print(f"📁 Working directory: {session_dir}")

    # Import and run Flask app directly
    try:
        import backend_enhanced
        app = backend_enhanced.app

        print("✅ Flask app loaded successfully")
        print("🌐 Starting server on http://localhost:5000")
        print("🌐 Also try: http://127.0.0.1:5000")
        print("📱 Press Ctrl+C to stop")
        print("=" * 50)

        # Start the server
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()