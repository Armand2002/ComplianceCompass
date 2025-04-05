# src/services/elasticsearch_service.py
"""
Servizio per la gestione delle operazioni con Elasticsearch.

Fornisce un'astrazione per interagire con Elasticsearch, 
con meccanismi di fallback e gestione degli errori.
"""

import logging
from typing import Dict, Any, Optional, Callable
from elasticsearch import Elasticsearch, exceptions as es_exceptions

from src.exceptions import ServiceUnavailableException
from src.config import settings

logger = logging.getLogger(__name__)

class ElasticsearchService:
    """
    Servizio per la gestione delle operazioni su Elasticsearch.
    
    Offre metodi per ricerca, indicizzazione e gestione 
    con meccanismi di fallback e logging.
    """
    
    def __init__(self, 
                 es_client: Optional[Elasticsearch] = None, 
                 index_name: str = "compliance_compass"):
        """
        Inizializza il servizio Elasticsearch.
        
        Args:
            es_client (Elasticsearch, optional): Client Elasticsearch personalizzato
            index_name (str, optional): Nome dell'indice principale
        """
        self.index_name = index_name
        
        # Usa il client passato o crea un nuovo client
        self.es = es_client or self._create_es_client()
        
        # Flag per verificare la disponibilità del servizio
        self.is_available = self._check_connection()
    
    def _create_es_client(self) -> Optional[Elasticsearch]:
        """
        Crea un client Elasticsearch basato sulle impostazioni.
        
        Returns:
            Optional[Elasticsearch]: Client Elasticsearch o None
        """
        try:
            return Elasticsearch(
                [settings.ELASTICSEARCH_URL],
                retry_on_timeout=True,
                max_retries=3,
                timeout=10
            )
        except Exception as e:
            logger.error(f"Errore nella connessione a Elasticsearch: {e}")
            return None
    
    def _check_connection(self) -> bool:
        """
        Verifica la connessione a Elasticsearch.
        
        Returns:
            bool: True se la connessione è attiva, False altrimenti
        """
        if not self.es:
            return False
        
        try:
            return self.es.ping()
        except Exception as e:
            logger.warning(f"Ping Elasticsearch fallito: {e}")
            return False
    
    def search(self, 
               query: Dict[str, Any], 
               fallback_method: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Esegue una ricerca su Elasticsearch con meccanismo di fallback.
        
        Args:
            query (Dict[str, Any]): Query di ricerca Elasticsearch
            fallback_method (Callable, optional): Metodo alternativo di ricerca
        
        Returns:
            Dict[str, Any]: Risultati della ricerca
        
        Raises:
            ServiceUnavailableException: Se la ricerca fallisce
        """
        try:
            # Verifica disponibilità del servizio
            if not self.is_available:
                raise ServiceUnavailableException("Elasticsearch")
            
            # Esegui ricerca
            results = self.es.search(index=self.index_name, body=query)
            return results
        
        except es_exceptions.ElasticsearchException as es_err:
            logger.error(f"Errore Elasticsearch: {es_err}")
            
            # Fallback se disponibile
            if fallback_method:
                logger.info("Utilizzo metodo di fallback per la ricerca")
                return fallback_method(query)
            
            # Solleva eccezione personalizzata
            raise ServiceUnavailableException(
                "Elasticsearch", 
                reason=str(es_err)
            )
    
    def index_document(self, 
                       document: Dict[str, Any], 
                       doc_id: Optional[str] = None) -> str:
        """
        Indicizza un documento in Elasticsearch.
        
        Args:
            document (Dict[str, Any]): Documento da indicizzare
            doc_id (str, optional): ID documento personalizzato
        
        Returns:
            str: ID del documento indicizzato
        
        Raises:
            ServiceUnavailableException: Se l'indicizzazione fallisce
        """
        try:
            # Verifica disponibilità del servizio
            if not self.is_available:
                raise ServiceUnavailableException("Elasticsearch")
            
            # Indicizza documento
            result = self.es.index(
                index=self.index_name, 
                body=document, 
                id=doc_id
            )
            
            return result['_id']
        
        except es_exceptions.ElasticsearchException as es_err:
            logger.error(f"Errore durante l'indicizzazione: {es_err}")
            raise ServiceUnavailableException(
                "Elasticsearch", 
                reason=f"Indicizzazione fallita: {es_err}"
            )
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Elimina un documento da Elasticsearch.
        
        Args:
            doc_id (str): ID del documento da eliminare
        
        Returns:
            bool: True se l'eliminazione è riuscita
        
        Raises:
            ServiceUnavailableException: Se l'eliminazione fallisce
        """
        try:
            # Verifica disponibilità del servizio
            if not self.is_available:
                raise ServiceUnavailableException("Elasticsearch")
            
            # Elimina documento
            result = self.es.delete(
                index=self.index_name, 
                id=doc_id
            )
            
            return result['result'] == 'deleted'
        
        except es_exceptions.ElasticsearchException as es_err:
            logger.error(f"Errore durante l'eliminazione: {es_err}")
            raise ServiceUnavailableException(
                "Elasticsearch", 
                reason=f"Eliminazione fallita: {es_err}"
            )