import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.redis_client import redis_manager
from app.api.health import router as health_router
from app.api.agents import router as agents_router
from app.api.chat import router as chat_router
from app.api.jobs import router as jobs_router
from app.api.mcp import router as mcp_router
from app.api.websocket import router as ws_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ats_engineering")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up ATS Engineering AI Backend...")
    await init_db()
    await redis_manager.connect()
    yield
    logger.info("Shutting down ATS Engineering AI Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Industrial AI Platform for Autodesk CAD Integration",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.export import router as export_router
from app.api.render import router as render_router
from app.api.websocket import router as ws_router

# Mount Routes
app.include_router(health_router)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(mcp_router, prefix=settings.API_V1_STR)
app.include_router(export_router, prefix=settings.API_V1_STR)
app.include_router(render_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)

import os
from fastapi.responses import FileResponse

@app.get("/download/autodesk-agent.zip")
async def download_agent_zip():
    zip_path = os.path.join(os.path.dirname(__file__), "..", "autodesk-agent.zip")
    if os.path.exists(zip_path):
        return FileResponse(zip_path, filename="autodesk-agent.zip", media_type="application/zip")
    return {"error": "Zip package not found"}

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "agent_download_url": "/download/autodesk-agent.zip"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
