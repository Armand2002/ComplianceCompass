# src/main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

from src.config import settings
from src.routes.api import api_router
from src.db.init_db import init_db

# Configurazione logger
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crea applicazione FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if not settings.ENVIRONMENT == "production" else None,
    redoc_url="/api/redoc" if not settings.ENVIRONMENT == "production" else None,
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware per logging delle richieste
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware per loggare le richieste in entrata e i tempi di risposta.
    """
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Process time: {process_time:.2f}ms"
    )
    
    return response

# Handler globale errori
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler globale per eccezioni non gestite.
    """
    logger.error(f"Eccezione non gestita: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Si è verificato un errore interno."}
    )

# Includi router API
app.include_router(api_router)

# Route principale
@app.get("/")
async def root():
    """
    Endpoint principale che fornisce informazioni sull'API.
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/api/docs",
        "api": "/api"
    }

# Inizializzazione app
@app.on_event("startup")
async def startup_event():
    """
    Evento di avvio dell'applicazione.
    
    Inizializza il database e altre risorse.
    """
    logger.info(f"Avvio applicazione {settings.APP_NAME} in ambiente {settings.ENVIRONMENT}")
    
    # Inizializza database
    init_db()
    
    logger.info("Applicazione avviata con successo")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento di spegnimento dell'applicazione.
    
    Chiude le connessioni e libera le risorse.
    """
    logger.info("Spegnimento applicazione")

# Esecuzione standalone
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )