# Banking Login & Security Helper

RAG-powered assistant for banking login and security questions using LangGraph.

## Quick Start

### Using Docker (Recommended)

```bash
docker-compose up
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

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py       # API endpoints
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
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Tech Stack

- **Frontend**: Next.js 16, React 19, TailwindCSS, shadcn/ui
- **Backend**: FastAPI, Python 3.11
- **Future**: LangGraph, Vector DB (FAISS/Chroma), LLM Integration

## Status

- ✅ Frontend UI functional
- ✅ Backend API skeleton
- ⏳ RAG implementation (pending)
- ⏳ LangGraph agent (pending)
- ⏳ Vector DB integration (pending)

## Development Commands

```bash
# Build and start services
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```
