"""Utility per la gestione della cache con supporto per TTL."""
from functools import wraps
import time
from typing import Dict, Any, Callable, Tuple, Optional
import logging
import threading

logger = logging.getLogger(__name__)

class Cache:
    """
    Implementazione di un sistema di caching in-memory con TTL.
    """
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.RLock()
        
    def cached(self, ttl: int = 60):
        """
        Decorator per cachare i risultati delle funzioni.
        
        Args:
            ttl: Tempo di vita in secondi per la cache
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Crea una chiave unica basata su funzione e parametri
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                with self._lock:
                    # Verifica se il valore è in cache e non è scaduto
                    if key in self._cache:
                        value, timestamp = self._cache[key]
                        if time.time() - timestamp < ttl:
                            logger.debug(f"Cache hit for {key}")
                            return value
                    
                    # Esegui la funzione e salva il risultato in cache
                    logger.debug(f"Cache miss for {key}")
                    result = func(*args, **kwargs)
                    self._cache[key] = (result, time.time())
                    return result
                
            return wrapper
        return decorator
    
    def get(self, key: str, default: Any = None) -> Any:
        """Recupera un valore dalla cache."""
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                return value
            return default
    
    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """Imposta un valore nella cache."""
        with self._lock:
            self._cache[key] = (value, time.time() + ttl)
    
    def delete(self, key: str) -> None:
        """Elimina una chiave dalla cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self, pattern: Optional[str] = None):
        """Pulisce la cache, opzionalmente solo le chiavi che corrispondono a un pattern."""
        with self._lock:
            if pattern:
                self._cache = {k: v for k, v in self._cache.items() if pattern not in k}
            else:
                self._cache.clear()

# Crea un'istanza di cache globale
cache = Cache()

# Esporta la funzione decorated per compatibilità
def cached(ttl: int = 60):
    """Decorator compatibile per il caching."""
    return cache.cached(ttl)

# Per invalidare la cache dei pattern
def invalidate_pattern_cache():
    """Invalida la cache relativa ai pattern."""
    cache.clear(pattern="pattern")