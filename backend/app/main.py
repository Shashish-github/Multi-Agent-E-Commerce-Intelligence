"""
Autonomous Multi-Agent E-Commerce Intelligence Platform - FastAPI Main Application
"""
import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.seeder import seed_catalog_if_empty
from app.core.telemetry import logger, set_request_id
from app.core.errors import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables and seed catalog data
    logger.info("Initializing database schemas...")
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_catalog_if_empty(session)
    logger.info("Application startup completed successfully.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multi-Agent E-Commerce Intelligence Platform with Evidence-Aware Ranking and Explainable Recommendations",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    # Extract or generate correlation/request ID
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_id(req_id)
    request.state.request_id = req_id

    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Process-Time-Ms"] = str(duration_ms)
    return response


# Register Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV
    }
