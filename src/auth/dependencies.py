# src/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user_model import User
from src.utils.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Ottiene l'utente corrente dal token JWT.
    
    Args:
        token (str): Token JWT
        db (Session): Sessione database
        
    Returns:
        User: Utente autenticato
        
    Raises:
        HTTPException: Se l'autenticazione fallisce
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token di autenticazione non valido",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token di autenticazione non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    Verifica che l'utente corrente sia un admin.
    
    Args:
        current_user (User): Utente corrente
        
    Returns:
        User: Utente admin
        
    Raises:
        HTTPException: Se l'utente non è un admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permessi insufficienti. Richiesti privilegi di amministratore"
        )
    
    return current_user