# src/schemas/auth.py
from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, Field, constr

class UserLogin(BaseModel):
    """Schema per il login utente."""
    email: EmailStr = Field(..., description="Email dell'utente")
    password: Annotated[str, constr(min_length=8)] = Field(..., description="Password dell'utente")

class UserRegister(BaseModel):
    """Schema per la registrazione utente."""
    email: EmailStr = Field(..., description="Email dell'utente")
    username: Annotated[str, constr(min_length=3, max_length=50)] = Field(..., description="Nome utente")
    password: Annotated[str, constr(min_length=8)] = Field(..., description="Password dell'utente")
    full_name: Optional[Annotated[str, constr(max_length=100)]] = Field(None, description="Nome completo dell'utente")

class TokenData(BaseModel):
    """Schema per i dati contenuti nel token JWT."""
    sub: int  # user_id
    exp: int  # expiration time
    iat: int  # issued at time

class Token(BaseModel):
    """Schema per il token di accesso."""
    access_token: str
    token_type: str = "bearer"

class PasswordChange(BaseModel):
    """Schema per il cambio password."""
    current_password: Annotated[str, constr(min_length=8)] = Field(..., description="Password attuale")
    new_password: Annotated[str, constr(min_length=8)] = Field(..., description="Nuova password")
    confirm_password: Annotated[str, constr(min_length=8)] = Field(..., description="Conferma nuova password")

class PasswordReset(BaseModel):
    """Schema per il reset della password."""
    email: EmailStr = Field(..., description="Email dell'utente")

class PasswordResetConfirm(BaseModel):
    """Schema per la conferma del reset della password."""
    token: str = Field(..., description="Token di reset")
    new_password: Annotated[str, constr(min_length=8)] = Field(..., description="Nuova password")
    confirm_password: Annotated[str, constr(min_length=8)] = Field(..., description="Conferma nuova password")