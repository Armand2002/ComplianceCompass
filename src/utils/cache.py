# src/utils/cache.py
from functools import wraps
import time
from typing import Dict, Any, Callable, Optional, Set, List, Tuple, Union
import threading
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

# Singleton cache globale
_cache_instance = None

def get_cache():
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AdvancedCache()
    return _cache_instance

class CacheEntry:
    """Rappresenta un elemento in cache con metadati associati."""
    
    def __init__(self, key: str, value: Any, ttl: int):
        self.key = key
        self.value = value
        self.expires_at = time.time() + ttl
        self.created_at = time.time()
        self.access_count = 0
        self.last_accessed_at = self.created_at
    
    def is_expired(self) -> bool:
        """Verifica se l'elemento è scaduto."""
        return time.time() > self.expires_at
    
    def access(self) -> None:
        """Registra un accesso all'elemento."""
        self.access_count += 1
        self.last_accessed_at = time.time()
    
    def as_dict(self) -> Dict[str, Any]:
        """Converte l'elemento in un dizionario."""
        return {
            'key': self.key,
            'expires_at': self.expires_at,
            'created_at': self.created_at,
            'access_count': self.access_count,
            'last_accessed_at': self.last_accessed_at,
            'ttl': self.expires_at - self.created_at,
            'remaining_ttl': max(0, self.expires_at - time.time()),
            'age': time.time() - self.created_at
        }

class AdvancedCache:
    """
    Implementazione avanzata di un sistema di cache in memoria.
    
    Features:
    - Cache gerarchica per namespace
    - Invalidazione selettiva
    - Statistiche e metriche
    - Throttling automatico
    - Supporto per TTL variabile
    """
    
    def __init__(self, default_ttl: int = 300, max_size: int = 10000):
        """
        Inizializza la cache.
        
        Args:
            default_ttl (int): Time-to-live di default in secondi
            max_size (int): Dimensione massima della cache
        """
        self.entries: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._lock = threading.RLock()  # Per thread safety
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0,
            'cleanups': 0
        }
        self._last_cleanup = time.time()
        # Esegui cleanup periodico
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Avvia un thread per il cleanup periodico."""
        def cleanup_loop():
            while True:
                time.sleep(60)  # Ogni minuto
                self._cleanup()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera un valore dalla cache.
        
        Args:
            key (str): Chiave per il valore da recuperare
            
        Returns:
            Any: Valore in cache o None se non presente o scaduto
        """
        with self._lock:
            entry = self.entries.get(key)
            
            if not entry:
                self.stats['misses'] += 1
                return None
                
            # Verifica scadenza
            if entry.is_expired():
                del self.entries[key]
                self.stats['misses'] += 1
                return None
            
            # Aggiorna statistiche di accesso
            entry.access()
            self.stats['hits'] += 1
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Inserisce un valore in cache.
        
        Args:
            key (str): Chiave per il valore
            value (Any): Valore da salvare
            ttl (int, optional): Time-to-live specifico in secondi
        """
        with self._lock:
            # Limita dimensione cache
            if len(self.entries) >= self.max_size and key not in self.entries:
                self._evict()
            
            # Crea nuovo entry
            entry = CacheEntry(key, value, ttl or self.default_ttl)
            self.entries[key] = entry
            self.stats['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """
        Elimina un valore dalla cache.
        
        Args:
            key (str): Chiave da eliminare
            
        Returns:
            bool: True se l'elemento è stato eliminato, False altrimenti
        """
        with self._lock:
            if key in self.entries:
                del self.entries[key]
                self.stats['deletes'] += 1
                return True
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Elimina tutti i valori il cui nome chiave contiene il pattern.
        
        Args:
            pattern (str): Pattern da cercare nelle chiavi
            
        Returns:
            int: Numero di elementi eliminati
        """
        with self._lock:
            keys_to_delete = [k for k in self.entries.keys() if pattern in k]
            for key in keys_to_delete:
                del self.entries[key]
            
            self.stats['deletes'] += len(keys_to_delete)
            return len(keys_to_delete)
    
    def delete_namespace(self, namespace: str) -> int:
        """
        Elimina tutti i valori con un determinato namespace.
        
        Args:
            namespace (str): Namespace da eliminare (formato: "namespace:")
            
        Returns:
            int: Numero di elementi eliminati
        """
        if not namespace.endswith(':'):
            namespace = f"{namespace}:"
        
        return self.delete_pattern(namespace)
    
    def clear(self) -> None:
        """Svuota tutta la cache."""
        with self._lock:
            entries_count = len(self.entries)
            self.entries.clear()
            self.stats['deletes'] += entries_count
    
    def _cleanup(self) -> None:
        """Rimuove elementi scaduti dalla cache."""
        with self._lock:
            now = time.time()
            expired_keys = [k for k, v in self.entries.items() if v.is_expired()]
            
            for key in expired_keys:
                del self.entries[key]
            
            self.stats['cleanups'] += 1
            self._last_cleanup = now
    
    def _evict(self) -> None:
        """
        Rimuove un elemento dalla cache quando è piena.
        Strategia: rimuovi gli elementi meno usati (LFU) o più vecchi (LRU).
        """
        with self._lock:
            if not self.entries:
                return
            
            # Prima prova a rimuovere elementi scaduti
            now = time.time()
            expired_keys = [k for k, v in self.entries.items() if v.is_expired()]
            
            if expired_keys:
                for key in expired_keys[:max(1, len(expired_keys) // 10)]:  # Rimuovi almeno 1, max 10% degli scaduti
                    del self.entries[key]
                self.stats['evictions'] += len(expired_keys)
                return
            
            # Se non ci sono elementi scaduti, usa una strategia ibrida
            # 80% delle volte: rimuovi l'elemento meno frequentemente usato (LFU)
            # 20% delle volte: rimuovi l'elemento più vecchio (LRU)
            if hash(str(time.time())) % 100 < 80:
                # LFU strategy
                key_to_remove = min(self.entries.items(), key=lambda x: x[1].access_count)[0]
            else:
                # LRU strategy
                key_to_remove = min(self.entries.items(), key=lambda x: x[1].last_accessed_at)[0]
            
            del self.entries[key_to_remove]
            self.stats['evictions'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Ottiene statistiche sulla cache.
        
        Returns:
            Dict[str, Any]: Statistiche cache
        """
        with self._lock:
            hit_ratio = 0
            if (self.stats['hits'] + self.stats['misses']) > 0:
                hit_ratio = self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])
            
            return {
                'entries': len(self.entries),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
                'memory_usage_estimate': len(self.entries) * 200,  # Stima approssimativa in bytes
                'last_cleanup': self._last_cleanup,
                'stats': self.stats.copy(),
                'hit_ratio': hit_ratio,
                'namespaces': self._get_namespace_stats()
            }
    
    def _get_namespace_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Ottiene statistiche per namespace.
        
        Returns:
            Dict[str, Dict[str, int]]: Statistiche per namespace
        """
        namespace_stats = {}
        
        for key in self.entries.keys():
            namespace = key.split(':', 1)[0] if ':' in key else '_default_'
            
            if namespace not in namespace_stats:
                namespace_stats[namespace] = {'count': 0}
            
            namespace_stats[namespace]['count'] += 1
        
        return namespace_stats

def cached(ttl: Optional[int] = None, namespace: Optional[str] = None):
    """
    Decoratore per cachare il risultato di una funzione.
    La chiave di cache è basata sul nome della funzione e i suoi argomenti.
    
    Args:
        ttl (int, optional): Time-to-live specifico in secondi
        namespace (str, optional): Namespace per raggruppamento logico
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crea namespace da nome funzione o namespace specificato
            ns = namespace or f"{func.__module__}.{func.__name__}"
            
            # Serializza args e kwargs per generare chiave unica
            # Escludi argomenti non serializzabili (Session, Request, etc.)
            key_args = []
            for arg in args:
                try:
                    # Tenta la serializzazione per verificare se è hashable
                    json.dumps(str(arg))
                    key_args.append(str(arg))
                except (TypeError, ValueError, OverflowError):
                    # Se non serializzabile, usa l'ID dell'oggetto
                    key_args.append(f"obj:{id(arg)}")
            
            key_kwargs = []
            for k, v in sorted(kwargs.items()):
                try:
                    json.dumps(str(v))
                    key_kwargs.append(f"{k}={v}")
                except (TypeError, ValueError, OverflowError):
                    key_kwargs.append(f"{k}=obj:{id(v)}")
            
            # Genera hash univoco per la chiave
            key_string = f"{ns}:{':'.join(key_args)}:{':'.join(key_kwargs)}"
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            
            # Chiave finale
            cache_key = f"{ns}:{key_hash}"
            
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

def invalidate_cache(namespace: str) -> int:
    """
    Invalida tutti gli elementi cache in un namespace.
    
    Args:
        namespace (str): Namespace da invalidare
        
    Returns:
        int: Numero di elementi invalidati
    """
    cache = get_cache()
    return cache.delete_namespace(namespace)

def invalidate_pattern_cache(pattern_id: int) -> int:
    """
    Invalida tutte le cache relative a un pattern specifico.
    
    Args:
        pattern_id (int): ID del pattern
        
    Returns:
        int: Numero di elementi invalidati
    """
    cache = get_cache()
    
    # Invalida cache dirette del pattern
    count = cache.delete_pattern(f"pattern:{pattern_id}")
    
    # Invalida anche le cache di ricerca che potrebbero contenere questo pattern
    count += cache.delete_namespace("pattern_search")
    count += cache.delete_namespace("pattern_list")
    
    logger.info(f"Invalidate {count} cache entries for pattern {pattern_id}")
    return count

# Alias alla vecchia classe per retrocompatibilità
# SimpleCache = AdvancedCache