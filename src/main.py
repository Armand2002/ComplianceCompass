# src/main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.middleware.rate_limit import RateLimitMiddleware
from src.config import settings
from src.routes.api import api_router
from src.db.init_db import init_db
from src.services.elasticsearch_init import ElasticsearchInit
from src.middleware.error_handler import register_exception_handlers
from starlette.middleware import CSRFMiddleware
from src.logging_config import configure_logging

# Configura logging con impostazioni dall'environment
configure_logging(
    log_level='DEBUG' if settings.DEBUG else 'INFO',
    log_dir=settings.LOG_DIR if hasattr(settings, 'LOG_DIR') else None
)

logger = logging.getLogger(__name__)

# Configurazione rate limiter
limiter = Limiter(key_func=get_remote_address)

# Crea applicazione FastAPI
app = FastAPI(
    title="Compliance Compass API",
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if not settings.ENVIRONMENT == "production" else None,
    redoc_url="/api/redoc" if not settings.ENVIRONMENT == "production" else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configura CORS con supporto OPTIONS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# In src/main.py - Verificare che il middleware sia correttamente applicato
app.add_middleware(
    RateLimitMiddleware,
    limit=settings.RATE_LIMIT_DEFAULT,
    interval=60
)

app.add_middleware(
    CSRFMiddleware,
    secret=settings.SECRET_KEY,
    safe_methods=["GET", "HEAD", "OPTIONS"]
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