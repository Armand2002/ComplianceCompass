# src/utils/jwt.py
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt 
import secrets
from src.config import settings

# Configurazioni JWT
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT per l'autenticazione.
    
    Args:
        data (dict): Dati da includere nel token
        expires_delta (timedelta, optional): Durata validità token
        
    Returns:
        str: Token JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_hex(8)  # JWT ID per possibile invalidazione token
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica un token JWT.
    
    Args:
        token (str): Token JWT
        
    Returns:
        dict: Dati contenuti nel token
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un refresh token JWT per l'autenticazione persistente.
    
    Args:
        data (dict): Dati da includere nel token
        expires_delta (timedelta, optional): Durata validità token
        
    Returns:
        str: Refresh token JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_hex(8),
        "token_type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica un token JWT e restituisce i dati se valido.
    
    Args:
        token (str): Token JWT
        
    Returns:
        Optional[Dict[str, Any]]: Dati dal token o None se non valido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None