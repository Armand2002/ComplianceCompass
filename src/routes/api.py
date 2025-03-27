# src/routes/api.py
from fastapi import APIRouter

from src.routes import auth_routes, pattern_routes, user_routes, search_routes, notification_routes

# Crea il router API principale
api_router = APIRouter(prefix="/api")

# Includi sotto-router
api_router.include_router(auth_routes.router)
api_router.include_router(pattern_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(search_routes.router)
api_router.include_router(notification_routes.router)

@api_router.get("/health")
async def health_check():
    """
    Endpoint di health check.
    
    Utile per verificare che l'API sia operativa.
    """
    return {"status": "ok"}