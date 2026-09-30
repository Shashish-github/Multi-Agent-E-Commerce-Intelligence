"""
Main API v1 router.
"""
from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.investigations import router as investigations_router
from app.api.v1.products import router as products_router
from app.api.v1.comparisons import router as comparisons_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(investigations_router)
api_router.include_router(products_router)
api_router.include_router(comparisons_router)
