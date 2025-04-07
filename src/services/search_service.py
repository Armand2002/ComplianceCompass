# src/services/search_service.py
"""
Servizio di ricerca basato su SQL come sostituto di Elasticsearch.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from sqlalchemy.exc import SQLAlchemyError

from src.models.privacy_pattern import PrivacyPattern
from src.models.gdpr_model import GDPRArticle
from src.models.pbd_principle import PbDPrinciple
from src.models.iso_phase import ISOPhase
from src.models.vulnerability import Vulnerability

logger = logging.getLogger(__name__)

class SearchService:
    """
    Servizio per la ricerca di Privacy Patterns mediante SQL.
    Questa implementazione sostituisce completamente Elasticsearch.
    """
    
    def __init__(self):
        """
        Inizializza il servizio di ricerca.
        Nota: mantenuto es=None per compatibilità con il codice esistente.
        """
        self.es = None
        self.index_name = "privacy_patterns"  # Mantenuto per compatibilità
        logger.info("Inizializzato servizio di ricerca basato su SQL (senza Elasticsearch)")
    
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
        size: int = 10,
        sort_by: str = "relevance"
    ) -> Dict[str, Any]:
        """
        Esegue una ricerca di Privacy Patterns usando query SQL ottimizzate.
        
        Args:
            db (Session): Sessione database SQLAlchemy
            query (str, optional): Query di ricerca testuale
            strategy (str, optional): Filtra per strategia
            mvc_component (str, optional): Filtra per componente MVC
            gdpr_id (int, optional): Filtra per articolo GDPR
            pbd_id (int, optional): Filtra per principio PbD
            iso_id (int, optional): Filtra per fase ISO
            vulnerability_id (int, optional): Filtra per vulnerabilità
            from_pos (int): Posizione di partenza per la paginazione
            size (int): Numero di risultati da restituire
            sort_by (str): Campo di ordinamento
            
        Returns:
            Dict[str, Any]: Risultati della ricerca
        """
        try:
            # Costruzione della query base
            base_query = db.query(PrivacyPattern)
            
            # Applicazione dei filtri
            query_filters = []
            
            # Ricerca testuale
            if query:
                search_terms = query.lower().split()
                for term in search_terms:
                    like_term = f"%{term}%"
                    query_filters.append(
                        or_(
                            func.lower(PrivacyPattern.title).like(like_term),
                            func.lower(PrivacyPattern.description).like(like_term),
                            func.lower(PrivacyPattern.context).like(like_term),
                            func.lower(PrivacyPattern.problem).like(like_term),
                            func.lower(PrivacyPattern.solution).like(like_term),
                            func.lower(PrivacyPattern.consequences).like(like_term),
                        )
                    )
            
            # Filtri specifici
            if strategy:
                query_filters.append(PrivacyPattern.strategy == strategy)
            
            if mvc_component:
                query_filters.append(PrivacyPattern.mvc_component == mvc_component)
            
            if gdpr_id:
                base_query = base_query.join(PrivacyPattern.gdpr_articles)
                query_filters.append(GDPRArticle.id == gdpr_id)
            
            if pbd_id:
                base_query = base_query.join(PrivacyPattern.pbd_principles)
                query_filters.append(PbDPrinciple.id == pbd_id)
            
            if iso_id:
                base_query = base_query.join(PrivacyPattern.iso_phases)
                query_filters.append(ISOPhase.id == iso_id)
            
            if vulnerability_id:
                base_query = base_query.join(PrivacyPattern.vulnerabilities)
                query_filters.append(Vulnerability.id == vulnerability_id)
            
            # Applica tutti i filtri
            if query_filters:
                base_query = base_query.filter(and_(*query_filters))
            
            # Assicurati che i risultati siano unici
            base_query = base_query.distinct()
            
            # Ordinamento
            if sort_by == "relevance" and query:
                # In mancanza di full-text search, ordinamento per titolo
                base_query = base_query.order_by(PrivacyPattern.title)
            elif sort_by == "date":
                base_query = base_query.order_by(PrivacyPattern.updated_at.desc())
            else:
                base_query = base_query.order_by(PrivacyPattern.title)
            
            # Conteggio totale per paginazione
            total = base_query.count()
            
            # Applicazione paginazione
            patterns = base_query.offset(from_pos).limit(size).all()
            
            # Conversione per mantenere la compatibilità con l'interfaccia precedente
            results = []
            for pattern in patterns:
                results.append({
                    "id": pattern.id,
                    "title": pattern.title,
                    "description": pattern.description,
                    "strategy": pattern.strategy,
                    "mvc_component": pattern.mvc_component,
                    "created_at": pattern.created_at.isoformat() if pattern.created_at else None,
                    "updated_at": pattern.updated_at.isoformat() if pattern.updated_at else None,
                    "score": 1.0  # Placeholder, non abbiamo scoring senza Elasticsearch
                })
            
            return {
                "total": total,
                "results": results
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Errore SQL durante la ricerca: {str(e)}")
            return {"total": 0, "results": [], "error": "db_error"}
        except Exception as e:
            logger.error(f"Errore generico durante la ricerca: {str(e)}")
            return {"total": 0, "results": [], "error": "general_error"}
    
    def get_autocomplete_suggestions(
        self, 
        db: Session,
        query: str,
        limit: int = 10,
        fields: List[str] = ["title", "description", "strategy"]
    ) -> List[Dict[str, Any]]:
        """
        Ottiene suggerimenti di autocompletamento basati sul query utente.
        
        Args:
            db (Session): Sessione database SQLAlchemy
            query (str): Query utente parziale
            limit (int): Numero massimo di suggerimenti
            fields (List[str]): Campi su cui effettuare l'autocomplete
            
        Returns:
            List[Dict[str, Any]]: Lista di suggerimenti
        """
        if not query or not db:
            return []
        
        try:
            # Query SQL con LIKE per imitare autocomplete
            like_term = f"%{query}%"
            
            if "title" in fields:
                patterns = db.query(PrivacyPattern).filter(
                    PrivacyPattern.title.ilike(like_term)
                ).limit(limit).all()
            else:
                # Fallback generico
                patterns = db.query(PrivacyPattern).filter(
                    or_(
                        PrivacyPattern.title.ilike(like_term),
                        PrivacyPattern.description.ilike(like_term),
                        PrivacyPattern.strategy.ilike(like_term)
                    )
                ).limit(limit).all()
            
            suggestions = []
            for pattern in patterns:
                # Crea un excerpt della descrizione
                description = pattern.description[:50] + "..." if pattern.description and len(pattern.description) > 50 else pattern.description or ""
                
                suggestions.append({
                    "id": pattern.id,
                    "title": pattern.title,
                    "strategy": pattern.strategy,
                    "description": description,
                    "score": 1.0  # Placeholder score
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Errore nell'autocomplete: {str(e)}")
            return []
    
    # Metodi stub per compatibilità con il codice esistente
    def index_pattern(self, pattern) -> bool:
        """Stub per compatibilità."""
        return True
    
    def remove_pattern_from_index(self, pattern_id: int) -> bool:
        """Stub per compatibilità."""
        return True
    
    def reindex_all_patterns(self, db: Session) -> bool:
        """Stub per compatibilità."""
        return True