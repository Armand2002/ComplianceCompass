# src/schemas/notification.py
from typing import List, Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, validator, constr

from src.models.notification import NotificationType

class NotificationBase(BaseModel):
    """Schema base per le notifiche."""
    title: Annotated[str, Field(..., min_length=1, max_length=255, description="Titolo della notifica")]
    message: Annotated[str, Field(..., min_length=1, description="Messaggio della notifica")]
    related_object_id: Optional[int] = Field(None, description="ID dell'oggetto correlato")
    related_object_type: Optional[str] = Field(None, description="Tipo dell'oggetto correlato")

class NotificationCreate(NotificationBase):
    """Schema per la creazione di una notifica."""
    user_id: int = Field(..., description="ID dell'utente destinatario")
    send_email: bool = Field(default=False, description="Se inviare un'email all'utente")

class NotificationResponse(NotificationBase):
    """Schema per la risposta con una notifica."""
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class NotificationList(BaseModel):
    """Schema per la lista di notifiche."""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int