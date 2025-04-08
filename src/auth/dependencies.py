# src/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional

from src.db.session import get_db
from src.models.user_model import User
from src.config import settings
from src.schemas.user import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def decode_token(token: str) -> dict:
    """Decodifica un token JWT."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Ottiene l'utente corrente dal token JWT."""
    payload = decode_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Verifica che l'utente corrente sia attivo."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente non attivo",
        )
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verifica che l'utente corrente sia un amministratore."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permessi insufficienti",
        )
    return current_user

