# filepath: c:\Users\arman\Desktop\ComplianceCompass\ComplianceCompass\scripts\init_elasticsearch.py
"""
Script per inizializzare gli indici Elasticsearch e indicizzare i pattern esistenti.
"""
import sys
import os
import logging
from pathlib import Path

# Aggiungi la directory principale al PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.services.elasticsearch_init import ElasticsearchInit
from src.models.privacy_pattern import PrivacyPattern

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_elasticsearch():
    """Inizializza Elasticsearch e indicizza tutti i pattern."""
    try:
        db = SessionLocal()
        es_init = ElasticsearchInit()
        
        # Verifica connessione
        if not es_init.es or not es_init.connected:
            logger.error("Impossibile connettersi a Elasticsearch. Verifica che il servizio sia attivo.")
            return False
        
        # Crea indice se non esiste
        logger.info("Creazione indice in corso...")
        es_init.setup_indices()
            
        # Indicizza tutti i pattern
        logger.info("Indicizzazione pattern in corso...")
        patterns = db.query(PrivacyPattern).all()
        for pattern in patterns:
            es_init.index_pattern(pattern)
        
        logger.info(f"Indicizzazione completata: {len(patterns)} pattern indicizzati.")
        
        return True
    except Exception as e:
        logger.error(f"Errore nell'inizializzazione di Elasticsearch: {str(e)}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    logger.info("Inizializzazione di Elasticsearch...")
    if init_elasticsearch():
        logger.info("Inizializzazione completata con successo!")
    else:
        logger.error("Inizializzazione fallita!")
        sys.exit(1)