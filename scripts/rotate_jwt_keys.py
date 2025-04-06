#!/usr/bin/env python
# scripts/rotate_jwt_keys.py
"""
Script per rotazione pianificata delle chiavi JWT.

Questo script dovrebbe essere eseguito periodicamente (es. cron settimanale)
per rotare automaticamente le chiavi JWT, migliorando la sicurezza.
"""
import os
import sys
import logging
from datetime import datetime

# Aggiungi la directory principale al path per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.jwt import key_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("jwt_rotation")

def main():
    """Ruota le chiavi JWT."""
    try:
        logger.info("Starting JWT key rotation")
        
        # Ottieni info chiavi attuali
        current_keys = key_manager.get_keys_info()
        logger.info(f"Current keys: {current_keys}")
        
        # Esegui rotazione
        result = key_manager.rotate_keys()
        
        # Log risultato
        logger.info(f"JWT key rotation completed: {result}")
        
        # Stampa a stdout per eventuali log di sistema
        print(f"JWT key rotation completed successfully at {datetime.utcnow().isoformat()}")
        print(f"Old key ID: {result['old_key_id']}")
        print(f"New key ID: {result['new_key_id']}")
        
        return 0
    except Exception as e:
        logger.error(f"Error during JWT key rotation: {str(e)}", exc_info=True)
        print(f"JWT key rotation failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())