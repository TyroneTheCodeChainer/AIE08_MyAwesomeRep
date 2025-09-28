#!/usr/bin/env python3
"""
Quick test script to verify OpenAI API key is working
Run this locally to test your API key before deployment
"""

import os
from openai import OpenAI

def test_openai_api():
    """Test if OpenAI API key is working"""

    # Get API key from environment or prompt user
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("Enter your OpenAI API key: ").strip()

    if not api_key:
        print("❌ No API key provided")
        return False

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Test with a simple completion
        print("[TEST] Testing OpenAI API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ],
            max_tokens=10
        )

        result = response.choices[0].message.content.strip()
        print(f"[SUCCESS] API Response: {result}")

        # Test embeddings (used in RAG)
        print("[TEST] Testing embeddings...")
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input="This is a test sentence for embeddings."
        )

        embedding_length = len(embedding_response.data[0].embedding)
        print(f"[SUCCESS] Embedding generated: {embedding_length} dimensions")

        print("\n[SUCCESS] All tests passed! Your API key is working correctly.")
        print(f"[INFO] API Key format: {api_key[:7]}...{api_key[-4:]}")

        return True

    except Exception as e:
        print(f"[ERROR] API test failed: {str(e)}")
        print("\n[HELP] Troubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Check you have sufficient OpenAI credits")
        print("3. Ensure key has proper permissions")
        return False

if __name__ == "__main__":
    print("[INFO] OpenAI API Key Test")
    print("=" * 40)
    test_openai_api()