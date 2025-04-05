# src/utils/metrics.py
import time
import threading
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
from functools import wraps

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Raccoglitore di metriche per monitorare le prestazioni dell'API.
    
    Implementa un singleton thread-safe per la raccolta di metriche
    di performance, errori e utilizzo delle API.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsCollector, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._metrics = {
            "requests": {
                "total": 0,
                "by_endpoint": {},
                "by_status": {},
                "by_method": {}
            },
            "errors": {
                "total": 0,
                "by_type": {}
            },
            "performance": {
                "response_times": [],
                "avg_response_time": 0
            },
            "started_at": datetime.utcnow().isoformat()
        }
        self._last_dump = datetime.utcnow()
        self._dump_interval = timedelta(hours=1)
        self._metrics_dir = "metrics"
        self._lock = threading.Lock()
        self._initialized = True
        
        # Crea directory per metriche se non esiste
        os.makedirs(self._metrics_dir, exist_ok=True)
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Registra una richiesta API."""
        with self._lock:
            # Incrementa contatori
            self._metrics["requests"]["total"] += 1
            
            # Per endpoint
            if endpoint not in self._metrics["requests"]["by_endpoint"]:
                self._metrics["requests"]["by_endpoint"][endpoint] = {
                    "count": 0,
                    "response_times": []
                }
            self._metrics["requests"]["by_endpoint"][endpoint]["count"] += 1
            self._metrics["requests"]["by_endpoint"][endpoint]["response_times"].append(duration)
            
            # Per codice stato
            status_str = str(status_code)
            if status_str not in self._metrics["requests"]["by_status"]:
                self._metrics["requests"]["by_status"][status_str] = 0
            self._metrics["requests"]["by_status"][status_str] += 1
            
            # Per metodo
            if method not in self._metrics["requests"]["by_method"]:
                self._metrics["requests"]["by_method"][method] = 0
            self._metrics["requests"]["by_method"][method] += 1
            
            # Performance
            self._metrics["performance"]["response_times"].append(duration)
            self._metrics["performance"]["avg_response_time"] = (
                sum(self._metrics["performance"]["response_times"]) / 
                len(self._metrics["performance"]["response_times"])
            )
            
            # Limita l'array delle response times per evitare eccesso di memoria
            max_samples = 1000
            if len(self._metrics["performance"]["response_times"]) > max_samples:
                self._metrics["performance"]["response_times"] = self._metrics["performance"]["response_times"][-max_samples:]
            
            # Dump periodico delle metriche
            now = datetime.utcnow()
            if now - self._last_dump > self._dump_interval:
                self._dump_metrics()
                self._last_dump = now
    
    def record_error(self, error_type: str, endpoint: str):
        """Registra un errore."""
        with self._lock:
            self._metrics["errors"]["total"] += 1
            
            if error_type not in self._metrics["errors"]["by_type"]:
                self._metrics["errors"]["by_type"][error_type] = {
                    "count": 0,
                    "endpoints": {}
                }
            self._metrics["errors"]["by_type"][error_type]["count"] += 1
            
            if endpoint not in self._metrics["errors"]["by_type"][error_type]["endpoints"]:
                self._metrics["errors"]["by_type"][error_type]["endpoints"][endpoint] = 0
            self._metrics["errors"]["by_type"][error_type]["endpoints"][endpoint] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Ottiene lo snapshot corrente delle metriche."""
        with self._lock:
            return self._metrics.copy()
    
    def _dump_metrics(self):
        """Salva le metriche su file per analisi storica."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{self._metrics_dir}/metrics_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(self._metrics, f, indent=2)
                
            logger.info(f"Metrics dumped to {filename}")
        except Exception as e:
            logger.error(f"Error dumping metrics: {str(e)}")


def track_metrics(func):
    """
    Decoratore per tracciare automaticamente metriche per funzioni di route.
    
    Usage:
        @router.get("/{pattern_id}")
        @track_metrics
        async def get_pattern(pattern_id: int):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        metrics = MetricsCollector()
        start_time = time.time()
        method = "UNKNOWN"
        endpoint = "UNKNOWN"
        status_code = 500
        
        # Estrai informazioni dalla richiesta
        for arg in args:
            if hasattr(arg, "method") and hasattr(arg, "url"):
                method = arg.method
                endpoint = str(arg.url.path)
                break
        
        try:
            response = await func(*args, **kwargs)
            status_code = getattr(response, "status_code", 200)
            return response
        except Exception as e:
            # Registra l'errore e lo status code
            error_type = type(e).__name__
            status_code = getattr(e, "status_code", 500)
            metrics.record_error(error_type, endpoint)
            raise
        finally:
            duration = time.time() - start_time
            metrics.record_request(method, endpoint, status_code, duration)
    
    return wrapper