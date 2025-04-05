# src/middleware/response_formatter.py
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ResponseFormatterMiddleware(BaseHTTPMiddleware):
    """
    Middleware per standardizzare il formato delle risposte e aggiungere metadati.
    
    - Aggiunge metadati come tempo di elaborazione e timestamp
    - Standardizza le risposte di errore
    - Registra metriche di latenza
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            # Processa la richiesta
            response = await call_next(request)
            
            # Aggiungi header con tempo di elaborazione
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Logga richieste lente
            if process_time > 0.5:  # 500ms
                logger.warning(
                    f"Richiesta lenta: {request.method} {request.url.path} - {process_time:.4f}s"
                )
            
            return response
            
        except Exception as exc:
            # Gestisci le eccezioni non catturate
            error_time = time.time() - start_time
            
            # Logga l'errore
            logger.error(
                f"Errore non gestito: {request.method} {request.url.path} - {str(exc)}",
                exc_info=True
            )
            
            # Prepara risposta di errore standardizzata
            error_response = {
                "detail": {
                    "message": "Si è verificato un errore interno",
                    "error_type": type(exc).__name__,
                    "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
                },
                "metadata": {
                    "timestamp": time.time(),
                    "process_time": error_time
                }
            }
            
            return JSONResponse(
                status_code=500,
                content=error_response
            )