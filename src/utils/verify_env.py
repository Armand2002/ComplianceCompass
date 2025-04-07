"""Utility per verificare la corretta configurazione dell'ambiente."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

required_vars = [
    "DATABASE_URL", 
    "ELASTICSEARCH_URL", 
    "JWT_SECRET_KEY", 
    "JWT_ALGORITHM",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
]

def verify_env_vars():
    """Verifica che tutte le variabili d'ambiente necessarie siano impostate."""
    # Carica .env se esiste
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Variabili d'ambiente mancanti: {', '.join(missing)}")
        return False
    
    logger.info("Tutte le variabili d'ambiente necessarie sono presenti.")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_env_vars():
        print("✅ Configurazione ambiente valida")
    else:
        print("❌ Configurazione ambiente incompleta")