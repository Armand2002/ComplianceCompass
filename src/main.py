# src/main.py
import uvicorn
from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Dict, Any
from pydantic import BaseModel

# Importazione fastapi-csrf-protect invece di CSRFMiddleware
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

from src.middleware.rate_limit import RateLimitMiddleware
from src.config import settings
from src.routes.api import api_router
from src.db.init_db import init_db
from src.services.elasticsearch_init import ElasticsearchInit
from src.middleware.error_handler import register_exception_handlers
from src.logging_config import configure_logging
from src.middleware.response_formatter import ResponseFormatterMiddleware
from src.middleware.logging_middleware import RequestLoggingMiddleware
from src.middleware.security import SecurityHeadersMiddleware, BruteForceProtectionMiddleware
from src.models.user_model import User
from src.auth.dependencies import get_current_admin_user
from src.routes import newsletter_routes
from src.schemas.newsletter import NewsletterSubscriptionCreate
from src.controllers.newsletter_controller import newsletter_controller
from sqlalchemy.orm import Session
from src.auth.dependencies import get_db

logger = logging.getLogger(__name__)

# Configurazione rate limiter
limiter = Limiter(key_func=get_remote_address)

# Configurazione CSRF
class CsrfSettings(BaseModel):
    secret_key: str = settings.JWT_SECRET_KEY
    cookie_secure: bool = False  # True in produzione
    cookie_samesite: str = 'lax'
    cookie_name: str = 'fastapi-csrf-token'

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# Inizializzazione app
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
        },
        {
            "name": "newsletter",
            "description": "Operazioni relative alla newsletter"
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

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Registrazione errori di rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Registrazione dei middleware
app.add_middleware(BruteForceProtectionMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ResponseFormatterMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    limit=settings.RATE_LIMIT_DEFAULT,
    interval=60
)

# Gestore eccezioni CSRF
@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# Attivazione router
app.include_router(api_router)
app.include_router(newsletter_routes.router, prefix="/api")

# Endpoint per generare CSRF token
@app.get("/api/csrf-token", tags=["Security"])
async def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    """Genera un nuovo token CSRF e lo imposta come cookie."""
    response = JSONResponse(content={"detail": "CSRF token cookie set"})
    csrf_protect.set_csrf_cookie(response)
    return response

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

# Endpoint per iscrizione alla newsletter
@newsletter_routes.router.post("/subscribe", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def subscribe_newsletter(
    subscription: NewsletterSubscriptionCreate,
    db: Session = Depends(get_db)
):
    """
    Iscrive un utente alla newsletter.
    
    - **email**: L'indirizzo email da iscrivere
    
    Returns:
        - **message**: Messaggio di esito dell'operazione
        - **requires_verification**: Se è richiesta la verifica dell'email
        - **already_subscribed**: Se l'email è già iscritta (opzionale)
    
    Esempi:
        - Iscrizione nuova email: `{"message": "Iscrizione creata. Email di verifica inviata.", "requires_verification": true}`
        - Email già iscritta: `{"message": "Email già iscritta alla newsletter", "already_subscribed": true}`
    """
    return newsletter_controller.subscribe(db, subscription.email)

# Evento di startup
@app.on_event("startup")
async def startup_event():
    logger.info(f"Avvio applicazione {settings.APP_NAME} in ambiente {settings.ENVIRONMENT}")
    
    # Inizializzazione database
    try:
        init_db()
        logger.info("Database inizializzato con successo")
    except Exception as e:
        logger.error(f"Errore nell'inizializzazione del database: {e}")
    
    # Inizializzazione Elasticsearch
    try:
        es_init = ElasticsearchInit()
        if es_init.connected:
            es_init.setup_indices()
            logger.info("Elasticsearch inizializzato con successo.")
        else:
            logger.warning("Elasticsearch non disponibile. Funzionalità di ricerca avanzata disabilitate.")
    except Exception as e:
        logger.error(f"Errore nell'inizializzazione di Elasticsearch: {e}")

    # Configura il logging con impostazioni dall'environment
    configure_logging(
        log_level='DEBUG' if settings.DEBUG else 'INFO',
        environment=settings.ENVIRONMENT,
        service_name='compliance-compass'
    )
    
    logger.info("Applicazione avviata con successo")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento di spegnimento dell'applicazione.
    
    Chiude le connessioni e libera le risorse.
    """
    logger.info("Spegnimento applicazione")

# Se questo file viene eseguito direttamente
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
