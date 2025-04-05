# src/services/pattern_service.py
"""
Servizio per la gestione dei Privacy Patterns.

Fornisce un'astrazione per le operazioni sui pattern, 
con supporto per ricerca, cache e gestione degli errori.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models.privacy_pattern import PrivacyPattern
from src.exceptions import DataIntegrityException, ServiceUnavailableException
from src.services.elasticsearch_service import ElasticsearchService
from src.utils.cache import cached

logger = logging.getLogger(__name__)

class PatternService:
    """
    Servizio per la gestione dei Privacy Patterns.
    
    Offre metodi per operazioni CRUD sui pattern, 
    con integrazione Elasticsearch e meccanismi di caching.
    """
    
    def __init__(
        self, 
        db_session: Session, 
        elasticsearch_service: Optional[ElasticsearchService] = None
    ):
        """
        Inizializza il servizio Pattern.
        
        Args:
            db_session (Session): Sessione database SQLAlchemy
            elasticsearch_service (ElasticsearchService, optional): Servizio Elasticsearch
        """
        self.db = db_session
        self.es_service = elasticsearch_service
    
    @cached(ttl=300)  # Cache per 5 minuti
    def get_pattern_by_id(self, pattern_id: int) -> Optional[PrivacyPattern]:
        """
        Recupera un pattern specifico tramite ID.
        
        Args:
            pattern_id (int): ID del pattern
        
        Returns:
            Optional[PrivacyPattern]: Pattern trovato o None
        
        Raises:
            DataIntegrityException: Se ci sono problemi con il recupero
        """
        try:
            pattern = self.db.query(PrivacyPattern).filter(
                PrivacyPattern.id == pattern_id
            ).first()
            
            if not pattern:
                logger.warning(f"Pattern con ID {pattern_id} non trovato")
                return None
            
            return pattern
        
        except SQLAlchemyError as e:
            logger.error(f"Errore nel recupero pattern: {e}")
            raise DataIntegrityException(
                entity="PrivacyPattern", 
                details=f"Errore nel recupero pattern {pattern_id}"
            )
    
    def create_pattern(self, pattern_data: Dict[str, Any]) -> PrivacyPattern:
        """
        Crea un nuovo pattern.
        
        Args:
            pattern_data (Dict[str, Any]): Dati del pattern
        
        Returns:
            PrivacyPattern: Pattern creato
        
        Raises:
            DataIntegrityException: Se la creazione fallisce
        """
        try:
            # Validazione dei dati
            self._validate_pattern_data(pattern_data)
            
            # Crea pattern
            pattern = PrivacyPattern(**pattern_data)
            self.db.add(pattern)
            self.db.commit()
            self.db.refresh(pattern)
            
            # Indica su Elasticsearch se disponibile
            if self.es_service and self.es_service.is_available:
                self._index_pattern_in_elasticsearch(pattern)
            
            return pattern
        
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Errore nella creazione pattern: {e}")
            raise DataIntegrityException(
                entity="PrivacyPattern", 
                details="Impossibile creare il pattern"
            )
    
    def update_pattern(
        self, 
        pattern_id: int, 
        update_data: Dict[str, Any]
    ) -> PrivacyPattern:
        """
        Aggiorna un pattern esistente.
        
        Args:
            pattern_id (int): ID del pattern da aggiornare
            update_data (Dict[str, Any]): Dati da aggiornare
        
        Returns:
            PrivacyPattern: Pattern aggiornato
        
        Raises:
            DataIntegrityException: Se l'aggiornamento fallisce
            ServiceUnavailableException: Se il servizio non è disponibile
        """
        try:
            # Recupera il pattern esistente
            pattern = self.get_pattern_by_id(pattern_id)
            
            if not pattern:
                raise DataIntegrityException(
                    entity="PrivacyPattern", 
                    details=f"Pattern con ID {pattern_id} non trovato"
                )
            
            # Valida e aggiorna i dati
            self._validate_pattern_update(pattern, update_data)
            
            # Applica gli aggiornamenti
            for key, value in update_data.items():
                setattr(pattern, key, value)
            
            # Salva le modifiche
            self.db.commit()
            self.db.refresh(pattern)
            
            # Re-indicizza su Elasticsearch se disponibile
            if self.es_service and self.es_service.is_available:
                self._index_pattern_in_elasticsearch(pattern)
            
            return pattern
        
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Errore nell'aggiornamento pattern: {e}")
            raise DataIntegrityException(
                entity="PrivacyPattern", 
                details=f"Impossibile aggiornare il pattern {pattern_id}"
            )
    
    def delete_pattern(self, pattern_id: int) -> bool:
        """
        Elimina un pattern.
        
        Args:
            pattern_id (int): ID del pattern da eliminare
        
        Returns:
            bool: True se l'eliminazione è riuscita
        
        Raises:
            DataIntegrityException: Se l'eliminazione fallisce
        """
        try:
            # Recupera il pattern
            pattern = self.get_pattern_by_id(pattern_id)
            
            if not pattern:
                logger.warning(f"Pattern con ID {pattern_id} non trovato")
                return False
            
            # Elimina da database
            self.db.delete(pattern)
            self.db.commit()
            
            # Rimuovi da Elasticsearch se disponibile
            if self.es_service and self.es_service.is_available:
                try:
                    self.es_service.delete_document(str(pattern_id))
                except Exception as e:
                    logger.warning(f"Errore nella rimozione da Elasticsearch: {e}")
            
            return True
        
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Errore nell'eliminazione pattern: {e}")
            raise DataIntegrityException(
                entity="PrivacyPattern", 
                details=f"Impossibile eliminare il pattern {pattern_id}"
            )
    
    def search_patterns(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        search_term: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Ricerca patterns con filtri e paginazione.
        
        Args:
            filters (Dict[str, Any], optional): Filtri di ricerca
            search_term (str, optional): Termine di ricerca testuale
            page (int, optional): Numero di pagina
            per_page (int, optional): Numero di risultati per pagina
        
        Returns:
            Dict[str, Any]: Risultati della ricerca con metadati
        """
        try:
            # Query base
            query = self.db.query(PrivacyPattern)
            
            # Applica filtri
            if filters:
                for key, value in filters.items():
                    if hasattr(PrivacyPattern, key):
                        query = query.filter(
                            getattr(PrivacyPattern, key) == value
                        )
            
            # Ricerca testuale
            if search_term:
                query = query.filter(
                    (PrivacyPattern.title.ilike(f"%{search_term}%")) |
                    (PrivacyPattern.description.ilike(f"%{search_term}%"))
                )
            
            # Conta risultati totali
            total_count = query.count()
            
            # Applica paginazione
            patterns = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                "patterns": patterns,
                "total": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page
            }
        
        except SQLAlchemyError as e:
            logger.error(f"Errore nella ricerca patterns: {e}")
            raise ServiceUnavailableException(
                "Database", 
                reason="Impossibile eseguire la ricerca dei patterns"
            )
    
    def _validate_pattern_data(self, pattern_data: Dict[str, Any]) -> None:
        """
        Valida i dati di un nuovo pattern.
        
        Args:
            pattern_data (Dict[str, Any]): Dati del pattern
        
        Raises:
            DataIntegrityException: Se i dati non sono validi
        """
        # Controlli di base
        required_fields = ['title', 'description', 'strategy']
        for field in required_fields:
            if field not in pattern_data or not pattern_data[field]:
                raise DataIntegrityException(
                    entity="PrivacyPattern", 
                    details=f"Campo obbligatorio mancante: {field}"
                )
        
        # Controllo lunghezza
        if len(pattern_data['title']) > 255:
            raise DataIntegrityException(
                entity="PrivacyPattern", 
                details="Titolo troppo lungo (max 255 caratteri)"
            )
    
    def _validate_pattern_update(
        self, 
        pattern: PrivacyPattern, 
        update_data: Dict[str, Any]
    ) -> None:
        """
        Valida i dati di aggiornamento di un pattern.
        
        Args:
            pattern (PrivacyPattern): Pattern esistente
            update_data (Dict[str, Any]): Dati di aggiornamento
        
        Raises:
            DataIntegrityException: Se i dati non sono validi
        """
        # Controlli specifici per l'aggiornamento
        if 'title' in update_data:
            if not update_data['title']:
                raise DataIntegrityException(
                    entity="PrivacyPattern", 
                    details="Titolo non può essere vuoto"
                )
            if len(update_data['title']) > 255:
                raise DataIntegrityException(
                    entity="PrivacyPattern", 
                    details="Titolo troppo lungo (max 255 caratteri)"
                )
    
    def _index_pattern_in_elasticsearch(self, pattern: PrivacyPattern) -> None:
        """
        Indicizza un pattern in Elasticsearch.
        
        Args:
            pattern (PrivacyPattern): Pattern da indicizzare
        """
        try:
            # Converti il pattern in un documento JSON
            pattern_doc = {
                'id': pattern.id,
                'title': pattern.title,
                'description': pattern.description,
                'strategy': pattern.strategy,
                'mvc_component': pattern.mvc_component,
                # Aggiungi altri campi necessari
            }
            
            # Indicizza nel servizio Elasticsearch
            self.es_service.index_document(pattern_doc, doc_id=str(pattern.id))
        
        except Exception as e:
            logger.warning(f"Errore nell'indicizzazione pattern: {e}")