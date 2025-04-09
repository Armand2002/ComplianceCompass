"""Servizio centralizzato per le operazioni relative agli articoli GDPR."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.models.gdpr_model import GDPRArticle
from src.utils.cache import Cache

# Configurazione del logger
logger = logging.getLogger(__name__)

# Istanza di cache centralizzata
cache = Cache()

class GDPRService:
    """
    Servizio centralizzato per operazioni relative agli articoli GDPR.
    Implementa pattern di resilienza e caching.
    """
    
    @staticmethod
    @cache.cached(ttl=300)  # Cache per 5 minuti
    def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Recupera articoli GDPR con gestione degli errori e caching.
        
        Args:
            db: Sessione database
            skip: Numero di record da saltare
            limit: Numero massimo di record da restituire
            
        Returns:
            Lista di articoli GDPR come dizionari
        """
        try:
            articles = db.query(GDPRArticle).order_by(GDPRArticle.number).offset(skip).limit(limit).all()
            return [article.to_dict() for article in articles]
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_articles: {str(e)}")
            # Implementazione circuit breaker: ritorna dati vuoti in caso di errore
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_articles: {str(e)}")
            return []
    
    @staticmethod
    @cache.cached(ttl=300)
    def get_article(db: Session, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera un articolo specifico per ID con gestione degli errori.
        
        Args:
            db: Sessione database
            article_id: ID dell'articolo da recuperare
            
        Returns:
            Articolo come dizionario o None se non trovato
        """
        try:
            article = db.query(GDPRArticle).filter(GDPRArticle.id == article_id).first()
            return article.to_dict() if article else None
        except Exception as e:
            logger.error(f"Error retrieving article {article_id}: {str(e)}")
            return None
            
    @staticmethod
    @cache.cached(ttl=300)
    def get_article_by_number(db: Session, article_number: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un articolo specifico per numero con gestione degli errori.
        
        Args:
            db: Sessione database
            article_number: Numero dell'articolo (es. "5.1.a")
            
        Returns:
            Articolo come dizionario o None se non trovato
        """
        try:
            article = GDPRArticle.get_by_number(db, article_number)
            return article.to_dict() if article else None
        except Exception as e:
            logger.error(f"Error retrieving article by number {article_number}: {str(e)}")
            return None