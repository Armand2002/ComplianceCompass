# src/services/pattern_service.py
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.models.privacy_pattern import PrivacyPattern, PatternGdprRelation, PatternPbdRelation, PatternIsoRelation, PatternVulnerabilityRelation
from src.models.user_model import User

logger = logging.getLogger(__name__)

class PatternService:
    """
    Servizio per l'accesso e la manipolazione dei privacy pattern.
    Implementa la logica di business tra i controller e i modelli.
    """
    
    @staticmethod
    def get_patterns_with_filters(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        strategy: Optional[str] = None,
        mvc_component: Optional[str] = None,
        gdpr_id: Optional[int] = None,
        pbd_id: Optional[int] = None,
        iso_id: Optional[int] = None,
        vulnerability_id: Optional[int] = None,
        search_term: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Recupera pattern con filtri.
        
        Args:
            db (Session): Sessione database
            skip (int): Offset per la paginazione
            limit (int): Limite risultati per pagina
            strategy (str, optional): Filtra per strategia
            mvc_component (str, optional): Filtra per componente MVC
            gdpr_id (int, optional): Filtra per articolo GDPR
            pbd_id (int, optional): Filtra per principio PbD
            iso_id (int, optional): Filtra per fase ISO
            vulnerability_id (int, optional): Filtra per vulnerabilità
            search_term (str, optional): Ricerca testuale
            user_id (int, optional): Filtra per creatore
            
        Returns:
            Dict: Dictionary con patterns, count e metadati
        """
        # Base query
        query = db.query(PrivacyPattern)
        
        # Filtra per strategia
        if strategy:
            query = query.filter(PrivacyPattern.strategy == strategy)
        
        # Filtra per componente MVC
        if mvc_component:
            query = query.filter(PrivacyPattern.mvc_component == mvc_component)
        
        # Filtra per articolo GDPR
        if gdpr_id:
            query = query.join(PatternGdprRelation).filter(
                PatternGdprRelation.gdpr_article_id == gdpr_id
            )
        
        # Filtra per principio PbD
        if pbd_id:
            query = query.join(PatternPbdRelation).filter(
                PatternPbdRelation.pbd_principle_id == pbd_id
            )
        
        # Filtra per fase ISO
        if iso_id:
            query = query.join(PatternIsoRelation).filter(
                PatternIsoRelation.iso_phase_id == iso_id
            )
        
        # Filtra per vulnerabilità
        if vulnerability_id:
            query = query.join(PatternVulnerabilityRelation).filter(
                PatternVulnerabilityRelation.vulnerability_id == vulnerability_id
            )
        
        # Filtra per creatore
        if user_id:
            query = query.filter(PrivacyPattern.created_by_id == user_id)
        
        # Ricerca testuale
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                PrivacyPattern.title.ilike(search_pattern) |
                PrivacyPattern.description.ilike(search_pattern) |
                PrivacyPattern.context.ilike(search_pattern) |
                PrivacyPattern.problem.ilike(search_pattern) |
                PrivacyPattern.solution.ilike(search_pattern)
            )
        
        # Ottieni conteggio totale per la paginazione
        total = query.count()
        
        # Calcola metadati paginazione
        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = skip // limit + 1 if limit > 0 else 1
        
        # Applica paginazione
        patterns = query.order_by(PrivacyPattern.updated_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return {
            "patterns": patterns,
            "total": total,
            "page": page,
            "pages": pages
        }
        
    @staticmethod
    def check_title_uniqueness(db: Session, title: str, pattern_id: Optional[int] = None) -> bool:
        """
        Verifica che il titolo di un pattern sia unico.
        
        Args:
            db (Session): Sessione database
            title (str): Titolo da verificare
            pattern_id (int, optional): ID del pattern da escludere dalla verifica
            
        Returns:
            bool: True se il titolo è unico, False altrimenti
        """
        query = db.query(PrivacyPattern).filter(PrivacyPattern.title == title)
        
        if pattern_id:
            query = query.filter(PrivacyPattern.id != pattern_id)
            
        return query.first() is None