# tests/unit/test_search_service.py
"""
Test unitari per il servizio di ricerca.

Verifica funzionalità specifiche del servizio di ricerca,
usando mock per isolarlo dalle dipendenze esterne.
"""
import pytest
import logging
from unittest.mock import patch, MagicMock, call, ANY
from elasticsearch import Elasticsearch, NotFoundError, TransportError
from sqlalchemy.orm import Session

from src.services.search_service import SearchService
from src.models.privacy_pattern import PrivacyPattern

class TestSearchService:
    """Test suite per SearchService."""
    
    def test_init_with_available_elasticsearch(self):
        """Verifica l'inizializzazione con Elasticsearch disponibile."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch disponibile
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_es.return_value = mock_instance
            
            service = SearchService()
            
            # Verifica corretta inizializzazione
            assert service.es is not None
            assert service.es == mock_instance
            assert mock_instance.ping.called
    
    def test_init_with_unavailable_elasticsearch(self):
        """Verifica l'inizializzazione con Elasticsearch non disponibile."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch non disponibile
            mock_instance = MagicMock()
            mock_instance.ping.return_value = False
            mock_es.return_value = mock_instance
            
            service = SearchService()
            
            # Verifica corretta gestione
            assert service.es is None  # Verifica direttamente la proprietà es invece di connected
    
    def test_init_with_connection_error(self):
        """Verifica l'inizializzazione con errore di connessione."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula errore connessione
            mock_es.side_effect = Exception("Connection failed")
            
            service = SearchService()
            
            # Verifica corretta gestione
            assert service.es is None
    
    def test_create_index_success(self):
        """Verifica creazione indice con successo."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch disponibile
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.indices.exists.return_value = False
            mock_es.return_value = mock_instance
            
            service = SearchService()
            result = service.create_index()
            
            # Verifica corretta creazione
            assert result is True
            assert mock_instance.indices.create.called
            
            # Verifica configurazione corretta
            create_args = mock_instance.indices.create.call_args[1]
            assert "body" in create_args
            assert "settings" in create_args["body"]
            assert "mappings" in create_args["body"]
    
    def test_create_index_already_exists(self):
        """Verifica comportamento quando l'indice esiste già."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula indice già esistente
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.indices.exists.return_value = True
            mock_es.return_value = mock_instance
            
            service = SearchService()
            result = service.create_index()
            
            # Verifica corretta gestione
            assert result is True
            assert not mock_instance.indices.create.called
    
    def test_create_index_error(self):
        """Verifica gestione errori durante creazione indice."""
        with patch("src.services.search_service.Elasticsearch") as mock_es, \
             patch("src.services.search_service.logger") as mock_logger:
            # Simula errore creazione
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.indices.exists.return_value = False
            mock_instance.indices.create.side_effect = Exception("Failed to create index")
            mock_es.return_value = mock_instance
            
            service = SearchService()
            result = service.create_index()
            
            # Verifica corretta gestione errore
            assert result is False
            mock_logger.error.assert_called_once()
    
    def test_index_pattern(self):
        """Verifica indicizzazione pattern."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch disponibile
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.indices.exists.return_value = True
            mock_es.return_value = mock_instance
            
            # Mock per il pattern
            mock_pattern = MagicMock(spec=PrivacyPattern)
            mock_pattern.id = 1
            mock_pattern.title = "Test Pattern"
            mock_pattern.description = "Test Description"
            mock_pattern.strategy = "Test Strategy"
            mock_pattern.mvc_component = "Model"
            mock_pattern.created_at.isoformat.return_value = "2023-01-01T00:00:00"
            mock_pattern.updated_at.isoformat.return_value = "2023-01-01T00:00:00"
            mock_pattern.gdpr_articles = []
            mock_pattern.pbd_principles = []
            mock_pattern.iso_phases = []
            mock_pattern.vulnerabilities = []
            
            service = SearchService()
            result = service.index_pattern(mock_pattern)
            
            # Verifica corretta indicizzazione
            assert result is True
            mock_instance.index.assert_called_once()
            
            # Verifica dati corretti
            call_args = mock_instance.index.call_args
            assert call_args[1]['id'] == 1
            assert 'body' in call_args[1]
            assert call_args[1]['body']['title'] == "Test Pattern"
    
    def test_reindex_all_patterns(self):
        """Verifica la funzionalità di reindicizzazione completa."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch disponibile
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.indices.exists.return_value = True
            mock_es.return_value = mock_instance
            
            # Mock del DB e patterns
            mock_db = MagicMock(spec=Session)
            mock_patterns = [MagicMock(spec=PrivacyPattern) for _ in range(3)]
            for i, pattern in enumerate(mock_patterns):
                pattern.id = i + 1
                pattern.title = f"Test Pattern {i+1}"
                pattern.created_at.isoformat.return_value = "2023-01-01T00:00:00"
                pattern.updated_at.isoformat.return_value = "2023-01-01T00:00:00"
                pattern.gdpr_articles = []
                pattern.pbd_principles = []
                pattern.iso_phases = []
                pattern.vulnerabilities = []
            
            mock_db.query.return_value.all.return_value = mock_patterns
            
            service = SearchService()
            result = service.reindex_all_patterns(mock_db)
            
            # Verifica corretta reindicizzazione
            assert result is True
            assert mock_instance.indices.delete.called
            assert mock_instance.indices.create.called
            assert mock_instance.index.call_count == 3
    
    def test_remove_pattern_from_index(self):
        """Verifica la rimozione di un pattern dall'indice."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch disponibile
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_es.return_value = mock_instance
            
            service = SearchService()
            result = service.remove_pattern_from_index(pattern_id=1)
            
            # Verifica corretta rimozione
            assert result is True
            mock_instance.delete.assert_called_once_with(index=service.index_name, id=1)
    
    def test_remove_pattern_from_index_error(self):
        """Verifica gestione errori durante rimozione pattern."""
        with patch("src.services.search_service.Elasticsearch") as mock_es, \
             patch("src.services.search_service.logger") as mock_logger:
            # Simula errore rimozione
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.delete.side_effect = NotFoundError("Document not found")
            mock_es.return_value = mock_instance
            
            service = SearchService()
            result = service.remove_pattern_from_index(pattern_id=1)
            
            # Verifica corretta gestione errore
            assert result is False
            mock_logger.error.assert_called_once()
    
    @pytest.mark.parametrize("search_term,expected_query", [
        (None, {"match_all": {}}),
        ("privacy", {"bool": {"should": [{"match": {"title": {"query": "privacy", "boost": 3}}}, ANY]}}),
    ])
    def test_search_patterns_query_construction(self, search_term, expected_query):
        """Verifica costruzione query di ricerca con vari parametri."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch disponibile
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.search.return_value = {
                "hits": {"total": {"value": 0}, "hits": []}
            }
            mock_es.return_value = mock_instance
            
            service = SearchService()
            service.search_patterns(query=search_term)
            
            # Verifica costruzione query
            search_args = mock_instance.search.call_args[1]
            assert "body" in search_args
            
            # Verifica tipo di query corretto
            if search_term is None:
                assert "match_all" in search_args["body"]["query"]
            else:
                assert "bool" in search_args["body"]["query"]
                assert "should" in search_args["body"]["query"]["bool"]
    
    def test_search_patterns_with_filters(self):
        """Verifica costruzione query con filtri applicati."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch disponibile
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.search.return_value = {
                "hits": {"total": {"value": 0}, "hits": []}
            }
            mock_es.return_value = mock_instance
            
            service = SearchService()
            service.search_patterns(
                strategy="Minimize",
                mvc_component="Model",
                gdpr_id=1,
                pbd_id=2
            )
            
            # Verifica costruzione query con filtri
            search_args = mock_instance.search.call_args[1]
            assert "body" in search_args
            assert "filter" in search_args["body"]["query"]["bool"]
            filter_clauses = search_args["body"]["query"]["bool"]["filter"]
            assert len(filter_clauses) == 4  # 4 filtri applicati
    
    def test_search_patterns_with_error(self):
        """Verifica gestione errori durante ricerca."""
        with patch("src.services.search_service.Elasticsearch") as mock_es, \
             patch("src.services.search_service.logger") as mock_logger:
            # Simula errore ricerca
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.search.side_effect = TransportError(500, "Search failed")
            mock_es.return_value = mock_instance
            
            service = SearchService()
            result = service.search_patterns(query="test")
            
            # Verifica risultato vuoto con info errore
            assert result["total"] == 0
            assert len(result["results"]) == 0
            assert "error" in result
            assert result["error"] == "general_error"
            mock_logger.error.assert_called_once()
    
    def test_search_without_elasticsearch(self):
        """Verifica ricerca senza Elasticsearch disponibile."""
        service = SearchService()
        service.es = None  # Forza Elasticsearch non disponibile
        
        result = service.search_patterns(query="test")
        
        # Verifica risultato vuoto
        assert result["total"] == 0
        assert len(result["results"]) == 0
    
    def test_get_autocomplete_suggestions_success(self):
        """Verifica che le suggstioni di autocompletamento vengano generate correttamente."""
        with patch("src.services.search_service.Elasticsearch") as mock_es:
            # Simula Elasticsearch disponibile con risposta
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            
            # Simula risposta per l'autocompletamento
            mock_instance.search.return_value = {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "id": 1,
                                "title": "Privacy Policy Pattern",
                                "strategy": "Inform",
                                "description": "A pattern for privacy policies"
                            },
                            "_score": 1.5,
                            "highlight": {
                                "title": ["<strong>Privacy</strong> Policy Pattern"],
                                "description": ["A pattern for <strong>privacy</strong> policies"]
                            }
                        }
                    ]
                }
            }
            
            mock_es.return_value = mock_instance
            
            service = SearchService()
            results = service.get_autocomplete_suggestions(query="privacy", limit=5)
            
            # Verifica che la ricerca sia configurata correttamente
            search_args = mock_instance.search.call_args[1]
            assert "body" in search_args
            assert search_args["body"]["size"] == 5
            assert "highlight" in search_args["body"]
            
            # Verifica la formattazione dei risultati
            assert len(results) == 1
            assert results[0]["id"] == 1
            assert results[0]["title"] == "<strong>Privacy</strong> Policy Pattern"
            assert "<strong>" in results[0]["description"]
            assert results[0]["score"] == 1.5
    
    def test_get_autocomplete_suggestions_no_es(self):
        """Verifica che autocomplete funzioni con fallback al DB quando ES non è disponibile."""
        # Mock del DB per il fallback
        mock_db = MagicMock(spec=Session)
        
        # Prepara mock patterns per il fallback
        mock_pattern = MagicMock(spec=PrivacyPattern)
        mock_pattern.id = 1
        mock_pattern.title = "DB Fallback Pattern"
        mock_pattern.strategy = "Fallback"
        mock_pattern.description = "This is a fallback pattern from DB"
        
        # Configura la query mock per il fallback
        mock_query = MagicMock()
        mock_query.filter.return_value.limit.return_value.all.return_value = [mock_pattern]
        mock_db.query.return_value = mock_query
        
        service = SearchService()
        service.es = None  # Forza l'uso del fallback
        
        results = service.get_autocomplete_suggestions(query="fallback", limit=5, db=mock_db)
        
        # Verifica che il fallback al DB sia stato usato
        assert len(results) == 1
        assert results[0]["id"] == 1
        assert results[0]["title"] == "DB Fallback Pattern"
        assert mock_db.query.called
    
    def test_db_autocomplete_fallback(self):
        """Verifica l'implementazione diretta del metodo di fallback per autocomplete."""
        # Mock del DB
        mock_db = MagicMock(spec=Session)
        
        # Prepara mock patterns per il risultato
        mock_pattern = MagicMock(spec=PrivacyPattern)
        mock_pattern.id = 1
        mock_pattern.title = "Pattern Title"
        mock_pattern.strategy = "Strategy"
        mock_pattern.description = "This is a very long description that should be truncated in the results"
        
        # Configura la query mock
        mock_query = MagicMock()
        mock_query.filter.return_value.limit.return_value.all.return_value = [mock_pattern]
        mock_db.query.return_value = mock_query
        
        service = SearchService()
        results = service._db_autocomplete_fallback(mock_db, "pattern", 10)
        
        # Verifica i risultati
        assert len(results) == 1
        assert results[0]["id"] == 1
        assert results[0]["title"] == "Pattern Title"
        assert len(results[0]["description"]) <= 53  # Originale + "..."
        assert results[0]["score"] == 1.0  # Score uniforme per il fallback
    
    def test_db_autocomplete_fallback_with_error(self):
        """Verifica che il fallback gestisca correttamente gli errori."""
        with patch("src.services.search_service.logger") as mock_logger:
            # Mock del DB che genera un errore
            mock_db = MagicMock(spec=Session)
            mock_db.query.side_effect = Exception("Database error")
            
            service = SearchService()
            results = service._db_autocomplete_fallback(mock_db, "query", 10)
            
            # Verifica che l'errore sia gestito correttamente
            assert results == []
            mock_logger.error.assert_called_once()