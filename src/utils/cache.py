# src/utils/cache.py
from functools import wraps
import time
from typing import Dict, Any, Callable, Optional

# Singleton cache globale
_cache_instance = None

def get_cache():
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = SimpleCache()
    return _cache_instance

class SimpleCache:
    """
    Implementazione semplice di un sistema di cache in memoria.
    """
    
    def __init__(self, default_ttl: int = 300):
        """
        Inizializza la cache.
        
        Args:
            default_ttl (int): Time-to-live di default in secondi
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera un valore dalla cache.
        
        Args:
            key (str): Chiave per il valore da recuperare
            
        Returns:
            Any: Valore in cache o None se non presente o scaduto
        """
        cache_item = self.cache.get(key)
        
        if not cache_item:
            return None
            
        # Verifica scadenza
        if time.time() > cache_item.get('expires_at', 0):
            del self.cache[key]
            return None
            
        return cache_item.get('value')
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Inserisce un valore in cache.
        
        Args:
            key (str): Chiave per il valore
            value (Any): Valore da salvare
            ttl (int, optional): Time-to-live specifico in secondi
        """
        expiry = time.time() + (ttl or self.default_ttl)
        
        self.cache[key] = {
            'value': value,
            'expires_at': expiry
        }
    
    def delete(self, key: str) -> None:
        """
        Elimina un valore dalla cache.
        
        Args:
            key (str): Chiave da eliminare
        """
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Svuota tutta la cache."""
        self.cache.clear()


def cached(ttl: Optional[int] = None):
    """
    Decoratore per cachare il risultato di una funzione.
    La chiave di cache è basata sul nome della funzione e i suoi argomenti.
    
    Args:
        ttl (int, optional): Time-to-live specifico in secondi
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crea una chiave unica basata sulla funzione e i suoi parametri
            key_parts = [func.__module__, func.__name__]
            
            # Aggiungi args e kwargs alla chiave
            for arg in args:
                key_parts.append(str(arg))
                
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
                
            cache_key = ":".join(key_parts)
            
            cache = get_cache()
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # Calcola il risultato e salvalo in cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator