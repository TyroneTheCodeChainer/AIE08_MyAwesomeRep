# Session 03: Clean RAG System

A working RAG (Retrieval Augmented Generation) system built from scratch, applying all lessons learned from previous attempts.

## 🎯 What This Does

- **PDF Upload**: Upload PDF documents and extract text
- **RAG Chat**: Ask questions about uploaded documents using AI
- **Regular Chat**: Standard AI chat without document context
- **CORS Fixed**: Proper CORS handling that actually works

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file in this directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Backend

```bash
python run_backend.py
```

The backend will start on `http://localhost:5000`

### 4. Open the Frontend

Open `frontend.html` in your web browser.

## 🧪 Testing

1. **Health Check**: The page should show "✅ Backend connected successfully"
2. **Upload PDF**: Drag & drop a PDF file (max 5MB)
3. **RAG Chat**: Ask questions about the uploaded document
4. **Regular Chat**: Switch to regular chat mode

## 🔧 How It Works

### Backend (Flask)
- **Flask-CORS**: Handles CORS properly with `CORS(app, origins="*")`
- **Simple RAG**: Basic document chunking and keyword search
- **File Validation**: Checks file type and size (5MB limit)
- **Error Handling**: Proper error responses with CORS headers

### Frontend (HTML/JS)
- **Modern UI**: Clean, responsive design
- **Drag & Drop**: Easy file upload
- **Real-time Chat**: Instant messaging interface
- **Mode Toggle**: Switch between RAG and regular chat

## 📁 File Structure

```
03_End-to-End_RAG_Clean/
├── backend.py          # Flask backend with RAG functionality
├── frontend.html       # Complete frontend interface
├── run_backend.py      # Backend runner script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🐛 Troubleshooting

### Backend Won't Start
- Check that `OPENAI_API_KEY` is set in `.env` file
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### CORS Errors
- This implementation uses Flask-CORS which handles CORS properly
- If you still get CORS errors, check that the backend is running on `localhost:5000`

### File Upload Fails
- Check file size (max 5MB)
- Ensure file is a PDF
- Check browser console for error messages

## 🎓 Learning Points

1. **Flask-CORS**: Much simpler than FastAPI CORS configuration
2. **Local Development**: Easier to debug than cloud deployment
3. **Simple RAG**: Basic implementation that actually works
4. **File Validation**: Proper size and type checking
5. **Error Handling**: Clear error messages for users

## 🚀 Next Steps

This is a working foundation for Session 03. You can:
- Add more sophisticated RAG techniques
- Implement vector embeddings
- Add document persistence
- Deploy to cloud platforms
- Add more file format support

## 📝 Session 03 Requirements Met

- ✅ PDF upload functionality
- ✅ Document-based Q&A with RAG
- ✅ Complete end-to-end workflow
- ✅ Working frontend and backend
- ✅ Proper error handling
- ✅ CORS issues resolved
