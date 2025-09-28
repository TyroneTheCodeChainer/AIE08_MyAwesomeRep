from fastapi import FastAPI
app = FastAPI()
@app.get('/api/health')
def health():
    return {'message': 'RAG Backend is running', 'status': 'ok'}
@app.get('/')
def root():
    return {'message': 'Session 03 RAG System', 'status': 'running'}