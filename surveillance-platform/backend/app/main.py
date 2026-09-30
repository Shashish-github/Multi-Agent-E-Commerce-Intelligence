"""FastAPI application entry point."""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.core.redis import redis_manager
from backend.app.api.v1.router import api_router
from backend.app.auth.router import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    await redis_manager.connect()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await redis_manager.disconnect()
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Surveillance Platform API",
        description="Real-Time Multi-Object Surveillance and Anomalous Behavior Detection",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    # Routes
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(api_router, prefix="/api/v1", tags=["api"])

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


app = create_app()
