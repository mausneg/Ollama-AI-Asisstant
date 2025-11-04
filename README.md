# Ollama AI Assistant

<p align="center">
  <strong>A production-ready RAG-powered conversational AI assistant with document processing capabilities</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#usage">Usage</a>
</p>

---

## Overview

Ollama AI Assistant is a sophisticated conversational AI application that combines Retrieval Augmented Generation (RAG) with local language models powered by Ollama. It features a ChatGPT-like interface, document vectorization, and persistent chat history management.

### Interface Preview

<p align="center">
  <img src="assets/images/tampilan_awal.png" alt="Initial Interface" width="800"/>
  <br/>
  <em>Clean ChatGPT-inspired interface with sidebar session management</em>
</p>

<p align="center">
  <img src="assets/images/saat_upload_file.png" alt="File Upload" width="800"/>
  <br/>
  <em>Document upload and vectorization process</em>
</p>

<p align="center">
  <img src="assets/images/sample_qa.png" alt="Sample Q&A" width="800"/>
  <br/>
  <em>Sample conversation with RAG-powered responses</em>
</p>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Starting the Application](#starting-the-application)
  - [Chat Interface](#chat-interface)
  - [Document Upload](#document-upload)
  - [Managing Sessions](#managing-sessions)
- [Configuration](#configuration)
- [Technology Stack](#technology-stack)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

### Key Highlights

- **RAG-Powered**: Intelligent document retrieval with FAISS vector store
- **Multi-Session Chat**: Persistent conversation history with SQLite
- **Document Processing**: PDF parsing and vectorization with PyMuPDF
- **Local LLM**: Privacy-focused using Ollama's local inference
- **Modern UI**: ChatGPT-inspired interface built with Streamlit
- **Zero Cloud Costs**: Runs entirely on your local machine

## Features

| Feature | Description |
|---------|-------------|
| **RAG System** | Retrieval Augmented Generation with FAISS vector store |
| **Document Upload** | Support for PDF, TXT, MD, DOCX, PPTX, XLSX files |
| **Chat Sessions** | Multiple conversation threads with persistent history |
| **Context Management** | Intelligent context retrieval from uploaded documents |
| **Local LLM** | Powered by Ollama (llama3.2:3b) for privacy and speed |
| **Chat History** | SQLite-based conversation persistence |
| **Vector Store Cache** | Efficient document embedding storage and retrieval |
| **Clean UI** | Modern, minimalist interface inspired by ChatGPT |

## Architecture

### RAG Concept

### Vector Store Concept

<p align="center">
  <img src="assets/images/konsep_vecktor_store.png" alt="Vector Store Concept" width="700"/>
  <br/>
  <em>Document embedding and similarity search process</em>
</p>

<p align="center">
  <img src="assets/images/konsep_rag.png" alt="RAG Concept" width="700"/>
  <br/>
  <em>Retrieval Augmented Generation workflow</em>
</p>


### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐     │
│  │  Chat UI    │  │  File Upload │  │  Session Mgmt   │     │
│  └─────────────┘  └──────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Assistant Class                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │  RAG Chain   │  │  Vector Store│  │  Chat History   │    │
│  └──────────────┘  └──────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Ollama     │    │    FAISS     │    │   SQLite     │
│   LLM API    │    │  Vector DB   │    │   Database   │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Data Flow

1. **User Input** → Streamlit interface captures question
2. **Context Retrieval** → FAISS searches relevant document chunks
3. **History Management** → SQLite loads conversation context
4. **LLM Processing** → Ollama generates response with RAG
5. **Response Display** → Streamed output to user interface

## Project Structure

```
Ollama-AI-Asisstant/
│
├── app.py                      # Main Streamlit application
│
├── utils/                      # Core utilities
│   ├── assistant.py            # RAG Assistant class
│   └── __pycache__/
│
├── vector_db/                  # FAISS vector store
│   └── index.faiss             # Document embeddings
│
├── chat_history.db             # SQLite conversation database
│
├── requirements.txt            # Python dependencies
│
├── .env                        # Environment configuration
│
└── README.md                   # This file
```

## Quick Start

### Prerequisites

| Requirement | Version | Description |
|-------------|---------|-------------|
| **Python** | 3.10+ | Programming language runtime |
| **Ollama** | Latest | Local LLM inference engine |
| **RAM** | 8GB+ | Recommended for model loading |

### Installation

**Step 1: Install Ollama**

Visit [Ollama's official website](https://ollama.ai) and install for your platform.

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# After installation, pull the model
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

**Step 2: Clone the Repository**
```bash
git clone https://github.com/mausneg/Ollama-AI-Asisstant.git
cd Ollama-AI-Asisstant
```

**Step 3: Create Virtual Environment**
```bash
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

**Step 4: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 5: Configure Environment (Optional)**

Create a `.env` file for debugging with LangSmith:
```bash
LANGCHAIN_API_KEY="your_api_key"
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_PROJECT="ollama-langchain"
```

Then add to your `utils/assistant.py`:
```python
from dotenv import load_dotenv

load_dotenv()
```

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Chat Interface

1. **New Conversation**: Click "New Chat" to start a fresh conversation
2. **Ask Questions**: Type your question in the chat input box
3. **View Response**: Watch the AI response stream in real-time
4. **Continue Chat**: Follow-up questions maintain conversation context

### Document Upload

**Step 1: Click the Attachment Button**
- Look for the 📎 icon near the chat input

**Step 2: Select Document**
- Supported formats: PDF, TXT, MD, DOCX, DOC, PPTX, PPT, XLSX, XLS
- Maximum size: 200MB per file

**Step 3: Wait for Processing**
- Document is parsed and split into chunks
- Embeddings are generated using Ollama
- Chunks are stored in FAISS vector store

**Step 4: Ask Questions**
- The AI can now answer questions about your document
- Context is automatically retrieved from vector store

### Managing Sessions

| Action | Description |
|--------|-------------|
| **New Chat** | Creates a new conversation session |
| **Switch Session** | Click on session title in sidebar |
| **Delete Session** | Click X button next to session |
| **Clear Cache** | Remove all vector store data |

### Clear Vector Store Cache

To reset all uploaded documents:
1. Click "Clear Cache" button in sidebar
2. Confirm the action
3. Vector store will be deleted and recreated on next upload

## Configuration

### Model Configuration

Edit `utils/assistant.py` to customize:

```python
class Assistant:
    def __init__(self, 
                 base_url="http://localhost:11434",
                 llm_model="llama3.2:3b",              # Change LLM model
                 embeddings_model="nomic-embed-text",  # Change embedding model
                 vector_db_path="vector_db",           # Vector store location
                 chat_history_db="sqlite:///chat_history.db"):  # Chat DB
```

### RAG Parameters

Adjust retrieval settings in `assistant.py`:

```python
def get_retriever(self):
    retriever = vector_store.as_retriever(
        search_type='similarity',
        search_kwargs={'k': 5, 'fetch_k': 10}  # Modify retrieval count
    )
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `k` | 5 | Number of documents to retrieve |
| `fetch_k` | 10 | Number of candidates to fetch |
| `chunk_size` | 1000 | Document chunk size |
| `chunk_overlap` | 100 | Overlap between chunks |

### Prompt Templates

Customize system prompts in `assistant.py`:

```python
self.system_prompt_with_context = SystemMessagePromptTemplate.from_template(
    "You are a helpful AI assistant who answers user questions based on the provided context from documents."
)
```

## Technology Stack

| Category | Technologies |
|----------|--------------|
| **Frontend** | Streamlit |
| **LLM** | Ollama (llama3.2:3b) |
| **Embeddings** | Ollama (nomic-embed-text) |
| **Vector Store** | FAISS (Facebook AI Similarity Search) |
| **Database** | SQLite |
| **Framework** | LangChain |
| **Document Processing** | PyMuPDF, python-docx, openpyxl |
| **Language** | Python 3.10+ |

### Key Dependencies

```
streamlit>=1.28.0          # Web interface
langchain>=0.3.0           # LLM framework
langchain-ollama>=0.2.0    # Ollama integration
faiss-cpu>=1.9.0           # Vector store
pymupdf>=1.24.0            # PDF processing
ollama>=0.4.0              # Ollama Python client
```

## Troubleshooting

<details>
<summary><b>Common Issues & Solutions</b></summary>

### Ollama Connection Error

**Error:**
```
ConnectionError: Could not connect to Ollama at http://localhost:11434
```

**Solutions:**
- Verify Ollama is running: `ollama list`
- Start Ollama service: `ollama serve`
- Check port availability: `netstat -tulpn | grep 11434`
- Ensure models are pulled: `ollama pull llama3.2:3b`

### Model Not Found

**Error:**
```
Error: model 'llama3.2:3b' not found
```

**Solutions:**
```bash
# Pull required models
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# Verify installation
ollama list
```

### Document Processing Fails

**Solutions:**
- Check file format is supported
- Verify file is not corrupted
- Ensure sufficient disk space for vector store
- Try with a smaller document first

### Vector Store Error

**Error:**
```
RuntimeError: FAISS index not found
```

**Solutions:**
- Click "Clear Cache" to reset vector store
- Ensure `vector_db` directory has write permissions
- Re-upload your documents
- Check disk space availability

### Slow Response Times

**Solutions:**
- Reduce `k` parameter in retriever (fewer documents)
- Use smaller LLM model: `ollama pull llama3.2:1b`
- Reduce chunk size in document processing
- Close other resource-intensive applications

### Session History Not Saving

**Solutions:**
- Check `chat_history.db` file permissions
- Verify SQLite database is not locked
- Restart the application
- Delete and recreate database file

</details>

### Debugging Commands

```bash
# Check Ollama status
ollama list

# Test Ollama API
curl http://localhost:11434/api/tags

# View running processes
ps aux | grep ollama

# Check Python environment
pip list | grep langchain

# Verify Streamlit installation
streamlit --version
```

## Advanced Features

### Custom Model Configuration

To use a different Ollama model:

1. Pull the desired model:
```bash
ollama pull mistral:7b
```

2. Update `assistant.py`:
```python
llm_model="mistral:7b"
```

### Batch Document Upload

For multiple documents, upload them one at a time. The vector store will accumulate all documents.

### Export Chat History

Access the SQLite database directly:
```bash
sqlite3 chat_history.db
SELECT * FROM message_store;
```

## Performance Optimization

### Memory Usage

- **8-bit quantization**: Already enabled in Ollama
- **Batch processing**: Documents processed sequentially
- **Cache management**: Use "Clear Cache" regularly

### Speed Improvements

- Use smaller models (1B instead of 3B)
- Reduce retrieval count (`k=3` instead of `k=5`)
- Optimize chunk size (500-1000 tokens)
- Close unused applications

## Security Considerations

- **Local Processing**: All data stays on your machine
- **No Cloud**: No external API calls (except Ollama)
- **Sensitive Data**: Safe for confidential documents
- **Database**: SQLite file is unencrypted by default

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** your changes: `git commit -m 'Add new feature'`
4. **Push** to the branch: `git push origin feature/your-feature`
5. **Open** a Pull Request

## Roadmap

- ✅ Document loader
- ✅ History message
- ✅ Vector store and RAG
- ⬜ Tool calling
- ⬜ Agents
- ⬜ Database utilities
- ⬜ Local deployment with Docker, Nginx and FastAPI
- ⬜ Deployment using AWS platforms (ECS, Lambda, S3)

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project builds upon excellent open-source work:

- [Ollama](https://ollama.ai) - Local LLM inference
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search
- [Streamlit](https://streamlit.io) - Web application framework
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF processing library

## Support

**Need help?**

- Open an issue on [GitHub Issues](https://github.com/mausneg/Ollama-AI-Asisstant/issues)
- Check the [Troubleshooting](#troubleshooting) section
- Review [Ollama Documentation](https://github.com/ollama/ollama)
- Join the [LangChain Discord](https://discord.gg/langchain)

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/mausneg">mausneg</a></sub>
</p>

<p align="center">
  <sub><strong>Note:</strong> This project is intended for educational and research purposes. Please ensure responsible AI usage and implement appropriate safety measures for production deployments.</sub>
</p>