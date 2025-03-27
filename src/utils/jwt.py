# src/utils/jwt.py
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt 
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

# Configurazioni JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "compliance_compass_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

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
    to_encode.update({"exp": expire})
    
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

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Crea un refresh token JWT per l'autenticazione persistente.
    
    Args:
        data (dict): Dati da includere nel token
        
    Returns:
        str: Refresh token JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
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