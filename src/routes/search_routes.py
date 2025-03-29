# src/routes/search_routes.py
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from src.controllers.pattern_controller import PatternController
from src.db.session import get_db
from src.services.search_service import SearchService
from src.controllers.search_controller import SearchController
from src.schemas.privacy_pattern import PatternSearch, PatternList
from src.models.notification import NotificationType

# Crea il router
router = APIRouter(
    prefix="/search",
    tags=["ricerca"],
    responses={500: {"description": "Errore interno"}}
)

# Istanzia il servizio di ricerca
search_service = SearchService()

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
    
    Utilizza Elasticsearch per ricerche avanzate e filtri.
    """
    # Verifica se Elasticsearch è disponibile
    if search_service.es:
        # Utilizza Elasticsearch per la ricerca
        from_pos = skip
        size = limit
        
        result = search_service.search_patterns(
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
        page = skip // limit + 1
        pages = (result["total"] + limit - 1) // limit  # Ceiling division
        
        # Se non ci sono risultati con Elasticsearch, fallback alla ricerca database
        if result["total"] == 0 and q:
            # Utilizza il controller del pattern per la ricerca fallback
            from src.controllers.pattern_controller import PatternController
            db_result = PatternController.get_patterns(
                db=db,
                skip=skip,
                limit=limit,
                strategy=strategy,
                mvc_component=mvc_component,
                gdpr_id=gdpr_id,
                pbd_id=pbd_id,
                iso_id=iso_id,
                vulnerability_id=vulnerability_id,
                search_term=q
            )
            
            return PatternList(
                patterns=db_result["patterns"],
                total=db_result["total"],
                page=db_result["page"],
                size=limit,
                pages=db_result["pages"]
            )
        
        # Recupera i pattern completi dal database
        # Nota: questo è necessario perché i risultati di ES non hanno tutte le relazioni ORM
        pattern_ids = [p["id"] for p in result["results"]]
        
        if pattern_ids:
            from src.controllers.pattern_controller import PatternController
            patterns = [PatternController.get_pattern(db=db, pattern_id=pid) for pid in pattern_ids]
            patterns = [p for p in patterns if p is not None]  # Filtra eventuali None
        else:
            patterns = []
        
        return PatternList(
            patterns=patterns,
            total=result["total"],
            page=page,
            size=size,
            pages=pages
        )
    else:
        # Fallback alla ricerca nel database
        from src.controllers.pattern_controller import PatternController
        result = PatternController.get_patterns(
            db=db,
            skip=skip,
            limit=limit,
            strategy=strategy,
            mvc_component=mvc_component,
            gdpr_id=gdpr_id,
            pbd_id=pbd_id,
            iso_id=iso_id,
            vulnerability_id=vulnerability_id,
            search_term=q
        )
        
        return PatternList(
            patterns=result["patterns"],
            total=result["total"],
            page=result["page"],
            size=limit,
            pages=result["pages"]
        )

@router.post("/reindex")
async def reindex_patterns(db: Session = Depends(get_db)):
    """
    Reindicizza tutti i pattern nel search engine.
    
    Utilizzato per aggiornare l'indice dopo modifiche significative.
    Solo per uso interno/admin.
    """
    if not search_service.es:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servizio di ricerca non disponibile"
        )
    
    result = search_service.reindex_all_patterns(db=db)
    
    if result:
        return {"message": "Reindicizzazione completata con successo"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante la reindicizzazione"
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
    controller = SearchController()
    suggestions = controller.get_autocomplete_suggestions(
        db=db,
        query=q,
        limit=limit
    )
    
    return {"suggestions": suggestions}

@router.get("/trending")
async def trending_patterns(
    limit: int = Query(5, ge=1, le=20, description="Numero di pattern da restituire"),
    db: Session = Depends(get_db)
):
    """
    Restituisce i pattern più visualizzati o popolari.
    """
    controller = PatternController()
    patterns = controller.get_trending_patterns(
        db=db,
        limit=limit
    )
    
    return {"patterns": patterns}