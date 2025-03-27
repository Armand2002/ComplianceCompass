# src/utils/password.py
from passlib.context import CryptContext

# Contesto per l'hashing delle password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se una password in chiaro corrisponde a una hash.
    
    Args:
        plain_password (str): Password in chiaro
        hashed_password (str): Hash della password
        
    Returns:
        bool: True se la password è corretta, False altrimenti
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Crea un hash sicuro per la password.
    
    Args:
        password (str): Password in chiaro
        
    Returns:
        str: Hash della password
    """
    return pwd_context.hash(password)