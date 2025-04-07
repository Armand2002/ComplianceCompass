# src/services/elasticsearch_init.py
"""
Servizio per l'inizializzazione e la gestione di Elasticsearch.

Questo modulo fornisce funzioni per configurare Elasticsearch,
creare gli indici e definire le mappature.
"""
import logging
from elasticsearch import Elasticsearch, exceptions
from sqlalchemy.orm import Session

from src.config import settings
from src.models.privacy_pattern import PrivacyPattern

logger = logging.getLogger(__name__)

class ElasticsearchInit:
    """
    Classe per l'inizializzazione di Elasticsearch.
    
    Gestisce la creazione di indici e altre operazioni di setup.
    """
    
    def __init__(self):
        """Inizializza la connessione a Elasticsearch."""
        self.es = None
        self.connected = False
        self.index_name = "privacy_patterns"
        
        # Tenta di connettersi a Elasticsearch
        self._connect()
    
    def _connect(self):
        """Crea una connessione a Elasticsearch."""
        try:
            self.es = Elasticsearch(settings.ELASTICSEARCH_URL)
            
            if self.es.ping():
                logger.info("Connessione a Elasticsearch stabilita con successo.")
                self.connected = True
            else:
                logger.warning("Impossibile connettersi a Elasticsearch. Servizio non disponibile.")
                self.es = None
                self.connected = False
        except exceptions.ConnectionError:
            logger.warning("Elasticsearch non disponibile.")
            self.es = None
            self.connected = False
        except Exception as e:
            logger.error(f"Errore nella connessione a Elasticsearch: {str(e)}")
            self.es = None
            self.connected = False
    
    def setup_indices(self):
        """
        Configura gli indici necessari per l'applicazione.
        
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.connected:
            logger.warning("Elasticsearch non disponibile. Impossibile configurare gli indici.")
            return False
        
        try:
            # Crea indice pattern se non esiste
            return self._create_pattern_index()
        except Exception as e:
            logger.error(f"Errore nella configurazione degli indici: {str(e)}")
            return False
    
    def _create_pattern_index(self):
        """
        Crea l'indice per i Privacy Patterns.
        
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.es.indices.exists(index=self.index_name):
            # Configurazione dell'indice con analyzer per italiano
            settings_body = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "italian_analyzer": {
                                "type": "standard",
                                "stopwords": "_italian_"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {
                            "type": "text", 
                            "analyzer": "italian_analyzer",
                            "fields": {
                                "keyword": {"type": "keyword"},
                                "completion": {
                                    "type": "completion",
                                    "analyzer": "italian_analyzer"
                                }
                            }
                        },
                        "description": {"type": "text", "analyzer": "italian_analyzer"},
                        "context": {"type": "text", "analyzer": "italian_analyzer"},
                        "problem": {"type": "text", "analyzer": "italian_analyzer"},
                        "solution": {"type": "text", "analyzer": "italian_analyzer"},
                        "consequences": {"type": "text", "analyzer": "italian_analyzer"},
                        "strategy": {"type": "keyword"},
                        "mvc_component": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "gdpr_articles": {
                            "type": "nested", 
                            "properties": {
                                "id": {"type": "integer"},
                                "number": {"type": "keyword"},
                                "title": {"type": "text", "analyzer": "italian_analyzer"}
                            }
                        },
                        "pbd_principles": {
                            "type": "nested", 
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "keyword"},
                                "description": {"type": "text", "analyzer": "italian_analyzer"}
                            }
                        },
                        "iso_phases": {
                            "type": "nested", 
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "keyword"},
                                "standard": {"type": "keyword"}
                            }
                        },
                        "vulnerabilities": {
                            "type": "nested", 
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "keyword"},
                                "severity": {"type": "keyword"}
                            }
                        }
                    }
                }
            }
            
            # Crea l'indice
            self.es.indices.create(index=self.index_name, body=settings_body)
            logger.info(f"Indice '{self.index_name}' creato con successo.")
            return True
        
        logger.info(f"Indice '{self.index_name}' già esistente.")
        return True
    
    def index_all_patterns(self, db: Session):
        """
        Indicizza tutti i pattern presenti nel database.
        
        Args:
            db (Session): Sessione del database
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.connected:
            logger.warning("Elasticsearch non disponibile. Impossibile indicizzare i pattern.")
            return False
        
        try:
            # Verifica che l'indice esista
            if not self.es.indices.exists(index=self.index_name):
                self._create_pattern_index()
            
            # Recupera tutti i pattern
            patterns = db.query(PrivacyPattern).all()
            
            # Conta pattern indicizzati
            count = 0
            
            # Indicizza ogni pattern
            for pattern in patterns:
                self._index_pattern(pattern)
                count += 1
            
            logger.info(f"Indicizzati {count} pattern in Elasticsearch.")
            return True
        except Exception as e:
            logger.error(f"Errore nell'indicizzazione dei pattern: {str(e)}")
            return False
    
    def index_pattern(self, pattern: PrivacyPattern) -> bool:
        """
        Wrapper pubblico per indicizzare un singolo pattern.
        
        Args:
            pattern (PrivacyPattern): Pattern da indicizzare
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.connected:
            logger.warning("Elasticsearch non disponibile. Impossibile indicizzare il pattern.")
            return False
            
        try:
            return self._index_pattern(pattern)
        except Exception as e:
            logger.error(f"Errore nell'indicizzazione del pattern {pattern.id}: {str(e)}")
            return False
    
    def _index_pattern(self, pattern: PrivacyPattern):
        """
        Indicizza un singolo pattern.
        
        Args:
            pattern (PrivacyPattern): Pattern da indicizzare
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        # Crea documento per Elasticsearch
        doc = {
            "id": pattern.id,
            "title": pattern.title,
            "description": pattern.description,
            "context": pattern.context,
            "problem": pattern.problem,
            "solution": pattern.solution,
            "consequences": pattern.consequences,
            "strategy": pattern.strategy,
            "mvc_component": pattern.mvc_component,
            "created_at": pattern.created_at.isoformat(),
            "updated_at": pattern.updated_at.isoformat(),
            "gdpr_articles": [
                {"id": article.id, "number": article.number, "title": article.title}
                for article in pattern.gdpr_articles
            ],
            "pbd_principles": [
                {"id": principle.id, "name": principle.name, "description": principle.description}
                for principle in pattern.pbd_principles
            ],
            "iso_phases": [
                {"id": phase.id, "name": phase.name, "standard": phase.standard}
                for phase in pattern.iso_phases
            ],
            "vulnerabilities": [
                {"id": vuln.id, "name": vuln.name, "severity": vuln.severity.value}
                for vuln in pattern.vulnerabilities
            ]
        }
        
        # Indicizza documento
        self.es.index(index=self.index_name, id=pattern.id, body=doc)
        
        return True
    
    def reset_indices(self):
        """
        Elimina e ricrea tutti gli indici.
        
        Utile per reinizializzare completamente il sistema di ricerca.
        
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.connected:
            logger.warning("Elasticsearch non disponibile. Impossibile resettare gli indici.")
            return False
        
        try:
            # Elimina indice se esiste
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                logger.info(f"Indice '{self.index_name}' eliminato.")
            
            # Ricrea indice
            self._create_pattern_index()
            
            return True
        except Exception as e:
            logger.error(f"Errore nel reset degli indici: {str(e)}")
            return False