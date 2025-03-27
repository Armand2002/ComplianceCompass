# src/schemas/chatbot.py
from typing import List, Dict, Optional, Annotated
from pydantic import BaseModel, Field, constr

class ChatRequest(BaseModel):
    """Schema per una richiesta al chatbot."""
    message: Annotated[str, constr(min_length=1)] = Field(..., description="Messaggio dell'utente")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=[],
        description="Storico della conversazione in formato [{role: 'user|assistant', content: '...'}]"
    )

class ChatResponse(BaseModel):
    """Schema per una risposta del chatbot."""
    response: str = Field(..., description="Risposta del chatbot")
    source: str = Field(default="chatbot", description="Fonte della risposta (chatbot, pattern, gdpr, ai_api, fallback)")
    pattern_id: Optional[int] = Field(None, description="ID del pattern se la risposta è basata su un pattern")
    pattern_title: Optional[str] = Field(None, description="Titolo del pattern se la risposta è basata su un pattern")
    article_id: Optional[int] = Field(None, description="ID dell'articolo GDPR se la risposta è basata su un articolo")
    article_number: Optional[str] = Field(None, description="Numero dell'articolo GDPR se la risposta è basata su un articolo")