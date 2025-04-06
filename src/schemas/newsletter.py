# src/schemas/newsletter.py
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List

# Base schemas
class NewsletterSubscriptionBase(BaseModel):
    """Schema base per le iscrizioni alla newsletter."""
    email: EmailStr = Field(..., description="Email dell'utente iscritto")

class NewsletterIssueBase(BaseModel):
    """Schema base per le edizioni della newsletter."""
    subject: str = Field(..., min_length=3, max_length=255, description="Oggetto della newsletter")
    content: str = Field(..., min_length=50, description="Contenuto HTML della newsletter")

# Create schemas
class NewsletterSubscriptionCreate(NewsletterSubscriptionBase):
    """Schema per la creazione di una nuova iscrizione alla newsletter."""
    pass

class NewsletterIssueCreate(NewsletterIssueBase):
    """Schema per la creazione di una nuova edizione della newsletter."""
    pass

# Update schemas
class NewsletterSubscriptionUpdate(BaseModel):
    """Schema per l'aggiornamento di un'iscrizione alla newsletter."""
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class NewsletterIssueUpdate(BaseModel):
    """Schema per l'aggiornamento di un'edizione della newsletter."""
    subject: Optional[str] = Field(None, min_length=3, max_length=255)
    content: Optional[str] = Field(None, min_length=50)
    sent_at: Optional[datetime] = None

# Response schemas
class NewsletterSubscriptionResponse(NewsletterSubscriptionBase):
    """Schema per la risposta con un'iscrizione alla newsletter."""
    id: int
    is_active: bool
    is_verified: bool
    subscribed_at: datetime
    last_updated_at: datetime
    user_id: Optional[int] = None
    
    class Config:
        orm_mode = True

class NewsletterIssueResponse(NewsletterIssueBase):
    """Schema per la risposta con un'edizione della newsletter."""
    id: int
    sent_at: Optional[datetime] = None
    created_at: datetime
    created_by_id: int
    
    class Config:
        orm_mode = True

# List schemas
class NewsletterSubscriptionList(BaseModel):
    """Schema per la lista di iscrizioni alla newsletter."""
    items: List[NewsletterSubscriptionResponse]
    total: int
    page: int
    page_size: int
    
    class Config:
        orm_mode = True

class NewsletterIssueList(BaseModel):
    """Schema per la lista di edizioni della newsletter."""
    items: List[NewsletterIssueResponse]
    total: int
    page: int
    page_size: int
    
    class Config:
        orm_mode = True