# 🔑 API Keys Setup Guide

## **Step 1: Get Your API Keys**

### **OpenAI API Key (Required)**
1. Go to https://platform.openai.com/api-keys
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Keep it secure** - don't share it publicly

### **LangSmith API Key (Optional but Recommended)**
1. Go to https://smith.langchain.com/
2. Sign up for a free account
3. Go to Settings > API Keys
4. Create a new API key
5. Copy the key

## **Step 2: Set Up Environment Files**

### **For Session 03 (End-to-End RAG)**
1. Copy `.env.example` to `.env` in the `03_End-to-End_RAG` folder
2. Replace `your_openai_api_key_here` with your actual OpenAI API key

### **For Session 04 (Production RAG)**
1. Copy `.env.example` to `.env` in the `04_Production_RAG` folder
2. Replace `your_openai_api_key_here` with your actual OpenAI API key
3. Replace `your_langsmith_api_key_here` with your LangSmith API key (optional)

## **Step 3: Test Your Setup**

### **Test Session 03**
```bash
cd 03_End-to-End_RAG
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

### **Test Session 04**
```bash
cd 04_Production_RAG
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

## **Step 4: Run Full Tests**

### **Session 03 Full Test**
```bash
cd 03_End-to-End_RAG
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from backend_enhanced import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/api/health')
print('Health check:', response.status_code)
"
```

### **Session 04 Full Test**
```bash
cd 04_Production_RAG
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from production_rag_system import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get('/api/health')
print('Health check:', response.status_code)
"
```

## **Step 5: Test Upload Functionality**

### **Session 03 Upload Test**
```bash
cd 03_End-to-End_RAG
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from backend_enhanced import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.post('/api/upload', files={'file': ('test.txt', 'test content', 'text/plain')})
print('Upload test:', response.status_code)
"
```

### **Session 04 Upload Test**
```bash
cd 04_Production_RAG
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from production_rag_system import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.post('/api/documents/upload', files={'file': ('test.txt', 'test content', 'text/plain')})
print('Upload test:', response.status_code)
"
```

## **Step 6: Test Chat Functionality**

### **Session 03 Chat Test**
```bash
cd 03_End-to-End_RAG
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from backend_enhanced import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.post('/api/chat', json={'user_message': 'Hello, how are you?'})
print('Chat test:', response.status_code)
if response.status_code == 200:
    print('Response:', response.json())
"
```

### **Session 04 Chat Test**
```bash
cd 04_Production_RAG
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from production_rag_system import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.post('/api/chat', json={'query': 'Hello, how are you?'})
print('Chat test:', response.status_code)
if response.status_code == 200:
    print('Response:', response.json())
"
```

## **Troubleshooting**

### **Common Issues:**
1. **"API key not found"** - Make sure you created `.env` files and added your API key
2. **"Invalid API key"** - Double-check your API key is correct
3. **"Rate limit exceeded"** - Wait a few minutes and try again
4. **"Module not found"** - Make sure you're in the correct directory

### **Success Indicators:**
- ✅ Health checks return 200
- ✅ Upload tests return 200
- ✅ Chat tests return 200 with actual responses
- ✅ No error messages about missing API keys

## **Next Steps:**
Once your API keys are working, you can:
1. **Deploy to production** (Vercel, Railway, etc.)
2. **Submit your homework** with working demos
3. **Showcase your AI systems** to potential employers

**Good luck! 🚀**


