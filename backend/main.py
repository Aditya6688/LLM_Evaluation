import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.dashboard_router import router as dashboard_router
from backend.api.eval_router import router as eval_router
from backend.api.ingest_router import router as ingest_router
from backend.api.query_router import router as query_router
from backend.api.review_router import router as review_router
from backend.db.database import engine
from backend.db.models import Base
from backend.observability.langfuse_client import flush_langfuse, get_langfuse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize Langfuse (no-op if not configured)
    get_langfuse()

    logger.info("LLM Eval pipeline ready")
    yield

    # Shutdown
    flush_langfuse()
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title="LLM Eval Pipeline",
    description="Production LLM evaluation & self-healing pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(eval_router)
app.include_router(review_router)
app.include_router(dashboard_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
