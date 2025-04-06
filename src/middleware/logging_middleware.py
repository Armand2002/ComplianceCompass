# src/middleware/logging_middleware.py
"""
Middleware per il logging delle richieste HTTP.

Questo modulo fornisce il middleware per il logging delle richieste
HTTP, inclusi tempi di risposta, status code e altri metadati.
"""

import time
import logging
import uuid
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.logging_config import set_request_context

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware per il logging delle richieste HTTP.
    
    Registra metadati e tempi di risposta per ogni richiesta.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        exclude_paths: list = None,
        log_request_body: bool = False
    ):
        """
        Inizializza il middleware.
        
        Args:
            app (ASGIApp): Applicazione ASGI
            exclude_paths (list, optional): Paths da escludere dal logging
            log_request_body (bool): Se loggare il corpo della richiesta
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.log_request_body = log_request_body
    
    async def dispatch(self, request: Request, call_next):
        # Genera request_id univoco
        request_id = str(uuid.uuid4())
        
        # Estrai informazioni dalla richiesta
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Imposta contesto per il logging
        set_request_context(
            request_id=request_id,
            ip=client_ip,
            path=path,
            method=method,
            user_agent=user_agent
        )
        
        # Ignora il logging per paths esclusi (es. health check)
        should_log = not any(path.startswith(excluded) for excluded in self.exclude_paths)
        
        if should_log:
            logger.info(f"Request started: {method} {path}")
        
        start_time = time.time()
        
        try:
            # Esegui la richiesta
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Ottieni lo status code
            status_code = response.status_code
            
            # Imposta l'header con il request ID
            response.headers["X-Request-ID"] = request_id
            
            # Log solo se non in lista di esclusione
            if should_log:
                log_level = logging.INFO
                
                # Usa log di warning per risposte di errore (4xx, 5xx)
                if status_code >= 400:
                    log_level = logging.WARNING
                
                log_message = (
                    f"Request completed: {method} {path} - "
                    f"Status: {status_code} - "
                    f"Duration: {process_time:.3f}s"
                )
                
                logger.log(log_level, log_message)
                
                # Log dettagliato per richieste lente (> 1s)
                if process_time > 1.0:
                    logger.warning(
                        f"Slow request detected: {method} {path} - "
                        f"Duration: {process_time:.3f}s"
                    )
            
            return response
            
        except Exception as e:
            # Log dell'errore
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed: {method} {path} - "
                f"Error: {type(e).__name__} - "
                f"Message: {str(e)} - "
                f"Duration: {process_time:.3f}s",
                exc_info=True
            )
            
            # Rilancia l'eccezione per gestione centralizzata
            raise