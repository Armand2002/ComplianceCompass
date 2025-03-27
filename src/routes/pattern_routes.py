# src/routes/pattern_routes.py
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.controllers.pattern_controller import PatternController
from src.models.user_model import User
from src.middleware.auth_middleware import get_current_user, get_current_editor_user, get_current_admin_user
from src.schemas.privacy_pattern import (
    PatternCreate, 
    PatternUpdate, 
    PatternResponse, 
    PatternList
)

# Crea il router
router = APIRouter(
    prefix="/patterns",
    tags=["privacy-patterns"],
    responses={404: {"description": "Pattern non trovato"}}
)

@router.get("/", response_model=PatternList)
async def get_patterns(
    skip: int = Query(0, ge=0, description="Numero di record da saltare"),
    limit: int = Query(10, ge=1, le=100, description="Numero massimo di record da restituire"),
    strategy: Optional[str] = Query(None, description="Filtra per strategia"),
    mvc_component: Optional[str] = Query(None, description="Filtra per componente MVC"),
    gdpr_id: Optional[int] = Query(None, description="Filtra per articolo GDPR"),
    pbd_id: Optional[int] = Query(None, description="Filtra per principio PbD"),
    iso_id: Optional[int] = Query(None, description="Filtra per fase ISO"),
    vulnerability_id: Optional[int] = Query(None, description="Filtra per vulnerabilità"),
    search: Optional[str] = Query(None, description="Termine di ricerca"),
    db: Session = Depends(get_db)
):
    """
    Recupera un elenco di privacy pattern con filtri opzionali.
    
    Restituisce una lista paginata di pattern che corrispondono ai criteri di ricerca.
    """
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
        search_term=search
    )
    
    return PatternList(
        patterns=result["patterns"],
        total=result["total"],
        page=result["page"],
        size=limit,
        pages=result["pages"]
    )

@router.get("/stats")
async def get_pattern_stats(db: Session = Depends(get_db)):
    """
    Recupera statistiche sui privacy pattern.
    
    Restituisce informazioni aggregate come conteggi per strategia e componente MVC.
    """
    return PatternController.get_pattern_stats(db=db)

@router.get("/{pattern_id}", response_model=PatternResponse)
async def get_pattern(
    pattern_id: int,
    db: Session = Depends(get_db)
):
    """
    Recupera un privacy pattern specifico per ID.
    
    Restituisce i dettagli completi di un pattern, incluse tutte le relazioni.
    """
    pattern = PatternController.get_pattern(db=db, pattern_id=pattern_id)
    
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pattern con ID {pattern_id} non trovato"
        )
    
    return pattern

@router.post("/", response_model=PatternResponse, status_code=status.HTTP_201_CREATED)
async def create_pattern(
    pattern: PatternCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_editor_user)
):
    """
    Crea un nuovo privacy pattern.
    
    Richiede privilegi di editor o admin.
    """
    return PatternController.create_pattern(db=db, pattern=pattern, current_user=current_user)

@router.put("/{pattern_id}", response_model=PatternResponse)
async def update_pattern(
    pattern_id: int,
    pattern: PatternUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggiorna un privacy pattern esistente.
    
    Gli admin possono modificare qualsiasi pattern, gli editor solo quelli creati da loro.
    """
    return PatternController.update_pattern(
        db=db, 
        pattern_id=pattern_id, 
        pattern_update=pattern, 
        current_user=current_user
    )

@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pattern(
    pattern_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un privacy pattern.
    
    Gli admin possono eliminare qualsiasi pattern, gli editor solo quelli creati da loro.
    """
    PatternController.delete_pattern(db=db, pattern_id=pattern_id, current_user=current_user)
    return None

@router.get("/by-strategy/{strategy}", response_model=List[PatternResponse])
async def get_patterns_by_strategy(
    strategy: str,
    db: Session = Depends(get_db)
):
    """
    Recupera tutti i pattern con una specifica strategia.
    
    Utile per raggruppare i pattern per strategia di privacy.
    """
    result = PatternController.get_patterns(
        db=db,
        strategy=strategy
    )
    
    return result["patterns"]

@router.get("/by-mvc/{component}", response_model=List[PatternResponse])
async def get_patterns_by_mvc(
    component: str,
    db: Session = Depends(get_db)
):
    """
    Recupera tutti i pattern con un specifico componente MVC.
    
    Utile per raggruppare i pattern per componente di architettura.
    """
    result = PatternController.get_patterns(
        db=db,
        mvc_component=component
    )
    
    return result["patterns"]