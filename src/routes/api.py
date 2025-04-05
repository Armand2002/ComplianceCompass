# src/routes/api.py
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.routes import (
    auth_routes, 
    pattern_routes, 
    user_routes, 
    search_routes, 
    notification_routes, 
    chatbot_routes,
    health_routes
)
from src.middleware.auth_middleware import get_current_user
from src.config import settings

# Esempi per Swagger
example_privacy_pattern = {
    "id": 1,
    "title": "Transparent Privacy Policy",
    "description": "Make the privacy policy clear and accessible to users",
    "context": "When collecting personal data from users",
    "problem": "Users often don't understand privacy policies",
    "solution": "Create a clear, concise, and accessible privacy policy",
    "consequences": "Improved user trust and compliance with regulations",
    "strategy": "Inform",
    "mvc_component": "View",
    "created_at": "2025-01-01T12:00:00",
    "updated_at": "2025-01-01T12:00:00",
    "gdpr_articles": [
        {
            "id": 1,
            "number": "12",
            "title": "Transparent information"
        }
    ],
    "pbd_principles": [
        {
            "id": 1,
            "name": "Visibility and transparency",
            "description": "Keep operations visible and transparent"
        }
    ]
}

# Crea il router API principale con prefisso globale
api_router = APIRouter(prefix="/api")

# Includi sotto-router con priorità appropriate
api_router.include_router(auth_routes.router)

# Imposta esempi globali per la documentazione del router pattern_routes
api_router.include_router(
    pattern_routes.router,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": example_privacy_pattern
                }
            },
            "description": "Successful response"
        }
    }
)

api_router.include_router(user_routes.router)
api_router.include_router(search_routes.router)
api_router.include_router(notification_routes.router)
api_router.include_router(chatbot_routes.router)
api_router.include_router(health_routes.router)  # Nuovo router per health check

@api_router.get("/", include_in_schema=False)
async def api_root():
    """
    Endpoint radice dell'API che fornisce metadati e informazioni di base.
    Utile per discovery e verifica dell'API.
    """
    return JSONResponse({
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documentation": "/api/docs",
        "health": "/api/health",
        "api_prefix": "/api"
    })