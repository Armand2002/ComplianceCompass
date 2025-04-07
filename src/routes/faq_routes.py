# src/routes/faq_routes.py
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.controllers.faq_controller import FAQController
from src.models.user_model import User
from src.middleware.auth_middleware import get_current_user

# Crea il router
router = APIRouter(
    prefix="/faq",
    tags=["faq"],
    responses={404: {"description": "Non trovato"}}
)

# Istanzia il controller
faq_controller = FAQController()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_faqs():
    """
    Ottiene l'elenco completo delle FAQ.
    """
    return faq_controller.get_all_faqs()

@router.get("/{faq_id}", response_model=Dict[str, Any])
async def get_faq_by_id(faq_id: int):
    """
    Ottiene una FAQ specifica per ID.
    
    Args:
        faq_id (int): ID della FAQ
    """
    faq = faq_controller.get_faq_by_id(faq_id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FAQ con ID {faq_id} non trovata"
        )
    return faq

@router.get("/search/", response_model=Dict[str, Any])
async def search_faqs(q: Optional[str] = Query(None, description="Termine di ricerca")):
    """
    Cerca tra le FAQ in base a una query.
    
    Args:
        q (str, optional): Termine di ricerca
    """
    return faq_controller.search_faqs(q or "")

@router.post("/ask", response_model=Dict[str, Any])
async def ask_question(
    query: str = Query(..., description="Domanda dell'utente")
):
    """
    Ottiene una risposta alla domanda dell'utente.
    Questo endpoint sostituisce il chatbot con risposte basate sulle FAQ.
    
    Args:
        query (str): Domanda dell'utente
    """
    return faq_controller.get_response_for_query(query)