# src/routes/newsletter_routes.py
from fastapi import APIRouter, Depends, Query, HTTPException, status, Path, Body
from sqlalchemy.orm import Session
from pydantic import EmailStr
from typing import Dict, Any, List, Optional

from src.db.session import get_db
from src.controllers.newsletter_controller import NewsletterController
from src.schemas.newsletter import (
    NewsletterSubscriptionCreate,
    NewsletterSubscriptionResponse,
    NewsletterIssueCreate,
    NewsletterIssueResponse,
    NewsletterSubscriptionList,
    NewsletterIssueList
)
from src.auth.dependencies import get_current_active_user, get_current_admin_user
from src.schemas.user import UserResponse

router = APIRouter(
    prefix="/newsletter",
    tags=["newsletter"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"}
    }
)

newsletter_controller = NewsletterController()

@router.post("/subscribe", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def subscribe_newsletter(
    subscription: NewsletterSubscriptionCreate,
    db: Session = Depends(get_db)
):
    """
    Iscrive un utente alla newsletter.
    
    Args:
        subscription: Dati iscrizione (email)
        db: Sessione database
        
    Returns:
        Informazioni sull'esito dell'iscrizione
    """
    return newsletter_controller.subscribe(db, subscription.email)

@router.delete("/unsubscribe", response_model=Dict[str, Any])
async def unsubscribe_newsletter(
    email: EmailStr = Query(..., description="Email da disiscrivere"), 
    db: Session = Depends(get_db)
):
    """
    Cancella l'iscrizione di un utente dalla newsletter.
    
    Args:
        email: Email da disiscrivere
        db: Sessione database
        
    Returns:
        Informazioni sull'esito della cancellazione
    """
    return newsletter_controller.unsubscribe(db, email)

@router.post("/verify", response_model=Dict[str, Any])
async def verify_newsletter_subscription(
    email: EmailStr = Query(..., description="Email da verificare"),
    token: str = Query(..., description="Token di verifica"),
    db: Session = Depends(get_db)
):
    """
    Verifica l'iscrizione alla newsletter tramite token.
    
    Args:
        email: Email da verificare
        token: Token di verifica
        db: Sessione database
        
    Returns:
        Informazioni sull'esito della verifica
    """
    return newsletter_controller.verify_subscription(db, email, token)

@router.get("/status", response_model=Dict[str, Any])
async def get_newsletter_status(
    email: EmailStr = Query(..., description="Email da controllare"),
    db: Session = Depends(get_db)
):
    """
    Verifica lo stato dell'iscrizione alla newsletter.
    
    Args:
        email: Email da controllare
        db: Sessione database
        
    Returns:
        Stato dell'iscrizione alla newsletter
    """
    return newsletter_controller.get_subscription_status(db, email)

# --- Rotte per amministratori ---

@router.get("/subscriptions", response_model=NewsletterSubscriptionList)
async def get_newsletter_subscriptions(
    skip: int = Query(0, ge=0, description="Numero di record da saltare"),
    limit: int = Query(100, ge=1, le=100, description="Numero massimo di record da restituire"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Ottiene la lista delle iscrizioni attive alla newsletter.
    
    Args:
        skip: Numero di record da saltare (paginazione)
        limit: Numero massimo di record da restituire
        db: Sessione database
        current_user: Utente corrente (admin)
        
    Returns:
        Lista delle iscrizioni attive
    """
    return newsletter_controller.get_active_subscriptions(db, skip, limit)

@router.post("/issues", status_code=status.HTTP_201_CREATED, response_model=NewsletterIssueResponse)
async def create_newsletter_issue(
    newsletter_data: NewsletterIssueCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Crea una nuova edizione della newsletter.
    
    Args:
        newsletter_data: Dati della newsletter (subject, content)
        db: Sessione database
        current_user: Utente corrente (admin)
        
    Returns:
        Dettagli della newsletter creata
    """
    return newsletter_controller.create_newsletter_issue(db, newsletter_data, current_user.id)

@router.post("/issues/{issue_id}/send", response_model=Dict[str, Any])
async def send_newsletter_issue(
    issue_id: int = Path(..., description="ID della newsletter da inviare"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    Invia una newsletter a tutti gli iscritti attivi.
    
    Args:
        issue_id: ID della newsletter da inviare
        db: Sessione database
        current_user: Utente corrente (admin)
        
    Returns:
        Risultato dell'invio
    """
    return newsletter_controller.send_newsletter_issue(db, issue_id)