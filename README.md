# LLM Eval Pipeline

A production LLM evaluation and self-healing pipeline that automatically detects hallucinations in RAG-based Q&A, routes to stronger models when quality drops, and logs every failure for review.

## Architecture

```
User uploads PDF/URL
    → Text extracted → Chunked → Embedded → Stored in ChromaDB

User asks a question
    → Hybrid search (dense + BM25) finds relevant chunks
    → GPT-4o-mini generates answer using those chunks
    → GPT-4o judges the answer (faithfulness, relevancy, precision)
    → If faithfulness < 0.7 → retry with GPT-4o
    → If still failing → flag for human review
    → Everything logged to SQLite + dashboard
```

### Key Features

- **RAG Pipeline** — Hybrid search combining vector similarity (ChromaDB) and keyword matching (BM25)
- **LLM-as-Judge** — GPT-4o automatically scores every response for faithfulness, relevancy, and context precision
- **Self-Healing** — Low-quality answers automatically retried with a stronger model before flagging for human review
- **Observability Dashboard** — React UI with score trends, model usage breakdown, cost tracking, and a human review queue
- **Langfuse Integration** — Optional trace logging for every LLM call (latency, tokens, cost)

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI (GPT-4o-mini generation, GPT-4o judge) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB (embedded) |
| Sparse Search | BM25 (rank-bm25) |
| Backend | FastAPI + SQLAlchemy + SQLite |
| Frontend | React + TypeScript + Tailwind + Recharts |
| Observability | Langfuse (optional) |
| Containerization | Docker + docker-compose |

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (reads .env)
│   ├── dependencies.py      # Dependency injection
│   ├── ingestion/           # PDF loader, web scraper, chunking
│   ├── vectorstore/         # ChromaDB + OpenAI embeddings
│   ├── rag/                 # Hybrid retriever, generation chain, query orchestrator
│   ├── evaluation/          # LLM-as-judge scoring
│   ├── healing/             # Self-healing strategy + review queue
│   ├── observability/       # Langfuse tracing (optional)
│   ├── api/                 # FastAPI route handlers
│   ├── db/                  # SQLAlchemy models + async SQLite
│   └── tests/               # Unit + integration tests
├── frontend/                # React dashboard (Vite + TypeScript)
├── scripts/                 # Seed data, batch evaluation
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── requirements.txt
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- An OpenAI API key

### 1. Clone and configure

```bash
git clone https://github.com/<your-username>/LLM-Eval.git
cd LLM-Eval
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Install dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 3. Run

**Terminal 1 — Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### 4. Use

1. Go to the **Query** tab
2. Upload a PDF or enter a URL to ingest documents
3. Ask questions about the ingested content
4. View eval scores, check the **Dashboard** for trends, and manage the **Review Queue**

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest` | Upload a PDF file |
| POST | `/ingest/url` | Ingest a web page |
| POST | `/query` | Ask a question (full pipeline) |
| GET | `/evaluations` | List eval results (filterable) |
| GET | `/review-queue` | List flagged items |
| PATCH | `/review-queue/{id}` | Resolve/dismiss a review item |
| GET | `/dashboard/stats` | Aggregated metrics for dashboard |
| GET | `/docs` | Swagger API documentation |

## Docker

```bash
# Copy and configure env
cp .env.example .env

# Start everything (backend, frontend, Langfuse)
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3001
- Langfuse: http://localhost:3000

## Configuration

All settings are in `.env` (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. Your OpenAI API key |
| `GENERATION_MODEL` | `gpt-4o-mini` | Model for answer generation |
| `JUDGE_MODEL` | `gpt-4o` | Model for evaluation scoring |
| `FAITHFULNESS_THRESHOLD` | `0.7` | Score below this triggers self-healing |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `LANGFUSE_PUBLIC_KEY` | — | Optional. Enables Langfuse tracing |
| `LANGFUSE_SECRET_KEY` | — | Optional. Enables Langfuse tracing |

## How Self-Healing Works

```
Query → GPT-4o-mini generates answer
         ↓
    GPT-4o judges (faithfulness score)
         ↓
    Score >= 0.7? → Accept ✓
         ↓ No
    Retry with GPT-4o (stronger model)
         ↓
    Score >= 0.7? → Accept ✓
         ↓ No
    Flag for human review ⚠
```

## License

MIT
