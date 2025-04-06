# src/services/search_service.py
import logging
from typing import Dict, List, Any, Optional
from elasticsearch import Elasticsearch, exceptions
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.config import settings
from src.models.privacy_pattern import PrivacyPattern
from src.utils.circuit_breaker import circuit_breaker

logger = logging.getLogger(__name__)

class SearchService:
    """
    Servizio per la gestione delle ricerche mediante Elasticsearch.
    
    Fornisce funzionalità per indicizzare e cercare Privacy Patterns.
    """
    
    def __init__(self):
        """Inizializza la connessione a Elasticsearch."""
        self.es = None
        self.index_name = "privacy_patterns"
        
        try:
            self.es = Elasticsearch(settings.ELASTICSEARCH_URL, retry_on_timeout=True, max_retries=3)
            if not self.es.ping():
                logger.warning("Impossibile connettersi a Elasticsearch. Ricerca avanzata non disponibile.")
                self.es = None
        except Exception as e:
            logger.warning(f"Errore connessione Elasticsearch: {str(e)}. Ricerca avanzata non disponibile.")
            self.es = None
    
    def create_index(self) -> bool:
        """
        Crea l'indice per i Privacy Patterns se non esiste.
        
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.es:
            return False
        
        try:
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
                            "title": {"type": "text", "analyzer": "italian_analyzer"},
                            "description": {"type": "text", "analyzer": "italian_analyzer"},
                            "context": {"type": "text", "analyzer": "italian_analyzer"},
                            "problem": {"type": "text", "analyzer": "italian_analyzer"},
                            "solution": {"type": "text", "analyzer": "italian_analyzer"},
                            "consequences": {"type": "text", "analyzer": "italian_analyzer"},
                            "strategy": {"type": "keyword"},
                            "mvc_component": {"type": "keyword"},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"},
                            "gdpr_articles": {"type": "nested", "properties": {
                                "id": {"type": "integer"},
                                "number": {"type": "keyword"},
                                "title": {"type": "text", "analyzer": "italian_analyzer"}
                            }},
                            "pbd_principles": {"type": "nested", "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "keyword"},
                                "description": {"type": "text", "analyzer": "italian_analyzer"}
                            }},
                            "iso_phases": {"type": "nested", "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "keyword"},
                                "standard": {"type": "keyword"}
                            }},
                            "vulnerabilities": {"type": "nested", "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "keyword"},
                                "severity": {"type": "keyword"}
                            }}
                        }
                    }
                }
                
                self.es.indices.create(index=self.index_name, body=settings_body)
                logger.info(f"Indice '{self.index_name}' creato con successo.")
                return True
            
            return True
        except Exception as e:
            logger.error(f"Errore nella creazione dell'indice: {str(e)}")
            return False
    
    def index_pattern(self, pattern: PrivacyPattern) -> bool:
        """
        Indicizza un Privacy Pattern.
        
        Args:
            pattern (PrivacyPattern): Pattern da indicizzare
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.es:
            return False
        
        try:
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
            
            self.es.index(index=self.index_name, id=pattern.id, body=doc)
            logger.info(f"Pattern '{pattern.title}' (ID: {pattern.id}) indicizzato con successo.")
            return True
        except Exception as e:
            logger.error(f"Errore nell'indicizzazione del pattern {pattern.id}: {str(e)}")
            return False
    
    def reindex_all_patterns(self, db: Session) -> bool:
        """
        Reindicizza tutti i Privacy Patterns nel database.
        
        Args:
            db (Session): Sessione database
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.es:
            return False
        
        try:
            # Ricrea l'indice
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
            
            # Crea nuovo indice
            self.create_index()
            
            # Recupera tutti i pattern dal database
            patterns = db.query(PrivacyPattern).all()
            
            for pattern in patterns:
                self.index_pattern(pattern)
            
            logger.info(f"Reindicizzazione completata per {len(patterns)} patterns.")
            return True
        except Exception as e:
            logger.error(f"Errore nella reindicizzazione dei pattern: {str(e)}")
            return False
    
    def remove_pattern_from_index(self, pattern_id: int) -> bool:
        """
        Rimuove un Privacy Pattern dall'indice.
        
        Args:
            pattern_id (int): ID del pattern da rimuovere
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if not self.es:
            return False
        
        try:
            self.es.delete(index=self.index_name, id=pattern_id)
            logger.info(f"Pattern (ID: {pattern_id}) rimosso dall'indice con successo.")
            return True
        except Exception as e:
            logger.error(f"Errore nella rimozione del pattern {pattern_id} dall'indice: {str(e)}")
            return False
    
    @circuit_breaker("elasticsearch_search", fallback_function=lambda *args, **kwargs: {"total": 0, "results": []})
    def search_patterns(
        self, 
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
        Esegue una ricerca nell'indice dei Privacy Patterns.
        
        Args:
            query (str, optional): Query di ricerca full-text
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
        if not self.es:
            return {"total": 0, "results": []}
        
        try:
            # Costruisci query Elasticsearch
            should_clauses = []
            filter_clauses = []
            
            # Full-text search
            if query:
                should_clauses.extend([
                    {"match": {"title": {"query": query, "boost": 3}}},
                    {"match": {"description": {"query": query, "boost": 2}}},
                    {"match": {"context": {"query": query}}},
                    {"match": {"problem": {"query": query}}},
                    {"match": {"solution": {"query": query}}},
                    {"match": {"consequences": {"query": query}}}
                ])
            
            # Filtri
            if strategy:
                filter_clauses.append({"term": {"strategy": strategy}})
            
            if mvc_component:
                filter_clauses.append({"term": {"mvc_component": mvc_component}})
            
            if gdpr_id:
                filter_clauses.append({
                    "nested": {
                        "path": "gdpr_articles",
                        "query": {"term": {"gdpr_articles.id": gdpr_id}}
                    }
                })
            
            if pbd_id:
                filter_clauses.append({
                    "nested": {
                        "path": "pbd_principles",
                        "query": {"term": {"pbd_principles.id": pbd_id}}
                    }
                })
            
            if iso_id:
                filter_clauses.append({
                    "nested": {
                        "path": "iso_phases",
                        "query": {"term": {"iso_phases.id": iso_id}}
                    }
                })
            
            if vulnerability_id:
                filter_clauses.append({
                    "nested": {
                        "path": "vulnerabilities",
                        "query": {"term": {"vulnerabilities.id": vulnerability_id}}
                    }
                })
            
            # Costruisci body della query
            body = {
                "from": from_pos,
                "size": size,
                "sort": [{"_score": {"order": "desc"}}, {"created_at": {"order": "desc"}}],
                "query": {
                    "bool": {}
                }
            }
            
            # Aggiungi clausole should e filter
            if should_clauses:
                body["query"]["bool"]["should"] = should_clauses
                body["query"]["bool"]["minimum_should_match"] = 1
            
            if filter_clauses:
                body["query"]["bool"]["filter"] = filter_clauses
            
            # Se non ci sono clausole di ricerca, usa match_all
            if not should_clauses and not filter_clauses:
                body["query"] = {"match_all": {}}
            
            # Esegui ricerca
            response = self.es.search(index=self.index_name, body=body)
            
            # Elabora risultati
            hits = response["hits"]["hits"]
            total = response["hits"]["total"]["value"]
            
            results = []
            for hit in hits:
                source = hit["_source"]
                results.append(source)
            
            return {
                "total": total,
                "results": results
            }
        except exceptions.ConnectionError as e:
            logger.error(f"Errore di connessione a Elasticsearch: {str(e)}")
            return {"total": 0, "results": [], "error": "connection_error"}
        except exceptions.NotFoundError as e:
            logger.error(f"Indice non trovato in Elasticsearch: {str(e)}")
            return {"total": 0, "results": [], "error": "index_not_found"}
        except Exception as e:
            logger.error(f"Errore imprevisto nella ricerca Elasticsearch: {str(e)}")
            return {"total": 0, "results": [], "error": "general_error"}
    
    def get_autocomplete_suggestions(
        self, 
        query: str,
        limit: int = 10,
        fields: List[str] = ["title", "description", "strategy"],
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        Ottiene suggerimenti di autocompletamento basati sul query utente.
        
        Args:
            query (str): Query utente parziale
            limit (int): Numero massimo di suggerimenti
            fields (List[str]): Campi su cui effettuare l'autocomplete
            db (Session): Sessione database per il fallback
            
        Returns:
            List[Dict[str, Any]]: Lista di suggerimenti
        """
        if not self.es or not query:
            # Fallback alla ricerca DB se ES non disponibile
            return self._db_autocomplete_fallback(db, query, limit) if db else []
        
        try:
            # Crea una query multi-field più sofisticata
            should_clauses = []
            for field in fields:
                should_clauses.append({
                    "match_phrase_prefix": {
                        field: {
                            "query": query,
                            "max_expansions": 10,
                            "slop": 2,
                            "boost": 2.0 if field == "title" else 1.0
                        }
                    }
                })
            
            body = {
                "size": limit,
                "_source": ["id", "title", "strategy", "description"],
                "query": {
                    "bool": {
                        "should": should_clauses,
                        "minimum_should_match": 1
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {"number_of_fragments": 0},
                        "description": {"fragment_size": 50, "number_of_fragments": 1}
                    },
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                }
            }
            
            response = self.es.search(
                index=self.index_name,
                body=body
            )
            
            suggestions = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                highlights = hit.get("highlight", {})
                
                # Usa highlight se disponibile, altrimenti usa source
                title = highlights.get("title", [source["title"]])[0]
                description = highlights.get(
                    "description", 
                    [source["description"][:50] + "..."] if len(source["description"]) > 50 else [source["description"]]
                )[0]
                
                suggestions.append({
                    "id": source["id"],
                    "title": title,
                    "strategy": source["strategy"],
                    "description": description,
                    "score": hit["_score"]
                })
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Errore in autocomplete: {str(e)}")
            return self._db_autocomplete_fallback(db, query, limit) if db else []
    
    def _db_autocomplete_fallback(self, db: Session, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Metodo di fallback per autocomplete usando il database standard.
        
        Args:
            db (Session): Sessione database
            query (str): Query utente parziale
            limit (int): Numero massimo di suggerimenti
            
        Returns:
            List[Dict[str, Any]]: Lista di suggerimenti
        """
        if not db or not query:
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
                description = pattern.description[:50] + "..." if len(pattern.description) > 50 else pattern.description
                
                suggestions.append({
                    "id": pattern.id,
                    "title": pattern.title,
                    "strategy": pattern.strategy,
                    "description": description,
                    "score": 1.0  # Score uniforme per il fallback
                })
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Errore nel fallback autocomplete DB: {str(e)}")
            return []