#!/usr/bin/env python3
"""
Simple Demo Launcher for Session 04 Production RAG System
"""

import os
import sys

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file."""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("[INFO] Loaded environment variables from .env file")
    else:
        print("[WARNING] No .env file found")

def main():
    print("="*50)
    print("Session 04 Production RAG System Demo")
    print("="*50)

    # Load environment variables
    load_env()

    # Check if we're in the right directory
    if not os.path.exists('session04_production_rag_system.py'):
        print("[ERROR] session04_production_rag_system.py not found!")
        print("Please run this script from the main AIE08_MyAwesomeRep directory")
        return False

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("[ERROR] OpenAI API key not configured")
        print("Please set OPENAI_API_KEY environment variable or update .env file")
        return False

    print("[SUCCESS] Environment looks good!")
    print("\nStarting Production RAG Server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server when ready")
    print("="*50)

    try:
        # Import and run the production system
        exec(open('session04_production_rag_system.py').read())
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    else:
        print("[SUCCESS] Demo completed!")
        sys.exit(0)