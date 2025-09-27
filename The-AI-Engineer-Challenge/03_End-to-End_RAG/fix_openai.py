#!/usr/bin/env python3
"""Fix OpenAI initialization in backend_enhanced.py"""

# Read the file
with open('backend_enhanced.py', 'r') as f:
    content = f.read()

# Replace the problematic line
old_line = 'openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))'
new_code = '''openai_client = None

def get_openai_client():
    """Get OpenAI client with lazy initialization."""
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        openai_client = OpenAI(api_key=api_key)
    return openai_client'''

# Replace the line
new_content = content.replace(old_line, new_code)

# Write the fixed file
with open('backend_enhanced.py', 'w') as f:
    f.write(new_content)

print("Fixed OpenAI initialization in backend_enhanced.py")

