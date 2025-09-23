#!/usr/bin/env python3
"""
Session 03: RAG Backend Runner
=============================

Simple script to run the Flask backend with proper environment setup.
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print("🚀 Starting Session 03 RAG Backend...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key:")
        print("1. Create a .env file in this directory")
        print("2. Add: OPENAI_API_KEY=your_key_here")
        print("3. Or set it as an environment variable")
        sys.exit(1)
    
    print("✅ OpenAI API key found")
    print("✅ Starting Flask server on http://localhost:5000")
    print("✅ Open frontend.html in your browser to test")
    print("=" * 50)
    
    # Import and run the Flask app
    from backend import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
