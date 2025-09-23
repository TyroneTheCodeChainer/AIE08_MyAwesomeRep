# 🎬 Session 3: End-to-End RAG Application - Loom Video Script

## 📋 **Video Overview**
**Duration:** 5-6 minutes  
**Focus:** Full-stack RAG application with domain-specific customization  
**Target:** Sleep researchers, psychologists, and dream interpretation enthusiasts

---

## 🎯 **Opening (30 seconds)**

### **Script:**
"Hello! I'm Tyrone, and today I'm demonstrating my Session 3 assignment: an End-to-End RAG Application. This is a full-stack AI system that I've specifically customized for dream interpretation research. 

The application combines a FastAPI backend with a Next.js frontend, deployed on Vercel, and includes advanced RAG capabilities with PDF document processing. Let me show you how it works and how I've tailored it for sleep researchers and psychologists."

---

## 🚀 **Main Demonstration (4-5 minutes)**

### **1. Live Application Demo (2-3 minutes)**

#### **Navigate to the Application:**
"First, let me show you the deployed application. I'll navigate to the live URL:"

**🔗 URL to show:** `https://ai-vibe-project.vercel.app`

**Note:** If the RAG features don't appear, the user should:
1. Click the gear icon (⚙️) in the top right to open settings
2. Look for the "📚 Dream Research Mode" toggle
3. Enable it to see PDF upload functionality

#### **Script:**
"Here's the Dream Interpretation Assistant interface. Notice the dream-themed UI with the moon icon and purple gradient - this immediately signals to users that this is specialized for dream research."

#### **Settings Panel Demonstration:**
"Let me click the gear icon to show the settings panel. Here you can see:
- API key configuration for OpenAI
- Model selection (GPT-4, GPT-3.5, etc.)
- System message customization
- Most importantly, the RAG mode toggle

This toggle is crucial - it switches between regular AI chat and RAG-powered document analysis."

#### **PDF Upload and Processing:**
"Now let me demonstrate the RAG functionality. I'll upload a dream research paper - this could be a study on REM sleep patterns or dream symbolism. 

*[Upload a PDF file]*

Watch as the system processes the document, extracts text, creates embeddings, and stores them in the vector database. This is the core RAG functionality that makes the system intelligent about specific research content."

#### **RAG Chat Demonstration:**
"With RAG mode enabled, let me ask a question about the uploaded document: 'What are the main findings about dream symbolism in this research?' 

*[Ask question and show response]*

Notice how the AI provides specific, document-based answers rather than generic responses. This is the power of RAG - it grounds the AI's responses in actual research data."

#### **Regular Chat Mode:**
"Now let me toggle off RAG mode and ask for a general dream interpretation: 'I dreamed about flying over a city. What does this mean?'

*[Toggle RAG off and ask question]*

This shows the system's versatility - it can provide both research-based answers and general dream interpretation guidance."

### **2. Technical Implementation (1-2 minutes)**

#### **GitHub Repository Tour:**
"Let me show you the technical implementation. I'll navigate to my GitHub repository:"

**🔗 URL to show:** `https://github.com/TyroneTheCodeChainer/AIE08_MyAwesomeRep/tree/s03-assignment`

#### **Script:**
"Here's the complete codebase. Let me highlight the key components:

**Backend Structure (api/):**
- `app.py` - The main FastAPI application with RAG endpoints
- `app_educational.py` - A heavily commented educational version
- `requirements.txt` - Python dependencies
- `vercel.json` - Deployment configuration

**Frontend Structure (frontend/):**
- `pages/index.tsx` - Main React component with dream-themed UI
- `next.config.js` - API proxy configuration
- `package.json` - Frontend dependencies

**Key Features:**
- PDF upload and processing with PyPDF2
- Vector database integration for semantic search
- Streaming responses for better user experience
- Domain-specific UI customization for dream research"

#### **Code Highlights:**
"Let me show you a few key code sections:

**RAG Implementation in app.py:**
```python
@app.post("/api/rag-chat")
async def rag_chat(request: RAGChatRequest):
    # Process user query with RAG
    response = rag_system.chat(request.message)
    return {"response": response}
```

**Dream-themed UI in index.tsx:**
```tsx
<div className="bg-gradient-to-br from-purple-900 to-indigo-900">
  <Moon className="w-8 h-8 text-yellow-300" />
  <h1>Dream Interpretation Assistant</h1>
</div>
```

This shows how I've customized both the functionality and the user interface for the specific domain."

---

## ✅ **Requirements Validation (30 seconds)**

### **Script:**
"Let me quickly validate that I've met all the assignment requirements:

**Activity #1 - RAG Functionality:**
✅ PDF upload and processing - demonstrated
✅ Document chunking and embedding - shown in processing
✅ Semantic search capabilities - proven with specific questions

**Activity #2 - Domain Customization:**
✅ Specific use-case (Dream Interpretation) - clear from UI and functionality
✅ Target user identification (sleep researchers, psychologists) - mentioned throughout
✅ UI customization for the domain - dream theme, moon icons, purple gradients

**Technical Requirements:**
✅ Branch development with MERGE.md file - shown in repository
✅ Vercel deployment working in production - live application demonstrated
✅ Full-stack implementation - FastAPI backend + Next.js frontend

**Advanced Build:**
✅ Enhanced system message for better responses
✅ Streaming responses for improved UX
✅ Error handling and user feedback"

---

## 🎯 **Closing (30 seconds)**

### **Script:**
"This Dream Interpretation Assistant demonstrates how to take a generic RAG system and make it truly valuable for a specific domain. By combining technical RAG capabilities with thoughtful UI design and user experience considerations, we've created a tool that sleep researchers and psychologists can actually use in their work.

The key learnings here are:
1. **Domain-specific customization** makes AI tools more valuable
2. **Full-stack development** enables real-world deployment
3. **User experience design** is crucial for adoption

Thank you for watching, and I'm excited to continue building more specialized AI applications in the next sessions!"

---

## 📝 **Production Notes**

### **Pre-Recording Checklist:**
- [ ] Ensure the deployed application is working
- [ ] Have a sample PDF ready for upload
- [ ] Test both RAG and regular chat modes
- [ ] Verify GitHub repository is accessible
- [ ] Check that all code examples are visible

### **Key URLs to Have Ready:**
- **Live Application:** `https://ai-vibe-project-hacpk6hba-tyrone-s-vercel.vercel.app`
- **GitHub Repository:** `https://github.com/TyroneTheCodeChainer/AIE08_MyAwesomeRep/tree/s03-assignment`
- **Backend Code:** `https://github.com/TyroneTheCodeChainer/AIE08_MyAwesomeRep/blob/s03-assignment/api/app.py`
- **Frontend Code:** `https://github.com/TyroneTheCodeChainer/AIE08_MyAwesomeRep/blob/s03-assignment/frontend/pages/index.tsx`

### **Backup Plans:**
- If live app is down, show local development version
- If GitHub is slow, have code screenshots ready
- If PDF upload fails, use a different sample document

---

## 🎬 **Recording Tips**

1. **Screen Recording:** Use full screen to show the application clearly
2. **Audio:** Speak clearly and at a moderate pace
3. **Transitions:** Use smooth transitions between sections
4. **Timing:** Keep each section within the allocated time
5. **Engagement:** Maintain enthusiasm and explain technical concepts clearly
