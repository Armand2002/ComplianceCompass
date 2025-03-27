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
from src.services.elasticsearch_init import ElasticsearchInit
from src.middleware.error_handler import register_exception_handlers

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

# Registra gli handler per le eccezioni
register_exception_handlers(app)

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
    
    # Inizializza Elasticsearch
    try:
        es_init = ElasticsearchInit()
        if es_init.connected:
            # Setup indici Elasticsearch
            es_init.setup_indices()
            logger.info("Elasticsearch inizializzato con successo.")
        else:
            logger.warning("Elasticsearch non disponibile. Funzionalità di ricerca avanzata disabilitate.")
    except Exception as e:
        logger.error(f"Errore nell'inizializzazione di Elasticsearch: {str(e)}")
    
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