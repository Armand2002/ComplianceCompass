"""
Monitoraggio delle query database.

Monitora le query SQL lente e fornisce report di performance.
"""

import time
import logging
import threading
from collections import deque
from typing import Dict, Any
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# Cache circolare per le query lente (conserva le ultime N query)
_slow_queries = deque(maxlen=100)
_query_stats = {
    "count": 0,
    "total_time": 0,
    "slow_count": 0,  # Query oltre la soglia
    "max_time": 0
}

# Soglia in secondi per considerate una query "lenta"
SLOW_QUERY_THRESHOLD = 0.5

# Lock per thread safety
_stats_lock = threading.RLock()

def init_query_monitoring():
    """Inizializza il monitoraggio delle query SQL."""
    logger.info("Inizializzazione monitoraggio query database")
    
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()
    
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        execution_time = time.time() - context._query_start_time
        
        with _stats_lock:
            # Aggiorna statistiche generali
            _query_stats["count"] += 1
            _query_stats["total_time"] += execution_time
            
            if execution_time > _query_stats["max_time"]:
                _query_stats["max_time"] = execution_time
            
            # Registra query lente
            if execution_time > SLOW_QUERY_THRESHOLD:
                _query_stats["slow_count"] += 1
                
                # Formatta parametri per leggibilità
                params_str = str(parameters)
                if len(params_str) > 200:
                    params_str = params_str[:200] + "..."
                
                # Registra i dettagli della query lenta
                _slow_queries.append({
                    "timestamp": time.time(),
                    "statement": statement,
                    "parameters": params_str,
                    "execution_time": execution_time
                })
                
                # Log delle query particolarmente lente
                if execution_time > SLOW_QUERY_THRESHOLD * 2:
                    logger.warning(f"Query molto lenta ({execution_time:.2f}s): {statement[:100]}...")

def get_slow_queries_report() -> Dict[str, Any]:
    """
    Genera un report sulle query lente.
    
    Returns:
        Dict[str, Any]: Report con statistiche e lista di query lente
    """
    with _stats_lock:
        avg_time = 0
        if _query_stats["count"] > 0:
            avg_time = _query_stats["total_time"] / _query_stats["count"]
        
        return {
            "stats": {
                "total_queries": _query_stats["count"],
                "total_execution_time": round(_query_stats["total_time"], 2),
                "average_time": round(avg_time, 4),
                "max_time": round(_query_stats["max_time"], 4),
                "slow_queries_count": _query_stats["slow_count"],
                "slow_query_threshold": SLOW_QUERY_THRESHOLD
            },
            "slow_queries": list(_slow_queries)
        }

def reset_stats() -> None:
    """Resetta le statistiche e le query memorizzate."""
    with _stats_lock:
        _slow_queries.clear()
        _query_stats["count"] = 0
        _query_stats["total_time"] = 0
        _query_stats["slow_count"] = 0
        _query_stats["max_time"] = 0