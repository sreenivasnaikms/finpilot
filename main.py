"""FinPilot: Proactive Multi-Agent Financial Copilot.

Powered by Mesh API (https://api.meshapi.ai/v1)
Orchestrated via LangGraph StateGraph
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from finpilot.config import settings
from finpilot.database import init_db
from finpilot.api.routes import router as api_router
from finpilot.scheduler.digest_scheduler import get_digest_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("finpilot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler: initializes DB and background scheduler."""
    logger.info("Initializing FinPilot Database...")
    init_db()
    
    logger.info("Starting Proactive Digest Background Scheduler (APScheduler)...")
    scheduler = get_digest_scheduler()
    scheduler.start()
    
    yield
    
    logger.info("Shutting down FinPilot Background Scheduler...")
    scheduler.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Proactive Multi-Agent Financial Assistant powered by Mesh API and LangGraph.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount Static Assets & Frontend UI
static_dir = os.path.join(os.path.dirname(__file__), "finpilot", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(static_dir, "index.html"))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
