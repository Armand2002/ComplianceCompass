# src/services/search_service.py - Versione modificata
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
    Servizio per la ricerca di Privacy Patterns.
    Questa implementazione sostituisce Elasticsearch con ricerca SQL.
    """
    
    def __init__(self):
        """
        Inizializza il servizio di ricerca.
        Nota: mantenuto es=None per compatibilità con il codice esistente.
        """
        self.es = None  # Mantenuto per compatibilità, ma non usato
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
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Implementazione di ricerca basata su SQL.
        """
        # Implementare qui la logica di ricerca con SQLAlchemy
        return self._db_search_fallback(
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
    
    def _db_search_fallback(
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
        Ricerca pattern nel database usando SQLAlchemy.
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
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Ottiene suggerimenti di autocompletamento basati sul query utente.
        """
        if not query or not db:
            return []
        
        try:
            # Query SQL con LIKE per imitare autocomplete
            like_term = f"%{query}%"
            
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