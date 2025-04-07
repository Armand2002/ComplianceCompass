# src/controllers/search_controller.py
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from src.services.search_service import SearchService
from src.models.privacy_pattern import PrivacyPattern

logger = logging.getLogger(__name__)

class SearchController:
    """
    Controller per la gestione delle ricerche.
    Aggiornato per utilizzare la ricerca basata su SQL invece di Elasticsearch.
    """
    
    def __init__(self):
        """Inizializza il controller con il servizio di ricerca."""
        self.search_service = SearchService()
    
    def search_patterns(
        self, 
        db: Session,
        query: Optional[str] = None,
        strategy: Optional[str] = None,
        mvc_component: Optional[str] = None,
        gdpr_id: Optional[int] = None,
        pbd_id: Optional[int] = None,
        iso_id: Optional[int] = None,
        vulnerability_id: Optional[int] = None,
        from_pos: int = 0,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Cerca privacy patterns.
        
        Args:
            db (Session): Sessione database
            query (str, optional): Query di ricerca
            strategy (str, optional): Filtra per strategia
            mvc_component (str, optional): Filtra per componente MVC
            gdpr_id (int, optional): Filtra per articolo GDPR
            pbd_id (int, optional): Filtra per principio PbD
            iso_id (int, optional): Filtra per fase ISO
            vulnerability_id (int, optional): Filtra per vulnerabilità
            from_pos (int): Posizione di partenza per i risultati
            size (int): Numero di risultati da restituire
            
        Returns:
            Dict[str, Any]: Risultati della ricerca
        """
        # Utilizziamo direttamente il servizio SQL
        return self.search_service.search_patterns(
            db=db,
            query=query,
            strategy=strategy,
            mvc_component=mvc_component,
            gdpr_id=gdpr_id,
            pbd_id=pbd_id,
            iso_id=iso_id,
            vulnerability_id=vulnerability_id,
            from_pos=from_pos,
            size=size
        )
    
    def get_autocomplete_suggestions(
        self, 
        db: Session,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Genera suggerimenti di autocompletamento.
        
        Args:
            db (Session): Sessione database
            query (str): Query parziale
            limit (int): Numero massimo di suggerimenti
            
        Returns:
            List[Dict[str, Any]]: Lista di suggerimenti
        """
        return self.search_service.get_autocomplete_suggestions(
            db=db,
            query=query,
            limit=limit
        )
    
    # Questi metodi sono mantenuti per compatibilità
    def index_pattern(self, pattern: PrivacyPattern) -> bool:
        """Stub per compatibilità."""
        return True
    
    def remove_pattern_from_index(self, pattern_id: int) -> bool:
        """Stub per compatibilità."""
        return True
    
    def reindex_all_patterns(self, db: Session) -> bool:
        """Stub per compatibilità."""
        return True