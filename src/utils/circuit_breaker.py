# src/utils/circuit_breaker.py
"""
Implementazione del pattern Circuit Breaker.

Questo modulo fornisce un'implementazione del pattern Circuit Breaker
per prevenire chiamate ripetute a servizi non disponibili.
"""

import time
import logging
import threading
import functools
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitState(str, Enum):
    """Stati possibili del Circuit Breaker."""
    CLOSED = "CLOSED"        # Normale operatività
    OPEN = "OPEN"            # Non permette chiamate
    HALF_OPEN = "HALF_OPEN"  # Permette una singola chiamata di test

class CircuitBreaker:
    """
    Implementazione del pattern Circuit Breaker.
    
    Previene chiamate ripetute a servizi che falliscono regolarmente,
    permettendo il recovery automatico.
    """
    
    # Registry globale dei circuit breaker
    _instances: Dict[str, 'CircuitBreaker'] = {}
    _lock = threading.RLock()
    
    @classmethod
    def get_or_create(
        cls, 
        name: str, 
        failure_threshold: int = 5,
        reset_timeout: int = 60
    ) -> 'CircuitBreaker':
        """
        Ottiene o crea un circuit breaker con un dato nome.
        
        Args:
            name (str): Nome univoco del circuit breaker
            failure_threshold (int): Numero di fallimenti prima dell'apertura
            reset_timeout (int): Secondi prima di tentare il reset (HALF_OPEN)
            
        Returns:
            CircuitBreaker: Istanza richiesta del circuit breaker
        """
        with cls._lock:
            if name not in cls._instances:
                cls._instances[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    reset_timeout=reset_timeout
                )
            return cls._instances[name]
    
    @classmethod
    def get_all_states(cls) -> Dict[str, Dict[str, Any]]:
        """
        Ottiene lo stato di tutti i circuit breaker.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dizionario con lo stato di ogni circuit breaker
        """
        with cls._lock:
            return {
                name: breaker.get_state_dict()
                for name, breaker in cls._instances.items()
            }
    
    def __init__(
        self, 
        name: str,
        failure_threshold: int = 5,
        reset_timeout: int = 60
    ):
        """
        Inizializza un circuit breaker.
        
        Args:
            name (str): Nome univoco del circuit breaker
            failure_threshold (int): Numero di fallimenti prima dell'apertura
            reset_timeout (int): Secondi prima di tentare il reset (HALF_OPEN)
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = 0.0
        self.total_failures = 0
        self.consecutive_successes = 0
        self.total_successes = 0
        
        self._lock = threading.RLock()
    
    def get_state_dict(self) -> Dict[str, Any]:
        """
        Restituisce un dizionario con lo stato corrente.
        
        Returns:
            Dict[str, Any]: Stato corrente del circuit breaker
        """
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "failure_threshold": self.failure_threshold,
                "reset_timeout": self.reset_timeout,
                "last_failure_time": self.last_failure_time,
                "last_success_time": self.last_success_time,
                "total_failures": self.total_failures,
                "total_successes": self.total_successes,
                "consecutive_successes": self.consecutive_successes
            }
    
    def _should_attempt_call(self) -> bool:
        """
        Verifica se è possibile tentare una chiamata.
        
        Returns:
            bool: True se la chiamata è permessa, False altrimenti
        """
        with self._lock:
            now = time.time()
            
            if self.state == CircuitState.CLOSED:
                return True
                
            if self.state == CircuitState.OPEN:
                # Verifica se è passato abbastanza tempo per passare a HALF_OPEN
                time_since_last_failure = now - self.last_failure_time
                if time_since_last_failure >= self.reset_timeout:
                    logger.info(f"Circuit breaker {self.name} entering HALF-OPEN state")
                    self.state = CircuitState.HALF_OPEN
                    return True
                return False
                
            # In HALF_OPEN, permetti una singola chiamata
            return True
    
    def _on_success(self) -> None:
        """Gestisce il successo di una chiamata."""
        with self._lock:
            self.last_success_time = time.time()
            self.total_successes += 1
            
            if self.state == CircuitState.HALF_OPEN:
                self.consecutive_successes += 1
                
                # Dopo 3 successi consecutivi in HALF_OPEN, torna a CLOSED
                if self.consecutive_successes >= 3:
                    logger.info(f"Circuit breaker {self.name} reset to CLOSED")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.consecutive_successes = 0
            
            # In CLOSED, resetta i contatori di fallimento
            if self.state == CircuitState.CLOSED:
                self.failure_count = 0
                self.consecutive_successes = 0
    
    def _on_failure(self, exception: Exception) -> None:
        """
        Gestisce il fallimento di una chiamata.
        
        Args:
            exception (Exception): Eccezione che ha causato il fallimento
        """
        with self._lock:
            now = time.time()
            self.last_failure_time = now
            self.failure_count += 1
            self.total_failures += 1
            self.consecutive_successes = 0
            
            # In HALF_OPEN, torna subito a OPEN
            if self.state == CircuitState.HALF_OPEN:
                logger.warning(
                    f"Circuit breaker {self.name} returned to OPEN state after "
                    f"failure in HALF-OPEN: {str(exception)}"
                )
                self.state = CircuitState.OPEN
                return
                
            # In CLOSED, verifica se superata la soglia
            if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
                logger.warning(
                    f"Circuit breaker {self.name} tripped to OPEN state after "
                    f"{self.failure_count} consecutive failures"
                )
                self.state = CircuitState.OPEN
    
    def execute(self, func: Callable[..., T], fallback: Optional[Callable[..., T]] = None) -> T:
        """
        Esegue una funzione con la protezione del circuit breaker.
        
        Args:
            func (Callable): Funzione da eseguire
            fallback (Callable, optional): Funzione di fallback
            
        Returns:
            Any: Risultato della funzione o del fallback
            
        Raises:
            Exception: Se la chiamata fallisce e non è fornito un fallback
        """
        # Verifica se è possibile tentare la chiamata
        if not self._should_attempt_call():
            logger.warning(f"Circuit breaker {self.name} is OPEN, using fallback")
            
            if fallback:
                return fallback()
            
            raise RuntimeError(f"Circuit breaker {self.name} is OPEN and no fallback provided")
        
        try:
            result = func()
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure(e)
            
            if fallback:
                logger.info(f"Circuit breaker {self.name} is using fallback after failure")
                return fallback()
            
            raise

def circuit_breaker(
    name_or_breaker: Union[str, CircuitBreaker],
    failure_threshold: int = 5,
    reset_timeout: int = 60,
    fallback_function: Optional[Callable[..., T]] = None
):
    """
    Decoratore che applica il pattern Circuit Breaker a una funzione.
    
    Args:
        name_or_breaker: Nome del circuit breaker o istanza
        failure_threshold: Numero di fallimenti prima dell'apertura
        reset_timeout: Secondi prima di tentare il reset
        fallback_function: Funzione di fallback opzionale
    
    Returns:
        Callable: Funzione decorata con circuit breaker
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            breaker = name_or_breaker
            
            if isinstance(name_or_breaker, str):
                breaker = CircuitBreaker.get_or_create(
                    name=name_or_breaker,
                    failure_threshold=failure_threshold,
                    reset_timeout=reset_timeout
                )
            
            # Preparare funzione e fallback
            def execute_function():
                return func(*args, **kwargs)
            
            fallback = None
            if fallback_function:
                def execute_fallback():
                    return fallback_function(*args, **kwargs)
                fallback = execute_fallback
            
            return cast(CircuitBreaker, breaker).execute(execute_function, fallback)
        
        return wrapper
    
    return decorator