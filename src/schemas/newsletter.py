"""
Schemi per la gestione delle newsletter.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class NewsletterSubscriberBase(BaseModel):
    """Schema base per gli abbonati alla newsletter."""
    email: EmailStr = Field(..., description="Email dell'abbonato")
    first_name: Optional[str] = Field(None, max_length=100, description="Nome dell'abbonato")
    last_name: Optional[str] = Field(None, max_length=100, description="Cognome dell'abbonato")


class NewsletterSubscriberCreate(NewsletterSubscriberBase):
    """Schema per la creazione di un nuovo abbonato."""
    preferences: Optional[Dict[str, Any]] = Field(None, description="Preferenze dell'abbonato")


class NewsletterSubscriberUpdate(BaseModel):
    """Schema per l'aggiornamento di un abbonato esistente."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None


class NewsletterSubscriberResponse(NewsletterSubscriberBase):
    """Schema per la risposta con un abbonato."""
    id: uuid.UUID
    is_active: bool
    is_confirmed: bool
    created_at: datetime
    updated_at: datetime
    preferences: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class NewsletterCampaignBase(BaseModel):
    """Schema base per le campagne newsletter."""
    title: str = Field(..., min_length=3, max_length=255, description="Titolo della campagna")
    subject: str = Field(..., min_length=3, max_length=255, description="Oggetto dell'email")
    content: str = Field(..., description="Contenuto della newsletter in formato markdown")
    content_html: Optional[str] = Field(None, description="Contenuto della newsletter in formato HTML")


class NewsletterCampaignCreate(NewsletterCampaignBase):
    """Schema per la creazione di una nuova campagna."""
    scheduled_at: Optional[datetime] = Field(None, description="Data e ora di invio programmato")
    target_segment: Optional[Dict[str, Any]] = Field(None, description="Segmento target per la campagna")


class NewsletterCampaignUpdate(BaseModel):
    """Schema per l'aggiornamento di una campagna esistente."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    subject: Optional[str] = Field(None, min_length=3, max_length=255)
    content: Optional[str] = None
    content_html: Optional[str] = None
    status: Optional[str] = Field(None, description="Stato della campagna: draft, scheduled, sent, cancelled")
    scheduled_at: Optional[datetime] = None
    target_segment: Optional[Dict[str, Any]] = None


class NewsletterCampaignResponse(NewsletterCampaignBase):
    """Schema per la risposta con una campagna."""
    id: uuid.UUID
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    target_segment: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class NewsletterDeliveryBase(BaseModel):
    """Schema base per le consegne newsletter."""
    campaign_id: uuid.UUID = Field(..., description="ID della campagna")
    subscriber_id: uuid.UUID = Field(..., description="ID dell'abbonato")


class NewsletterDeliveryCreate(NewsletterDeliveryBase):
    """Schema per la creazione di una nuova consegna."""
    pass


class NewsletterDeliveryUpdate(BaseModel):
    """Schema per l'aggiornamento di una consegna esistente."""
    status: Optional[str] = Field(None, description="Stato della consegna")
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error: Optional[str] = None


class NewsletterDeliveryResponse(NewsletterDeliveryBase):
    """Schema per la risposta con una consegna."""
    id: uuid.UUID
    status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionVerificationRequest(BaseModel):
    """Schema per la richiesta di verifica dell'iscrizione."""
    email: EmailStr
    token: str


class SubscriptionStatusResponse(BaseModel):
    """Schema per la risposta con lo stato dell'iscrizione."""
    email: EmailStr
    is_subscribed: bool
    is_active: bool
    is_confirmed: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    subscribed_at: Optional[datetime] = None


class NewsletterSubscriptionsList(BaseModel):
    """Schema per la lista di abbonati."""
    items: List[NewsletterSubscriberResponse]
    total: int
    page: int
    size: int
    pages: int


class NewsletterCampaignsList(BaseModel):
    """Schema per la lista di campagne."""
    items: List[NewsletterCampaignResponse]
    total: int
    page: int
    size: int
    pages: int


class NewsletterSubscriptionBase(BaseModel):
    """Schema base per le iscrizioni alla newsletter."""
    email: EmailStr


class NewsletterSubscriptionCreate(NewsletterSubscriptionBase):
    """Schema per la creazione di una nuova iscrizione."""
    pass


class NewsletterSubscription(NewsletterSubscriptionBase):
    """Schema per una iscrizione alla newsletter."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    subscribed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NewsletterSubscriptionResponse(NewsletterSubscription):
    """Schema di risposta per le iscrizioni alla newsletter."""
    # Eredita tutti gli attributi da NewsletterSubscription
    pass


class NewsletterIssueBase(BaseModel):
    """Schema base per le edizioni della newsletter."""
    title: str
    content: str


class NewsletterIssueCreate(NewsletterIssueBase):
    """Schema per la creazione di una nuova edizione."""
    pass


class NewsletterIssue(NewsletterIssueBase):
    """Schema per una edizione della newsletter."""
    id: int
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NewsletterIssueResponse(NewsletterIssue):
    """Schema di risposta per le edizioni newsletter."""
    # Eredita tutti gli attributi da NewsletterIssue
    pass


class NewsletterIssueList(BaseModel):
    """Schema per la lista paginata di edizioni newsletter."""
    items: List[NewsletterIssueResponse]
    total: int
    page: int
    page_size: int


class NewsletterSubscriptionList(BaseModel):
    """Schema per la lista paginata di iscrizioni newsletter."""
    items: List[NewsletterSubscriptionResponse]
    total: int
    page: int
    page_size: int