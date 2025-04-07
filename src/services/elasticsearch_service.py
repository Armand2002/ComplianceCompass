"""
Mock di Elasticsearch per demo/esame
"""
import logging
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger(__name__)

class ElasticsearchMock:
    def __init__(self, *args, **kwargs):
        self.indices = IndicesMock()
        print("Elasticsearch mock inizializzato per modalità demo")
    
    def search(self, index=None, body=None):
        """Restituisce risultati predefiniti per le ricerche"""
        # Risultati finti per dimostrare la funzionalità
        return {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {
                        "_id": "1",
                        "_source": {
                            "title": "Data Minimization Pattern",
                            "description": "Pattern per minimizzare i dati raccolti",
                            "category": "Privacy",
                            "gdpr_articles": [5, 25]
                        }
                    },
                    {
                        "_id": "2",
                        "_source": {
                            "title": "Consent Management Pattern",
                            "description": "Pattern per la gestione del consenso",
                            "category": "Privacy",
                            "gdpr_articles": [6, 7]
                        }
                    }
                ]
            }
        }
    
    def index(self, index=None, id=None, body=None, **kwargs):
        """Simula l'indicizzazione di un documento"""
        return {"result": "created", "_id": id or "mock_id"}
    
    def delete(self, index=None, id=None, **kwargs):
        """Simula l'eliminazione di un documento"""
        return {"result": "deleted"}
    
    def exists(self, index=None, **kwargs):
        """Simula il controllo dell'esistenza di un indice"""
        return True
    
    def ping(self):
        """Simula il ping per verificare la connessione"""
        return True


class IndicesMock:
    def exists(self, index=None):
        return False
    
    def create(self, index=None, body=None):
        return {"acknowledged": True}
    
    def delete(self, index=None):
        return {"acknowledged": True}


class MockElasticsearchService:
    """
    Servizio Elasticsearch simulato per testing.
    
    Simula le principali operazioni di Elasticsearch 
    senza dipendenze esterne.
    """
    
    def __init__(self):
        """Inizializza il servizio mock."""
        self.documents = {}
        self.is_available = True
        logger.info("MockElasticsearchService inizializzato per modalità demo/esame")
    
    def search(
        self, 
        query: Dict[str, Any], 
        fallback_method: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Simula una ricerca Elasticsearch.
        
        Args:
            query (Dict[str, Any]): Query di ricerca
            fallback_method (Callable, optional): Metodo di fallback
        
        Returns:
            Dict[str, Any]: Risultati simulati
        """
        # Risultati predefiniti per la dimostrazione
        return {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {
                        "_id": "1",
                        "_source": {
                            "id": 1,
                            "title": "Data Minimization Pattern",
                            "description": "Pattern per minimizzare i dati raccolti",
                            "strategy": "Minimizzazione",
                            "mvc_component": "Model",
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                            "gdpr_articles": [
                                {"id": 5, "number": "5", "title": "Principi relativi al trattamento dei dati"}
                            ],
                            "pbd_principles": [
                                {"id": 1, "name": "Privacy by Default", "description": "Misure tecniche per garantire che siano trattati solo i dati necessari"}
                            ]
                        }
                    },
                    {
                        "_id": "2",
                        "_source": {
                            "id": 2,
                            "title": "Consent Management Pattern",
                            "description": "Pattern per la gestione del consenso",
                            "strategy": "Consenso",
                            "mvc_component": "Controller",
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                            "gdpr_articles": [
                                {"id": 6, "number": "6", "title": "Liceità del trattamento"},
                                {"id": 7, "number": "7", "title": "Condizioni per il consenso"}
                            ],
                            "pbd_principles": [
                                {"id": 2, "name": "User Control", "description": "Garantire il controllo dell'utente sui propri dati"}
                            ]
                        }
                    }
                ]
            }
        }
    
    def index_document(
        self, 
        document: Dict[str, Any], 
        doc_id: Optional[str] = None
    ) -> str:
        """
        Simula l'indicizzazione di un documento.
        
        Args:
            document (Dict[str, Any]): Documento da indicizzare
            doc_id (str, optional): ID documento
        
        Returns:
            str: ID del documento
        """
        # Genera ID se non fornito
        if doc_id is None:
            doc_id = str(len(self.documents) + 1)
        
        self.documents[doc_id] = document
        return doc_id
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Simula l'eliminazione di un documento.
        
        Args:
            doc_id (str): ID del documento
        
        Returns:
            bool: True se l'eliminazione è riuscita
        """
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False
    
    def create_index(self):
        """Simula la creazione di un indice"""
        return True
    
    def reindex_all_patterns(self, db=None):
        """Simula la reindicizzazione di tutti i pattern"""
        return True
    
    def remove_pattern_from_index(self, pattern_id):
        """Simula la rimozione di un pattern dall'indice"""
        return True
    
    def search_patterns(self, query=None, **kwargs):
        """Simula la ricerca di pattern"""
        return {
            "total": 2,
            "results": [
                {
                    "id": 1,
                    "title": "Data Minimization Pattern",
                    "description": "Pattern per minimizzare i dati raccolti",
                    "strategy": "Minimizzazione",
                    "mvc_component": "Model"
                },
                {
                    "id": 2,
                    "title": "Consent Management Pattern",
                    "description": "Pattern per la gestione del consenso",
                    "strategy": "Consenso",
                    "mvc_component": "Controller"
                }
            ]
        }
    
    def get_autocomplete_suggestions(self, query, limit=10, fields=None, db=None):
        """Simula i suggerimenti di autocompletamento"""
        return [
            {
                "id": 1,
                "title": "Data Minimization Pattern",
                "strategy": "Minimizzazione",
                "description": "Pattern per minimizzare i dati raccolti",
                "score": 2.0
            },
            {
                "id": 2,
                "title": "Consent Management Pattern",
                "strategy": "Consenso",
                "description": "Pattern per la gestione del consenso",
                "score": 1.5
            }
        ]