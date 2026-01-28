# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

### Frontend
- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

### Backend (RAG System)
- **Python FastAPI** - High-performance API server
- **Ollama** - Local LLM runtime
  - Llama 3.2 - Language model
  - mxbai-embed-large - Embeddings model
- **ChromaDB** - Vector database for semantic search
- **RAG Pipeline** - Document processing and retrieval

## 🚀 Running the Application

This app requires both a **frontend** and **backend** to run.

### Quick Start

1. **Install and setup Ollama:**
   ```bash
   # Download from https://ollama.ai
   
   # Pull models
   ollama pull llama3.2
   ollama pull mxbai-embed-large
   ```

2. **Setup backend:**
   ```bash
   cd backend
   # Run automated setup (Windows)
   setup.bat
   
   # Or manual setup
   pip install -r requirements.txt
   ```

3. **Start backend server:**
   ```bash
   cd backend
   # Easy start (Windows)
   start_backend.bat
   
   # Or manual start
   python -m uvicorn main:app --reload --port 8000
   ```

4. **Start frontend (in a new terminal):**
   ```bash
   npm run dev
   ```

5. **Access the application:**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Full Documentation

See [backend/README.md](backend/README.md) for detailed setup instructions, API documentation, and troubleshooting.


## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
