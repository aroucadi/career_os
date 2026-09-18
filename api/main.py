"""
CareerOS API: Master FastAPI Application
=========================================
Production backend for CareerOS agentic decision engine, offering:
- Vercel AI SDK compatible Server-Sent Events (SSE) data streaming (/api/chat)
- Pipeline CRM REST management (/api/pipeline)
- Episodic Memory & Market Track Record REST endpoints (/api/memory)
- Health check & API documentation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import chat, pipeline, memory, documents, tokens, recruiter, candidates
from engine.storage.migrator import run_migrations

# Run automatic SQLite schema initialization & JSON state migration
run_migrations()

app = FastAPI(
    title="CareerOS Autonomous Decision Agent API",
    description="Backend API with Vercel AI SDK data streaming and multi-role agent harness.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Next.js dev server and Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Register routers
app.include_router(chat.router)
app.include_router(pipeline.router)
app.include_router(memory.router)
app.include_router(documents.router)
app.include_router(tokens.router)
app.include_router(recruiter.router)
app.include_router(recruiter.candidate_router)
app.include_router(candidates.router)

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for container orchestrators and monitoring."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "framework": "FastAPI",
        "streaming": "Vercel AI SDK Data Stream Protocol v1"
    }

@app.get("/api/system/logs", tags=["System"])
def get_audit_logs(limit: int = 50):
    """Retrieves recent structured audit interaction records."""
    from api.logger import AuditLogger
    return AuditLogger.get_recent_logs(limit=limit)

@app.get("/api/system/log-file", tags=["System"])
def get_raw_log_file(lines: int = 100):
    """Retrieves the tail of the rotating server log file."""
    from pathlib import Path
    log_file = Path("logs/careeros_api.log")
    if not log_file.exists():
        return {"lines": []}
    content = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"lines": content[-lines:]}

@app.get("/", tags=["System"])
def root():
    """Root landing endpoint with system status."""
    return {
        "name": "CareerOS Autonomous Agent API",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "logs": "/api/system/logs"
    }
