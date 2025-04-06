# src/main.py
import uvicorn
from fastapi import FastAPI, Request, Depends
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
from src.middleware.response_formatter import ResponseFormatterMiddleware
from src.middleware.logging_middleware import RequestLoggingMiddleware
from src.middleware.security import SecurityHeadersMiddleware, BruteForceProtectionMiddleware
from src.models.user_model import User
from src.auth.dependencies import get_current_admin_user

logger = logging.getLogger(__name__)

# Configurazione rate limiter
limiter = Limiter(key_func=get_remote_address)

# Crea applicazione FastAPI
app = FastAPI(
    title="Compliance Compass API",
    description="""
    # Compliance Compass API
    
    API per la piattaforma Compliance Compass che fornisce accesso a:
    
    * **Privacy Patterns**: Soluzioni riutilizzabili per implementare privacy nei sistemi
    * **Articoli GDPR**: Accesso dettagliato agli articoli del Regolamento GDPR
    * **Principi Privacy by Design**: Pattern correlati ai principi di Privacy by Design
    * **Fasi di Design ISO 9241-210**: Mappatura con standard di progettazione UX
    * **Vulnerabilità CWE**: Collegamento con vulnerabilità di sicurezza note
    * **Raccomandazioni OWASP**: Best practice di sicurezza applicativa
    
    ## Caratteristiche Principali
    
    - **Ricerca avanzata**: Ricerca full-text con filtri per articoli, principi e fasi
    - **Gestione utenti**: Autenticazione e autorizzazione granulare
    - **Notifiche**: Sistema di notifiche in tempo reale
    - **Chatbot**: Assistente virtuale integrato
    
    ## Sicurezza
    
    Tutte le richieste devono essere autenticate tramite token JWT ottenuti dalla rotta `/api/auth/login`.
    Token di refresh sono disponibili per mantenere la sessione senza richiedere nuovi login.
    
    Per problemi o assistenza, contattare il team di supporto.
    """,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if not settings.ENVIRONMENT == "production" else None,
    redoc_url="/api/redoc" if not settings.ENVIRONMENT == "production" else None,
    openapi_tags=[
        {
            "name": "autenticazione",
            "description": "Operazioni di autenticazione e gestione utenti"
        },
        {
            "name": "privacy-patterns",
            "description": "Operazioni sui Privacy Patterns"
        },
        {
            "name": "ricerca",
            "description": "Funzionalità di ricerca avanzata con filtri multidimensionali"
        },
        {
            "name": "notifiche",
            "description": "Gestione delle notifiche push e sottoscrizioni"
        },
        {
            "name": "chatbot",
            "description": "Interazione con l'assistente virtuale per domande su privacy e conformità"
        },
        {
            "name": "monitoraggio",
            "description": "Endpoint per health check e metriche del sistema"
        }
    ],
    openapi_url="/api/openapi.json",
    contact={
        "name": "Team Compliance Compass",
        "email": "support@compliancecompass.example.com",
        "url": "https://github.com/username/compliance-compass"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas section by default
        "docExpansion": "none",
        "filter": True,
        "operationsSorter": "alpha",
        "tagsSorter": "alpha",
        "tryItOutEnabled": True,
        "persistAuthorization": True
    }
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

# Aggiungi il middleware per la formattazione delle risposte
app.add_middleware(ResponseFormatterMiddleware)

# Middleware per rate limiting
app.add_middleware(
    RateLimitMiddleware,
    limit=settings.RATE_LIMIT_DEFAULT,
    interval=60
)

# Middleware per CSRF
app.add_middleware(
    CSRFMiddleware,
    secret=settings.SECRET_KEY,
    safe_methods=["GET", "HEAD", "OPTIONS"]
)

# Middleware per logging delle richieste
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/api/health", "/api/health/liveness", "/api/health/readiness"],
    log_request_body=False
)

# Aggiungi nuovi middleware di sicurezza
app.add_middleware(
    SecurityHeadersMiddleware,
    content_security_policy=None,  # Usa default
    enable_hsts=settings.ENVIRONMENT == "production"
)

app.add_middleware(
    BruteForceProtectionMiddleware,
    login_paths=["/api/auth/login"],
    max_attempts=5,
    lockout_time=1800  # 30 minuti
)

# Middleware di protezione SQL Injection solo in produzione
if settings.ENVIRONMENT == "production":
   from src.middleware.security import SQLInjectionProtectionMiddleware
   app.add_middleware(
       SQLInjectionProtectionMiddleware,
       enabled=True
   )

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

# Endpoint per il monitoraggio delle query lente
@app.get("/api/admin/performance/db-queries", include_in_schema=False)
async def get_db_performance(current_user: User = Depends(get_current_admin_user)):
    """
    Get database query performance report.
    Restricted to admin users.
    """
    from src.middleware.query_monitor import get_slow_queries_report
    return get_slow_queries_report()

# Inizializzazione app
@app.on_event("startup")
async def startup_event():
    """
    Evento di avvio dell'applicazione.
    
    Inizializza il database e altre risorse.
    """
    # Configura il logging con impostazioni dall'environment
    configure_logging(
        log_level='DEBUG' if settings.DEBUG else 'INFO',
        environment=settings.ENVIRONMENT,
        service_name='compliance-compass'
    )
    
    logger.info(f"Avvio applicazione {settings.APP_NAME} in ambiente {settings.ENVIRONMENT}")
    
    # Inizializza database
    init_db()
    
    # Inizializza il monitoraggio delle query
    from src.middleware.query_monitor import init_query_monitoring
    init_query_monitoring()
    
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