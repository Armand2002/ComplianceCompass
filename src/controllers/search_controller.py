# src/controllers/search_controller.py
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from src.services.search_service import SearchService
from src.models.privacy_pattern import PrivacyPattern

# Crea un logger per questo modulo
logger = logging.getLogger(__name__)

class SearchController:
    """
    Controller per la gestione delle ricerche.
    
    Gestisce la logica di business per le ricerche.
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
        if self.search_service.es:
            # Utilizza Elasticsearch per la ricerca
            result = self.search_service.search_patterns(
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
            
            return result
        else:
            # Fallback alla ricerca nel database
            from src.controllers.pattern_controller import PatternController
            
            # Calcola skip e limit
            skip = from_pos
            limit = size
            
            result = PatternController.get_patterns(
                db=db,
                skip=skip,
                limit=limit,
                strategy=strategy,
                mvc_component=mvc_component,
                gdpr_id=gdpr_id,
                pbd_id=pbd_id,
                iso_id=iso_id,
                vulnerability_id=vulnerability_id,
                search_term=query
            )
            
            # Adatta il formato del risultato
            return {
                "total": result["total"],
                "results": [
                    {
                        "id": pattern.id,
                        "title": pattern.title,
                        "description": pattern.description,
                        "strategy": pattern.strategy,
                        "mvc_component": pattern.mvc_component,
                        "created_at": pattern.created_at.isoformat(),
                        "updated_at": pattern.updated_at.isoformat(),
                        "score": 1.0
                    }
                    for pattern in result["patterns"]
                ]
            }
    
    def index_pattern(self, pattern: PrivacyPattern) -> bool:
        """
        Indicizza un pattern in Elasticsearch.
        
        Args:
            pattern (PrivacyPattern): Pattern da indicizzare
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.search_service.es:
            return False
        
        return self.search_service.index_pattern(pattern)
    
    def remove_pattern_from_index(self, pattern_id: int) -> bool:
        """
        Rimuove un pattern dall'indice.
        
        Args:
            pattern_id (int): ID del pattern da rimuovere
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.search_service.es:
            return False
        
        return self.search_service.remove_pattern_from_index(pattern_id)
    
    def reindex_all_patterns(self, db: Session) -> bool:
        """
        Reindicizza tutti i pattern.
        
        Args:
            db (Session): Sessione database
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.search_service.es:
            return False
        
        return self.search_service.reindex_all_patterns(db)
    
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
        # Se Elasticsearch è disponibile
        if self.search_service.es:
            try:
                # Usa Elasticsearch per suggerimenti
                body = {
                    "size": 0,
                    "suggest": {
                        "pattern_suggest": {
                            "prefix": query,
                            "completion": {
                                "field": "title.completion",
                                "size": limit
                            }
                        }
                    }
                }
                
                response = self.search_service.es.search(
                    index=self.search_service.index_name,
                    body=body
                )
                
                suggestions = []
                for option in response["suggest"]["pattern_suggest"][0]["options"]:
                    suggestions.append({
                        "id": option["_source"]["id"],
                        "title": option["_source"]["title"],
                        "text": option["text"]
                    })
                
                return suggestions
            except Exception as e:
                logger.error(f"Errore in autocomplete con Elasticsearch: {str(e)}")
        
        # Fallback: ricerca nel database
        search_term = f"%{query}%"
        patterns = db.query(PrivacyPattern).filter(
            PrivacyPattern.title.ilike(search_term)
        ).limit(limit).all()
        
        return [
            {"id": p.id, "title": p.title, "text": p.title} 
            for p in patterns
        ]