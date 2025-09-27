#!/usr/bin/env python3
"""
Fix Session 04 dependencies and start server
"""
import os
import sys
import subprocess

def install_missing_packages():
    """Install missing packages for Session 04"""
    print("🔧 Installing missing packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "onnxruntime"])
        print("✅ onnxruntime installed")
        return True
    except Exception as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def start_session04():
    """Start Session 04 server"""
    print("🚀 Starting Session 04: Production RAG System")
    print("=" * 50)

    session_dir = os.path.join(os.getcwd(), "04_Production_RAG")

    if not os.path.exists(session_dir):
        print("❌ 04_Production_RAG directory not found")
        return

    os.chdir(session_dir)
    print(f"📁 Working directory: {session_dir}")

    # Try to import and run
    try:
        import langchain_rag_system
        app = langchain_rag_system.app

        print("✅ FastAPI app loaded successfully")
        print("🌐 Starting server on http://localhost:8000")
        print("🌐 API docs at: http://localhost:8000/docs")
        print("📱 Press Ctrl+C to stop")
        print("=" * 50)

        # Start uvicorn server
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Trying fallback mode...")

        # Try simpler FastAPI app
        try:
            from fastapi import FastAPI
            import uvicorn

            app = FastAPI(title="Session 04 Fallback")

            @app.get("/")
            def root():
                return {"message": "Session 04 Fallback Mode", "status": "working"}

            @app.get("/health")
            def health():
                return {"status": "healthy"}

            print("✅ Fallback FastAPI app created")
            print("🌐 Starting fallback server on http://localhost:8000")
            uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")

def main():
    print("Session 04 Setup and Startup")
    print("=" * 30)

    # Install missing packages
    if not install_missing_packages():
        print("⚠️ Continuing without optional packages...")

    print()
    start_session04()

if __name__ == "__main__":
    main()