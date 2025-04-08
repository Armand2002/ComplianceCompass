# src/routes/pattern_routes.py
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status, Path, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.controllers.pattern_controller import PatternController
from src.controllers.search_controller import SearchController
from src.models.user_model import User
from src.middleware.auth_middleware import get_current_user, get_current_editor_user, get_current_admin_user
from src.schemas.privacy_pattern import (
    PatternCreate, 
    PatternUpdate, 
    PatternResponse, 
    PatternList
)

router = APIRouter(
    prefix="/patterns",
    tags=["privacy-patterns"],
    responses={
        400: {
            "description": "Richiesta non valida",
            "content": {
                "application/json": {
                    "example": {"detail": "Parametri di richiesta non validi"}
                }
            }
        },
        401: {
            "description": "Non autenticato",
            "content": {
                "application/json": {
                    "example": {"detail": "Autenticazione richiesta"}
                }
            }
        },
        403: {
            "description": "Non autorizzato",
            "content": {
                "application/json": {
                    "example": {"detail": "Permessi insufficienti"}
                }
            }
        },
        404: {
            "description": "Pattern non trovato",
            "content": {
                "application/json": {
                    "example": {"detail": "Pattern non trovato"}
                }
            }
        },
        500: {
            "description": "Errore interno del server",
            "content": {
                "application/json": {
                    "example": {"detail": "Si è verificato un errore interno"}
                }
            }
        }
    }
)

@router.get(
    "/",
    response_model=PatternList,
    summary="Recupera elenco privacy patterns",
    description="Restituisce una lista paginata di privacy patterns con filtri opzionali",
    response_description="Lista di privacy patterns con metadati di paginazione"
)
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
    
    Parametri di filtro:
    - **skip**: Posizione di partenza per paginazione
    - **limit**: Numero massimo di risultati da restituire
    - **strategy**: Filtra per strategia di privacy
    - **mvc_component**: Filtra per componente MVC
    - **gdpr_id**: Filtra per ID articolo GDPR
    - **pbd_id**: Filtra per ID principio Privacy by Design
    - **iso_id**: Filtra per ID fase ISO
    - **vulnerability_id**: Filtra per ID vulnerabilità
    - **search**: Termine di ricerca testuale
    
    Restituisce una lista paginata di pattern che corrispondono ai criteri di ricerca.
    """
    try:
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
    except Exception as e:
        # Log dettagliato dell'errore (omesso per brevità)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nel recupero dei pattern",
                "error_type": type(e).__name__,
                "error_details": str(e) if not isinstance(e, HTTPException) else None
            }
        )

@router.get(
    "/stats",
    summary="Recupera statistiche sui privacy patterns",
    description="Restituisce informazioni aggregate come conteggi per strategia e componente MVC",
    response_description="Statistiche aggregate sui pattern"
)
async def get_pattern_stats(db: Session = Depends(get_db)):
    """
    Recupera statistiche sui privacy pattern.
    
    Restituisce informazioni aggregate come:
    - Conteggio per strategia
    - Conteggio per componente MVC
    - Distribuzione per principio PbD
    - Distribuzione per articolo GDPR
    """
    try:
        return PatternController.get_pattern_stats(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nel recupero delle statistiche",
                "error_type": type(e).__name__,
                "error_details": str(e) if not isinstance(e, HTTPException) else None
            }
        )

@router.get(
    "/{pattern_id}",
    response_model=PatternResponse,
    summary="Recupera dettagli di un privacy pattern specifico",
    description="Restituisce i dettagli completi di un privacy pattern specifico in base all'ID"
)
async def get_pattern(
    pattern_id: int = Path(..., title="Pattern ID", description="ID univoco del pattern da recuperare", gt=0),
    db: Session = Depends(get_db)
):
    """
    Recupera un privacy pattern specifico per ID.
    
    Parametri:
    - **pattern_id**: ID univoco del privacy pattern da recuperare
    
    Restituisce i dettagli completi del pattern, incluse tutte le relazioni.
    Genera errore 404 se il pattern non esiste.
    """
    pattern = PatternController.get_pattern(db=db, pattern_id=pattern_id)
    
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Pattern con ID {pattern_id} non trovato",
                "code": "PATTERN_NOT_FOUND",
                "params": {"pattern_id": pattern_id}
            }
        )
    
    return pattern

@router.post(
    "/", 
    response_model=PatternResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuovo privacy pattern",
    description="Crea un nuovo privacy pattern con i dati forniti (richiede privilegi di editor o admin)",
    response_description="Privacy pattern creato con successo"
)
async def create_pattern(
    pattern: PatternCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_editor_user)
):
    """
    Crea un nuovo privacy pattern.
    
    Richiede privilegi di editor o admin.
    
    Il pattern creato sarà associato all'utente corrente come autore.
    """
    try:
        return PatternController.create_pattern(db=db, pattern=pattern, current_user=current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if "validation" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nella creazione del pattern",
                "error_type": type(e).__name__,
                "error_details": str(e) if not isinstance(e, HTTPException) else None
            }
        )

@router.put(
    "/{pattern_id}", 
    response_model=PatternResponse,
    summary="Aggiorna un privacy pattern esistente",
    description="Aggiorna un pattern esistente (admin possono modificare qualsiasi pattern, editor solo i propri)",
    response_description="Pattern aggiornato con successo"
)
async def update_pattern(
    pattern_id: int = Path(..., title="Pattern ID", description="ID univoco del pattern da aggiornare"),
    pattern: PatternUpdate = Body(..., description="Dati aggiornati del pattern"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggiorna un privacy pattern esistente.
    
    Gli admin possono modificare qualsiasi pattern, gli editor solo quelli creati da loro.
    
    Parametri:
    - **pattern_id**: ID univoco del pattern da aggiornare
    - **pattern**: Dati aggiornati del pattern
    """
    try:
        return PatternController.update_pattern(
            db=db, 
            pattern_id=pattern_id, 
            pattern_update=pattern, 
            current_user=current_user
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nell'aggiornamento del pattern",
                "error_type": type(e).__name__,
                "error_details": str(e)
            }
        )

@router.delete(
    "/{pattern_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina un privacy pattern",
    description="Elimina definitivamente un pattern (richiede privilegi di admin)",
    response_description="Pattern eliminato con successo (nessun contenuto)"
)
async def delete_pattern(
    pattern_id: int = Path(..., title="Pattern ID", description="ID univoco del pattern da eliminare"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Elimina un privacy pattern.
    
    Richiede permesso di amministratore.
    
    L'eliminazione è permanente e non può essere annullata.
    """
    try:
        PatternController.delete_pattern(db=db, pattern_id=pattern_id, current_user=current_user)
        return None
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nell'eliminazione del pattern",
                "error_type": type(e).__name__,
                "error_details": str(e)
            }
        )

@router.get(
    "/by-strategy/{strategy}", 
    response_model=List[PatternResponse],
    summary="Recupera pattern per strategia",
    description="Restituisce tutti i pattern con una specifica strategia di privacy",
    response_description="Lista di pattern con la strategia specificata"
)
async def get_patterns_by_strategy(
    strategy: str = Path(..., title="Strategia", description="Nome della strategia di privacy"),
    db: Session = Depends(get_db)
):
    """
    Recupera tutti i pattern con una specifica strategia.
    
    Parametri:
    - **strategy**: Nome della strategia di privacy (es. "Minimization", "Transparency", "Control")
    
    Utile per raggruppare i pattern per strategia di privacy.
    """
    try:
        result = PatternController.get_patterns(
            db=db,
            strategy=strategy
        )
        
        return result["patterns"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nel recupero dei pattern per strategia",
                "error_type": type(e).__name__,
                "error_details": str(e) if not isinstance(e, HTTPException) else None
            }
        )

@router.get(
    "/by-mvc/{component}", 
    response_model=List[PatternResponse],
    summary="Recupera pattern per componente MVC",
    description="Restituisce tutti i pattern associati a un specifico componente dell'architettura MVC",
    response_description="Lista di pattern per il componente MVC specificato"
)
async def get_patterns_by_mvc(
    component: str = Path(..., title="Componente MVC", description="Componente MVC (Model, View, Controller)"),
    db: Session = Depends(get_db)
):
    """
    Recupera tutti i pattern con un specifico componente MVC.
    
    Parametri:
    - **component**: Componente MVC (valori accettati: "Model", "View", "Controller")
    
    Utile per raggruppare i pattern per componente di architettura.
    """
    try:
        result = PatternController.get_patterns(
            db=db,
            mvc_component=component
        )
        
        return result["patterns"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nel recupero dei pattern per componente MVC",
                "error_type": type(e).__name__,
                "error_details": str(e) if not isinstance(e, HTTPException) else None
            }
        )

@router.get(
    "/by-category", 
    response_model=List[PatternResponse],
    summary="Recupera pattern per categoria",
    description="Restituisce tutti i pattern in una specifica categoria",
    response_description="Lista di pattern nella categoria specificata"
)
async def get_patterns_by_category(
    category: str = Query(..., title="Categoria", description="Categoria di pattern"),
    db: Session = Depends(get_db)
):
    """
    Recupera tutti i pattern in una specifica categoria.
    
    Parametri:
    - **category**: Categoria di pattern (es. "Authentication", "Data Protection", "Consent")
    
    Utile per visualizzazioni organizzate per categoria.
    """
    try:
        result = PatternController.get_patterns_by_category(
            db=db,
            category=category
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nel recupero dei pattern per categoria",
                "error_type": type(e).__name__,
                "error_details": str(e) if not isinstance(e, HTTPException) else None
            }
        )

@router.get(
    "/related/{pattern_id}", 
    response_model=List[PatternResponse],
    summary="Recupera pattern correlati",
    description="Restituisce pattern correlati al pattern specificato in base a tag, categorie e relazioni GDPR comuni",
    response_description="Lista di pattern correlati"
)
async def get_related_patterns(
    pattern_id: int = Path(..., title="Pattern ID", description="ID univoco del pattern di riferimento"),
    limit: int = Query(5, ge=1, le=20, title="Limite", description="Numero massimo di pattern correlati"),
    db: Session = Depends(get_db)
):
    """
    Recupera pattern correlati al pattern specificato.
    
    Parametri:
    - **pattern_id**: ID del pattern di riferimento
    - **limit**: Numero massimo di pattern correlati da restituire
    
    La correlazione è basata su tag, categorie e relazioni GDPR comuni.
    """
    try:
        pattern = PatternController.get_pattern(db=db, pattern_id=pattern_id)
        
        if not pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Pattern non trovato",
                    "code": "PATTERN_NOT_FOUND",
                    "params": {"pattern_id": pattern_id}
                }
            )
        
        related = PatternController.get_related_patterns(
            db=db,
            pattern=pattern,
            limit=limit
        )
        
        return related
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Errore nel recupero dei pattern correlati",
                "error_type": type(e).__name__,
                "error_details": str(e)
            }
        )