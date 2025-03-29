# src/middleware/rate_limit.py
from typing import Callable, Dict
import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware per implementare rate limiting più flessibile.
    """
    
    def __init__(
        self,
        app,
        limit: int = 100,  # Richieste per intervallo
        interval: int = 60,  # Intervallo in secondi
        by_ip: bool = True  # Se limitare per IP
    ):
        """
        Inizializza il middleware.
        
        Args:
            app: Applicazione FastAPI
            limit (int): Numero massimo di richieste per intervallo
            interval (int): Durata dell'intervallo in secondi
            by_ip (bool): Se usare l'IP per il limite
        """
        super().__init__(app)
        self.limit = limit
        self.interval = interval
        self.by_ip = by_ip
        self.requests: Dict[str, Dict[str, int]] = {}
        
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Processa la richiesta e applica il rate limiting.
        
        Args:
            request (Request): Richiesta HTTP
            call_next (Callable): Funzione per continuare la catena di middleware
            
        Returns:
            Response: Risposta HTTP
        """
        # Ottieni l'identificatore (IP o altro)
        identifier = request.client.host if self.by_ip else "global"
        
        # Cleanup vecchi record
        self._cleanup()
        
        # Controlla se l'identificatore esiste e inizializzalo se necessario
        if identifier not in self.requests:
            self.requests[identifier] = {
                "count": 0,
                "window_start": time.time()
            }
        
        # Incrementa contatore
        self.requests[identifier]["count"] += 1
        
        # Controlla se siamo oltre il limite
        if self.requests[identifier]["count"] > self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Troppe richieste, riprova più tardi."
            )
        
        # Continua con la richiesta
        return await call_next(request)
    
    def _cleanup(self):
        """Rimuove record scaduti"""
        current_time = time.time()
        expired_window = current_time - self.interval
        
        for identifier in list(self.requests.keys()):
            if self.requests[identifier]["window_start"] < expired_window:
                del self.requests[identifier]