# src/routes/health_routes.py
"""Routes per il monitoraggio dello stato del sistema."""

# Verifica se psutil è importato correttamente
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    import logging
    logging.warning("psutil non è installato. Alcune funzionalità di monitoraggio saranno limitate.")

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import os
import logging
import traceback

from src.db.session import get_db

router = APIRouter()

@router.get("/monitoring/health")
async def health_check(db: Session = Depends(get_db)):
    """Verifica completa dello stato del sistema."""
    try:
        start_time = time.time()
        result = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }
        
        # Verifica database
        try:
            db.execute(text("SELECT 1"))
            result["components"]["database"] = {
                "status": "healthy",
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            result["status"] = "degraded"
            result["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Verifica filesystem solo se psutil è disponibile
        if PSUTIL_AVAILABLE:
            try:
                disk = psutil.disk_usage(os.path.abspath(os.sep))
                result["components"]["filesystem"] = {
                    "status": "healthy",
                    "usage_percent": disk.percent,
                    "free_gb": round(disk.free / (1024 ** 3), 2)
                }
                
                if disk.percent > 90:
                    result["components"]["filesystem"]["status"] = "warning"
                    if result["status"] == "healthy":
                        result["status"] = "warning"
            except Exception as e:
                result["components"]["filesystem"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # Metriche di sistema
            result["system"] = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "response_time_ms": round((time.time() - start_time) * 1000, 2)
            }
        else:
            # Versione semplificata senza psutil
            result["components"]["system"] = {
                "status": "limited",
                "message": "psutil non disponibile, informazioni di sistema limitate"
            }
            result["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        
        return result
    except Exception as e:
        # Aggiungi log dell'errore
        logging.error(f"Errore in health_check: {str(e)}")
        logging.error(traceback.format_exc())
        
        # Restituisci comunque una risposta invece di lasciare fallire la richiesta
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

@router.get(
    "/monitoring/readiness",
    summary="Probe di readiness",
    description="Verifica che il sistema sia pronto a ricevere traffico",
    response_description="Stato di readiness del sistema"
)
async def readiness_probe(db: Session = Depends(get_db)):
    """Verifica che il sistema sia pronto a ricevere traffico."""
    try:
        # Verifica connessione DB
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema non pronto"
        )

@router.get(
    "/monitoring/liveness",
    summary="Probe di liveness",
    description="Verifica che il sistema sia in esecuzione",
    response_description="Stato di liveness del sistema"
)
async def liveness_probe():
    """Verifica semplice che il sistema sia in esecuzione."""
    return {"status": "alive"}

@router.get("/monitoring/ping")
async def ping():
    """Endpoint ultra-semplice per verificare che il router funzioni."""
    return {"status": "ok", "ping": "pong"}