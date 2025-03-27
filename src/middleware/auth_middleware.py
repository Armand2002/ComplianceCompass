# src/middleware/auth_middleware.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from src.db.session import get_db
from src.utils.jwt import decode_token
from src.models.user_model import User

# OAuth2 schema per l'estrazione del token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Ottiene l'utente corrente dal token JWT.
    
    Args:
        token (str): Token JWT
        db (Session): Sessione database
        
    Returns:
        User: Istanza dell'utente
        
    Raises:
        HTTPException: Se il token non è valido o l'utente non esiste
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: Optional[int] = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente disattivato"
        )
    
    # Aggiorna l'ultimo accesso
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica che l'utente corrente sia attivo.
    
    Args:
        current_user (User): Utente corrente
        
    Returns:
        User: Utente corrente
        
    Raises:
        HTTPException: Se l'utente non è attivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente disattivato"
        )
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica che l'utente corrente sia un amministratore.
    
    Args:
        current_user (User): Utente corrente
        
    Returns:
        User: Utente corrente
        
    Raises:
        HTTPException: Se l'utente non è un amministratore
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso riservato agli amministratori"
        )
    return current_user

async def get_current_editor_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica che l'utente corrente sia un editor o un amministratore.
    
    Args:
        current_user (User): Utente corrente
        
    Returns:
        User: Utente corrente
        
    Raises:
        HTTPException: Se l'utente non è un editor o un amministratore
    """
    if not current_user.is_editor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso riservato agli editor"
        )
    return current_user