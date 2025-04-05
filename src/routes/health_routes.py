# src/routes/health_routes.py
import time
import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.db.session import get_db
from src.services.search_service import SearchService

router = APIRouter(
    prefix="/health",
    tags=["monitoraggio"],
    responses={500: {"description": "Errore interno del server"}}
)

@router.get(
    "/",
    summary="Verifica stato sistema",
    description="Fornisce informazioni sull'integrità e lo stato dei componenti del sistema",
    response_description="Stato di salute del sistema"
)
async def health_check(db: Session = Depends(get_db)):
    """Verifica lo stato di salute dei componenti del sistema."""
    start_time = time.time()
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {}
    }
    
    # Verifica database
    try:
        # Query semplice per verificare connessione DB
        db.execute(text("SELECT 1"))
        health_data["components"]["database"] = {
            "status": "healthy",
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }
    except Exception as e:
        health_data["status"] = "degraded"
        health_data["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Verifica elasticsearch
    es_service = SearchService()
    if es_service.es and es_service.es.ping():
        health_data["components"]["elasticsearch"] = {
            "status": "healthy"
        }
    else:
        health_data["components"]["elasticsearch"] = {
            "status": "unavailable" if not es_service.es else "unhealthy"
        }
        if health_data["status"] == "healthy":
            health_data["status"] = "degraded"
    
    # Metriche di sistema
    health_data["metrics"] = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "response_time_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    return health_data

@router.get(
    "/readiness",
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
    "/liveness",
    summary="Probe di liveness",
    description="Verifica che il sistema sia in esecuzione",
    response_description="Stato di liveness del sistema"
)
async def liveness_probe():
    """Verifica semplice che il sistema sia in esecuzione."""
    return {"status": "alive"}