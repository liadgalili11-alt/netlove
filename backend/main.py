"""
Netlove Backend - FastAPI Application

Entry point. Run with:
    uvicorn backend.main:app --reload --port 8000
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.storage.temp_store import init_store, get_store
from backend.routers import media, analysis, publish


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    init_store(
        upload_dir=settings.temp_upload_dir,
        ttl_seconds=settings.temp_file_ttl_seconds,
    )
    task = asyncio.create_task(_periodic_cleanup())
    yield
    task.cancel()


async def _periodic_cleanup():
    """Run expired temp file cleanup every 10 minutes."""
    while True:
        await asyncio.sleep(600)
        try:
            store = get_store()
            removed = store.cleanup_expired()
            if removed:
                print(f"[TempStore] Cleaned up {removed} expired file(s).")
        except Exception as e:
            print(f"[TempStore] Cleanup error: {e}")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Netlove API",
        description="AI-powered social media content generation and publishing for Netlove frames",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(media.router, prefix="/api/v1")
    app.include_router(analysis.router, prefix="/api/v1")
    app.include_router(publish.router, prefix="/api/v1")

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "Netlove API"}

    return app


app = create_app()
