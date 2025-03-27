# src/routes/chatbot_routes.py
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.chatbot_service import ChatbotService
from src.models.user_model import User
from src.middleware.auth_middleware import get_current_user
from src.schemas.chatbot import ChatRequest, ChatResponse

# Crea il router
router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
    responses={401: {"description": "Non autorizzato"}}
)

# Istanzia il servizio chatbot
chatbot_service = ChatbotService()

@router.post("/chat", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Invia un messaggio al chatbot e ottiene una risposta.
    
    Il chatbot può rispondere a domande su Privacy Patterns, GDPR e normative correlate.
    """
    # Ottieni risposta dal chatbot
    response = chatbot_service.get_response(
        db=db,
        message=request.message,
        conversation_history=request.conversation_history
    )
    
    return ChatResponse(
        response=response["response"],
        source=response.get("source", "chatbot"),
        pattern_id=response.get("pattern_id"),
        pattern_title=response.get("pattern_title"),
        article_id=response.get("article_id"),
        article_number=response.get("article_number")
    )

@router.get("/suggestions", response_model=List[Dict[str, Any]])
async def get_pattern_suggestions(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ottiene suggerimenti di Privacy Patterns basati sulla query dell'utente.
    
    Utile per suggerire pattern correlati alle domande dell'utente.
    """
    suggestions = chatbot_service.get_pattern_suggestions(db=db, query=query)
    return suggestions