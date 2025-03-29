# src/schemas/user.py
from typing import Any, Dict, Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from pydantic.types import constr
from enum import Enum

class UserRole(str, Enum):
    """Ruoli utente disponibili nel sistema."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class UserBase(BaseModel):
    """Schema base per gli utenti."""
    email: EmailStr = Field(..., description="Email dell'utente")
    username: str = Field(..., min_length=3, max_length=50, description="Nome utente")
    full_name: Optional[str] = Field(None, max_length=100, description="Nome completo dell'utente")
    bio: Optional[str] = Field(None, description="Biografia dell'utente")
    avatar_url: Optional[str] = Field(None, description="URL dell'avatar dell'utente")

class UserCreate(UserBase):
    """Schema per la creazione di un nuovo utente."""
    password: str = Field(..., min_length=8, description="Password dell'utente")
    role: UserRole = Field(default=UserRole.VIEWER, description="Ruolo dell'utente")

class UserUpdate(BaseModel):
    """Schema per l'aggiornamento di un utente esistente."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

# Schema per la risposta (esclusi dati sensibili)
class UserResponse(UserBase):
    """Schema per la risposta con un utente."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

# Schema per la lista di utenti
class UserList(BaseModel):
    """Schema per la lista di utenti."""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int

# Schema per il profilo utente
class UserProfile(UserResponse):
    """Schema per il profilo utente completo."""
    created_patterns_count: int = 0

    class Config:
        orm_mode = True

# Schema per l'attività utente
class UserActivityResponse(BaseModel):
    """Schema per l'attività utente."""
    viewed_patterns: List[Dict[str, Any]]
    recent_searches: List[str]
    contributions: List[Dict[str, Any]]
    last_login: Optional[datetime] = None