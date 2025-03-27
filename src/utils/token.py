# Nuovo file src/utils/token.py
from datetime import datetime, timedelta
import secrets
from typing import Optional
import jwt
from src.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"

def generate_verification_token(user_id: int, expiration_hours: int = 24) -> str:
    """
    Genera un token di verifica (per reset password, verifica email, ecc.).
    
    Args:
        user_id (int): ID dell'utente
        expiration_hours (int): Ore di validità del token
        
    Returns:
        str: Token di verifica
    """
    expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
    data = {
        "sub": user_id,
        "exp": expiration,
        "type": "verification",
        "jti": secrets.token_hex(16)  # ID unico del token
    }
    
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_verification_token(token: str) -> Optional[int]:
    """
    Verifica un token di verifica e restituisce l'ID utente se valido.
    
    Args:
        token (str): Token di verifica
        
    Returns:
        Optional[int]: ID utente o None se token non valido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verifica tipo token
        if payload.get("type") != "verification":
            return None
            
        return payload.get("sub")
    except jwt.PyJWTError:
        return None