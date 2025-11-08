# Banking Login & Security Helper

RAG-powered assistant for banking login and security questions using LangGraph and Chroma vector database.

## Features

- 🤖 **LangGraph Agent** - Stateful agent with conditional routing
- 📚 **RAG (Retrieval-Augmented Generation)** - PDF-based knowledge retrieval using Chroma
- 🔐 **Security-focused** - Specialized in login and security topics
- 📅 **Federal Holidays API** - Real-time holiday information
- 🎨 **Modern UI** - Next.js with shadcn/ui components
- 🐳 **Dockerized** - Complete containerized setup

## Quick Start

### Prerequisites

1. Copy `.env.example` to `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Using Docker (Recommended)

```bash
# Build and start services
docker-compose up --build

# Run PDF ingestion (first time only)
docker-compose exec backend python -m app.rag.ingestion
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

#### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system architecture, diagrams, and design decisions.

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── agent/        # LangGraph agent
│   │   │   ├── graph.py       # Agent workflow graph
│   │   │   ├── nodes.py       # Agent nodes (router, retriever, LLM)
│   │   │   ├── state.py       # Agent state schema
│   │   │   └── prompts.py     # System prompts
│   │   ├── rag/          # RAG components
│   │   │   ├── embeddings.py  # OpenAI embeddings
│   │   │   ├── ingestion.py   # PDF → Chroma pipeline
│   │   │   └── retriever.py   # Semantic search
│   │   ├── tools/        # Agent tools
│   │   │   └── holidays.py    # Federal holidays API
│   │   ├── config.py     # Settings
│   │   └── main.py       # API endpoints
│   ├── data/
│   │   ├── pdfs/         # Source PDF documents
│   │   └── vectorstore/  # Chroma vector database
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Next.js frontend
│   ├── app/
│   ├── components/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── instructions.md       # Project requirements
└── README.md
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Backend (required)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Tech Stack

### Frontend
- **Framework**: Next.js 15, React 19
- **UI**: TailwindCSS, shadcn/ui
- **Deployment**: Docker (standalone output)

### Backend
- **Framework**: FastAPI, Python 3.11
- **Agent**: LangGraph 0.2.60
- **LLM**: OpenAI GPT-4o-mini
- **Vector DB**: Chroma 0.5.23
- **Embeddings**: OpenAI text-embedding-3-small
- **PDF Processing**: PyPDF 5.1.0, RecursiveCharacterTextSplitter

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Data Persistence**: Volume mounts for vectorstore

## RAG Pipeline

### 1. Document Ingestion
```bash
# Place PDFs in backend/data/pdfs/
# Run ingestion
docker-compose exec backend python -m app.rag.ingestion
```

**Pipeline:**
- Loads PDFs from `data/pdfs/`
- Splits into chunks (1000 chars, 200 overlap)
- Creates embeddings (OpenAI text-embedding-3-small)
- Stores in Chroma vectorstore

### 2. Semantic Retrieval
- Top-k similarity search (k=3)
- Metadata extraction (source, page)
- Context formatting for LLM

### 3. LangGraph Agent Flow
```
User Question
    ↓
Router Node → Classify (login/security vs out-of-scope)
    ↓
Retriever Node → RAG: Fetch relevant docs from Chroma
    ↓
Holidays Node → (Optional) Call federal holidays API
    ↓
LLM Answer Node → Generate response with citations
    ↓
Response + Sources
```

## Implementation Status

- ✅ Frontend UI functional
- ✅ Backend API with FastAPI
- ✅ RAG implementation with Chroma
- ✅ LangGraph agent with conditional routing
- ✅ Vector DB integration (Chroma)
- ✅ PDF ingestion pipeline
- ✅ Keyword-based router
- ✅ Federal holidays API integration
- ✅ Citation tracking

## Development Commands

### Docker Operations
```bash
# Build and start services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# Restart specific service
docker-compose restart backend
```

### RAG Operations
```bash
# Run PDF ingestion
docker-compose exec backend python -m app.rag.ingestion

# Add new PDF (then re-run ingestion)
# 1. Place PDF in backend/data/pdfs/
# 2. Run ingestion command above

# Test RAG query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'
```

### Testing
```bash
# Health check
curl http://localhost:8000/health

# Test login/security question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a one-time passcode?"}'

# Test holidays API integration
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Is today a federal holiday?"}'

# View API docs
open http://localhost:8000/docs
```

## Example Questions

The agent is trained to answer login and security questions based on the PDF knowledge base:

- "How do I reset my password if I forgot it?"
- "What is a one-time passcode or OTP?"
- "What should I do if I get a security code I didn't request?"
- "How long does the password reset link last?"
- "What happens if I try to login from an unrecognized device?"
- "Is today a federal holiday?" (uses external API)

**Response includes:**
- Detailed answer based on RAG context
- Source citations (e.g., "Security Training.pdf (Page 3)")
- Response time in milliseconds
- Tool calls made (e.g., federal holidays API)

## Testing

### Run Automated Tests

```bash
# Install test dependencies (if running locally)
cd backend
pip install pytest pytest-asyncio

# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_api.py

# Run with verbose output
docker-compose exec backend pytest -v

# Run with coverage
docker-compose exec backend pytest --cov=app tests/
```

### Test Structure

```
backend/tests/
├── conftest.py       # Shared fixtures
├── test_api.py       # API endpoint tests
├── test_rag.py       # RAG component tests
└── test_agent.py     # LangGraph agent tests
```

## Evaluation

### Run Evaluation Script

The evaluation script tests the agent with 10 sample prompts from `instructions.md`:

```bash
# From host machine
cd backend
python eval.py

# From Docker container
docker-compose exec backend python eval.py
```

### Evaluation Metrics

The script measures:
- **Latency**: p50, p95, p99, mean, min, max
- **SLA Compliance**: p95 ≤ 5000ms requirement
- **Quality**: Citations per query, tool calls, answer length
- **Coverage**: All 10 sample prompts tested

### Sample Output

```
⏱️  Latency Statistics:
   • p50: 4200ms
   • p95: 4800ms (SLA: ≤5000ms)
   • p99: 5100ms
   • Mean: 4300ms

✅ p95 latency PASSES 5s SLA requirement

📚 Quality Metrics:
   • Total queries: 10
   • Total citations: 10
   • Avg citations/query: 1.0
   • Total tool calls: 1
   • Avg answer length: 320 chars
```

## Troubleshooting

### Vector database not found
```bash
# Run ingestion to create vectorstore
docker-compose exec backend python -m app.rag.ingestion
```

### Backend container restarting
```bash
# Check if OPENAI_API_KEY is set
cat .env

# View backend logs
docker-compose logs backend
```

### PDF not being ingested
```bash
# Ensure PDF is in correct directory
ls backend/data/pdfs/

# Check ingestion logs
docker-compose exec backend python -m app.rag.ingestion
```
