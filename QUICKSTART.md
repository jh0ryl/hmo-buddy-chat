# 🚀 Quick Start Guide - HMO Buddy Chat with RAG

This guide will get you up and running in **5 minutes**!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js & npm installed
- [ ] Ollama installed from https://ollama.ai

## Step-by-Step Setup

### 1️⃣ Install Ollama Models (2 minutes)

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
```

Verify installation:
```bash
ollama list
```

### 2️⃣ Setup Backend (1 minute)

**Option A: Automated (Windows)**
```bash
cd backend
setup.bat
```

**Option B: Manual**
```bash
cd backend
pip install -r requirements.txt
```

### 3️⃣ Start the Backend (30 seconds)

**Option A: Easy Start (Windows)**
```bash
cd backend
start_backend.bat
```

**Option B: Manual**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4️⃣ Test the Backend (30 seconds)

Open a browser and visit: http://localhost:8000/api/health

You should see:
```json
{
  "status": "healthy",
  "ollama_available": true,
  ...
}
```

### 5️⃣ Start the Frontend (30 seconds)

**In a NEW terminal:**
```bash
npm run dev
```

### 6️⃣ Start Chatting! 🎉

Visit: http://localhost:8080

Your local AI assistant is ready!

## Testing RAG (Optional)

Want to test the RAG system? Run the test script:

```bash
cd backend
python test_rag.py
```

This will:
- ✓ Check Ollama connection
- ✓ Process the sample document
- ✓ Test vector store
- ✓ Generate a RAG response

## Adding Your Own Documents

1. Place PDF, TXT, or MD files in `backend/documents/`
2. Upload via the API:

```bash
curl -X POST "http://localhost:8000/api/upload" -F "file=@your_document.pdf"
```

## Troubleshooting

### "Ollama not available"
- Make sure Ollama is running: `ollama serve`
- Check models: `ollama list`

### "Module not found"
```bash
cd backend
pip install -r requirements.txt
```

### Port already in use
Change port in `backend/main.py` or kill the process using port 8000.

## Next Steps

- 📖 Read full documentation: [backend/README.md](backend/README.md)
- 🔧 Integrate frontend with backend API
- 📄 Add your own HMO documents
- 🎨 Customize the chat interface

## Need Help?

Check the comprehensive guides:
- [Backend Documentation](backend/README.md)
- [Walkthrough](../.gemini/antigravity/brain/a01cf463-3dd7-40d1-aebe-642265040673/walkthrough.md)

---

**You're all set!** 🚀 Enjoy your local AI-powered HMO assistant!
