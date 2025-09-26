from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="Session 03 RAG System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, World! Session 03 RAG System is working!"}

# Health endpoint
@app.get("/api/health")
async def health():
    return {"message": "RAG Backend is running", "status": "ok"}

# Upload endpoint
@app.post("/api/upload-pdf")
async def upload_pdf():
    return {"message": "Upload endpoint - basic functionality", "status": "ok"}

# Chat endpoint
@app.post("/api/rag-chat")
async def rag_chat():
    return {"message": "Chat endpoint - basic functionality", "status": "ok"}

# Chat endpoint
@app.post("/api/chat")
async def chat():
    return {"message": "Chat endpoint - basic functionality", "status": "ok"}

# Required for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
