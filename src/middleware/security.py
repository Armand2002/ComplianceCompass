# src/middleware/security.py
"""
Middleware di sicurezza per l'applicazione.

Fornisce protezioni aggiuntive contro attacchi comuni.
"""
import time
import re
import logging
from typing import Dict, List, Optional, Set, Tuple
import threading
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware che aggiunge header di sicurezza alle risposte.
    
    Implementa best practices per la sicurezza web.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        content_security_policy: Optional[str] = None,
        enable_hsts: bool = True
    ):
        """
        Inizializza il middleware.
        
        Args:
            app (ASGIApp): Applicazione ASGI
            content_security_policy (str, optional): CSP policy personalizzata
            enable_hsts (bool): Se abilitare HSTS
        """
        super().__init__(app)
        
        # Default CSP ragionevole
        self.csp = content_security_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self';"
        )
        
        self.enable_hsts = enable_hsts
    
    async def dispatch(self, request: Request, call_next):
        # Processa la richiesta normalmente
        response = await call_next(request)
        
        # Aggiungi header di sicurezza
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = self.csp
        
        # HSTS - usa solo in produzione o con HTTPS
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        
        # Aggiungi Permissions-Policy (precedentemente Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "interest-cohort=()"  # Disabilita FLoC
        )
        
        return response

class BruteForceProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware per protezione contro attacchi di forza bruta.
    
    Traccia e limita tentativi di accesso falliti.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        login_paths: List[str] = None,
        max_attempts: int = 5,
        lockout_time: int = 1800,  # 30 minuti
        ip_whitelist: List[str] = None
    ):
        """
        Inizializza il middleware.
        
        Args:
            app (ASGIApp): Applicazione ASGI
            login_paths (List[str]): Path delle pagine di login
            max_attempts (int): Massimo di tentativi prima del blocco
            lockout_time (int): Tempo di blocco in secondi
            ip_whitelist (List[str]): Lista IP da non bloccare mai
        """
        super().__init__(app)
        
        self.login_paths = set(login_paths or ["/api/auth/login"])
        self.max_attempts = max_attempts
        self.lockout_time = lockout_time
        self.ip_whitelist = set(ip_whitelist or ["127.0.0.1", "::1"])
        
        # Strutture dati per tracciare tentativi
        self.failed_attempts: Dict[str, List[float]] = {}
        self.locked_ips: Dict[str, float] = {}
        
        self._lock = threading.RLock()
        
        # Cleanup periodico
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Avvia un thread per il cleanup periodico."""
        def cleanup_loop():
            while True:
                time.sleep(300)  # Ogni 5 minuti
                self._cleanup()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def _cleanup(self):
        """Rimuove record scaduti."""
        now = time.time()
        
        with self._lock:
            # Pulisci tentativi falliti vecchi
            for ip, attempts in list(self.failed_attempts.items()):
                self.failed_attempts[ip] = [t for t in attempts if now - t < 3600]
                if not self.failed_attempts[ip]:
                    del self.failed_attempts[ip]
            
            # Pulisci blocchi scaduti
            for ip, lock_time in list(self.locked_ips.items()):
                if now - lock_time >= self.lockout_time:
                    del self.locked_ips[ip]
                    logger.info(f"IP {ip} unlocked after lockout period")
    
    def is_ip_locked(self, ip: str) -> bool:
        """
        Verifica se un IP è bloccato.
        
        Args:
            ip (str): Indirizzo IP
            
        Returns:
            bool: True se l'IP è bloccato
        """
        with self._lock:
            # IP in whitelist non sono mai bloccati
            if ip in self.ip_whitelist:
                return False
                
            # Verifica se IP è nella lista dei bloccati
            if ip in self.locked_ips:
                lock_time = self.locked_ips[ip]
                now = time.time()
                
                # Verifica se il blocco è scaduto
                if now - lock_time >= self.lockout_time:
                    del self.locked_ips[ip]
                    return False
                
                return True
            
            return False
    
    def record_failed_attempt(self, ip: str):
        """
        Registra un tentativo fallito.
        
        Args:
            ip (str): Indirizzo IP
        """
        with self._lock:
            now = time.time()
            
            # IP in whitelist non vengono tracciati
            if ip in self.ip_whitelist:
                return
                
            # Inizializza array per IP se non esiste
            if ip not in self.failed_attempts:
                self.failed_attempts[ip] = []
            
            # Aggiungi timestamp del tentativo
            self.failed_attempts[ip].append(now)
            
            # Considera solo tentativi recenti (ultima ora)
            recent_attempts = [t for t in self.failed_attempts[ip] if now - t < 3600]
            self.failed_attempts[ip] = recent_attempts
            
            # Verifica se superato limite tentativi
            if len(recent_attempts) >= self.max_attempts:
                self.locked_ips[ip] = now
                logger.warning(f"IP {ip} locked for {self.lockout_time}s after {len(recent_attempts)} failed attempts")
    
    async def dispatch(self, request: Request, call_next):
        """Processa la richiesta con protezione brute force."""
        # Estrai IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Verifica se è un endpoint di login
        is_login_endpoint = request.url.path in self.login_paths and request.method == "POST"
        
        # Verifica se IP è bloccato
        if is_login_endpoint and self.is_ip_locked(client_ip):
            logger.warning(f"Blocked login attempt from locked IP: {client_ip}")
            
            return Response(
                content='{"error":{"message":"Too many failed attempts. Try again later.","error_code":"TOO_MANY_ATTEMPTS"}}',
                status_code=429,
                media_type="application/json"
            )
        
        # Processa normalmente
        response = await call_next(request)
        
        # Se è un endpoint di login e la risposta indica fallimento (401)
        if is_login_endpoint and response.status_code == 401:
            self.record_failed_attempt(client_ip)
        
        return response

class SQLInjectionProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware per protezione basilare contro SQL injection.
    
    Effettua controlli semplici su input che potrebbero contenere SQL injection.
    Nota: questo è complementare, non sostitutivo, dell'uso di ORM e prepared statements.
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        enabled: bool = True
    ):
        """
        Inizializza il middleware.
        
        Args:
            app (ASGIApp): Applicazione ASGI
            enabled (bool): Se abilitare la protezione
        """
        super().__init__(app)
        
        self.enabled = enabled
        
        # Pattern per rilevare potenziali SQL injection
        self.sql_patterns = [
            r'(\%27)|(\')|(\-\-)|(\%23)|(#)',  # caratteri speciali comuni
            r'((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))',  # attacchi basilari
            r'\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))',  # tentativi di "OR"
            r'((\%27)|(\'))union',  # UNION attempts
            r'exec(\s|\+)+(s|x)p\w+',  # exec sp attempts
        ]
        
        self.sql_pattern_compiled = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]
    
    def _check_sql_injection(self, value: str) -> bool:
        """
        Verifica se una stringa contiene pattern sospetti di SQL injection.
        
        Args:
            value (str): Stringa da verificare
            
        Returns:
            bool: True se il valore è sospetto
        """
        for pattern in self.sql_pattern_compiled:
            if pattern.search(value):
                return True
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Processa la richiesta con controllo SQL injection."""
        if not self.enabled:
            return await call_next(request)
        
        # Controllo solo per richieste con dati (POST, PUT, PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Ottieni i parametri della query string
                query_params = dict(request.query_params)
                
                # Controlla i parametri di query
                for key, value in query_params.items():
                    if self._check_sql_injection(value):
                        logger.warning(f"Potential SQL injection detected in query param: {key}={value}")
                        
                        return Response(
                            content='{"error":{"message":"Invalid input detected","error_code":"INVALID_INPUT"}}',
                            status_code=400,
                            media_type="application/json"
                        )
                
                # Per richieste con body JSON/form, controlla anche il body
                content_type = request.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    # Converti body in JSON senza consumarlo
                    body_bytes = await request.body()
                    request._body = body_bytes  # Preserva il body per successive letture
                    
                    # Controlla solo se non vuoto
                    if body_bytes:
                        import json
                        try:
                            json_body = json.loads(body_bytes)
                            
                            # Funzione ricorsiva per controllare valori annidati
                            def check_nested_values(obj):
                                if isinstance(obj, dict):
                                    for k, v in obj.items():
                                        if isinstance(v, str) and self._check_sql_injection(v):
                                            return True
                                        if isinstance(v, (dict, list)) and check_nested_values(v):
                                            return True
                                elif isinstance(obj, list):
                                    for item in obj:
                                        if isinstance(item, str) and self._check_sql_injection(item):
                                            return True
                                        if isinstance(item, (dict, list)) and check_nested_values(item):
                                            return True
                                return False
                            
                            if check_nested_values(json_body):
                                logger.warning(f"Potential SQL injection detected in JSON body")
                                
                                return Response(
                                    content='{"error":{"message":"Invalid input detected","error_code":"INVALID_INPUT"}}',
                                    status_code=400,
                                    media_type="application/json"
                                )
                        except json.JSONDecodeError:
                            # Non è un JSON valido, ignora
                            pass
                
                elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                    # Per form data, controlla i valori
                    form = await request.form()
                    for key, value in form.items():
                        if isinstance(value, str) and self._check_sql_injection(value):
                            logger.warning(f"Potential SQL injection detected in form field: {key}")
                            
                            return Response(
                                content='{"error":{"message":"Invalid input detected","error_code":"INVALID_INPUT"}}',
                                status_code=400,
                                media_type="application/json"
                            )
            
            except Exception as e:
                # In caso di errore nell'analisi, registra ma continua
                logger.error(f"Error in SQL injection check: {str(e)}")
        
        # Procedi normalmente
        return await call_next(request)