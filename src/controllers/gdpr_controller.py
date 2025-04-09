"""Controller per la gestione degli articoli GDPR."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
import logging

from src.models.gdpr_model import GDPRArticle
from src.controllers.base_controller import BaseController
from src.services.gdpr_service import GDPRService

# Configurazione del logger
logger = logging.getLogger(__name__)

class GDPRController(BaseController[GDPRArticle]):
    """
    Controller per la gestione degli articoli GDPR.
    """
    model_class = GDPRArticle
    
    @staticmethod
    def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Recupera una lista paginata di articoli GDPR, delegando al service.
        
        Args:
            db: Sessione database
            skip: Numero di record da saltare
            limit: Numero massimo di record da restituire
            
        Returns:
            Lista di articoli GDPR come dizionari
        """
        return GDPRService.get_articles(db, skip, limit)
    
    @staticmethod
    def get_article(db: Session, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera un articolo specifico per ID, delegando al service.
        
        Args:
            db: Sessione database
            article_id: ID dell'articolo da recuperare
            
        Returns:
            Articolo come dizionario o None se non trovato
        """
        return GDPRService.get_article(db, article_id)
    
    @staticmethod
    def get_article_by_number(db: Session, article_number: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un articolo specifico per numero, delegando al service.
        
        Args:
            db: Sessione database
            article_number: Numero dell'articolo (es. "5.1.a")
            
        Returns:
            Articolo come dizionario o None se non trovato
        """
        return GDPRService.get_article_by_number(db, article_number)