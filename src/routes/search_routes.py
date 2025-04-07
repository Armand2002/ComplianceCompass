# src/routes/search_routes.py
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
import logging
from src.db.session import get_db
from src.controllers.search_controller import SearchController
from src.schemas.privacy_pattern import PatternSearch, PatternList

logger = logging.getLogger(__name__)

# Crea il router
router = APIRouter(
    prefix="/search",
    tags=["ricerca"],
    responses={500: {"description": "Errore interno"}}
)

# Istanzia il controller di ricerca
search_controller = SearchController()

@router.get("/patterns", response_model=PatternList)
async def search_patterns(
    q: Optional[str] = Query(None, description="Query di ricerca"),
    skip: int = Query(0, ge=0, description="Numero di record da saltare"),
    limit: int = Query(10, ge=1, le=100, description="Numero massimo di record da restituire"),
    strategy: Optional[str] = Query(None, description="Filtra per strategia"),
    mvc_component: Optional[str] = Query(None, description="Filtra per componente MVC"),
    gdpr_id: Optional[int] = Query(None, description="Filtra per articolo GDPR"),
    pbd_id: Optional[int] = Query(None, description="Filtra per principio PbD"),
    iso_id: Optional[int] = Query(None, description="Filtra per fase ISO"),
    vulnerability_id: Optional[int] = Query(None, description="Filtra per vulnerabilità"),
    db: Session = Depends(get_db)
):
    """
    Cerca privacy patterns con ricerca full-text.
    
    Utilizza query SQL per le ricerche e i filtri.
    """
    from_pos = skip
    size = limit
    
    result = search_controller.search_patterns(
        db=db,
        query=q,
        strategy=strategy,
        mvc_component=mvc_component,
        gdpr_id=gdpr_id,
        pbd_id=pbd_id,
        iso_id=iso_id,
        vulnerability_id=vulnerability_id,
        from_pos=from_pos,
        size=size
    )
    
    # Calcola informazioni di paginazione
    page = skip // limit + 1 if limit > 0 else 1
    pages = (result["total"] + limit - 1) // limit if limit > 0 else 1  # Ceiling division
    
    # Recuperare i pattern completi dal database
    pattern_ids = [p["id"] for p in result["results"]]
    
    from src.controllers.pattern_controller import PatternController
    patterns = []
    
    if pattern_ids:
        patterns = [PatternController.get_pattern(db=db, pattern_id=pid) for pid in pattern_ids]
        patterns = [p for p in patterns if p is not None]  # Filtra eventuali None
    
    return PatternList(
        patterns=patterns,
        total=result["total"],
        page=page,
        size=size,
        pages=pages
    )

@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=2, description="Query di ricerca"),
    limit: int = Query(10, ge=1, le=20, description="Numero massimo di suggerimenti"),
    db: Session = Depends(get_db)
):
    """
    Fornisce suggerimenti di autocompletamento basati sulla query.
    """
    suggestions = search_controller.get_autocomplete_suggestions(
        db=db,
        query=q,
        limit=limit
    )
    
    return {"suggestions": suggestions}

# Mantenuto per compatibilità con l'interfaccia esistente
@router.post("/reindex")
async def reindex_patterns(db: Session = Depends(get_db)):
    """
    Endpoint stub che simula la reindicizzazione.
    Mantenuto per compatibilità con l'interfaccia esistente.
    """
    return {"message": "Operazione completata con successo"}