# src/utils/jwt.py
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt 
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

# Configurazioni JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "compliance_compass_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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