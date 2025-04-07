# tests/unit/test_search_service.py
"""
Test unitari per il servizio di ricerca.

Verifica funzionalità specifiche del servizio di ricerca SQL,
usando mock per isolarlo dalle dipendenze esterne.
"""
import pytest
import logging
from unittest.mock import patch, MagicMock, call, ANY
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.services.search_service import SearchService
from src.models.privacy_pattern import PrivacyPattern

class TestSearchService:
    """Test suite per SearchService."""
    
    def test_init_service(self):
        """Verifica l'inizializzazione del servizio."""
        service = SearchService()
        # Verifica che il servizio sia inizializzato correttamente
        assert service.es is None  # Non dovrebbe esistere una connessione Elasticsearch
        
    def test_search_patterns_basic(self):
        """Verifica la funzionalità di ricerca base."""
        # Mock del database
        mock_db = MagicMock(spec=Session)
        
        # Mock della query e dei risultati
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.count.return_value = 1
        
        # Crea un mock di pattern per il risultato
        mock_pattern = MagicMock(spec=PrivacyPattern)
        mock_pattern.id = 1
        mock_pattern.title = "Test Pattern"
        mock_pattern.description = "Test Description"
        mock_pattern.strategy = "Test Strategy"
        mock_pattern.mvc_component = "Model"
        mock_pattern.created_at.isoformat.return_value = "2023-01-01T00:00:00"
        mock_pattern.updated_at.isoformat.return_value = "2023-01-01T00:00:00"
        
        # Configura il mock per restituire i pattern
        mock_query.all.return_value = [mock_pattern]
        mock_db.query.return_value = mock_query
        
        service = SearchService()
        result = service.search_patterns(
            db=mock_db,
            query="test",
            strategy="Test Strategy",
            from_pos=0,
            size=10
        )
        
        # Verifica il formato dei risultati
        assert "total" in result
        assert "results" in result
        assert result["total"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Pattern"
        
    def test_search_patterns_with_filters(self):
        """Verifica ricerca con filtri applicati."""
        # Mock del database
        mock_db = MagicMock(spec=Session)
        
        # Mock della query e dei risultati
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.count.return_value = 1
        
        # Crea un mock di pattern per il risultato
        mock_pattern = MagicMock(spec=PrivacyPattern)
        mock_pattern.id = 1
        mock_pattern.title = "Test Pattern"
        mock_pattern.description = "Test Description"
        mock_pattern.strategy = "Minimize"
        mock_pattern.mvc_component = "Model"
        mock_pattern.created_at.isoformat.return_value = "2023-01-01T00:00:00"
        mock_pattern.updated_at.isoformat.return_value = "2023-01-01T00:00:00"
        
        # Configura il mock per restituire i pattern
        mock_query.all.return_value = [mock_pattern]
        mock_db.query.return_value = mock_query
        
        service = SearchService()
        result = service.search_patterns(
            db=mock_db,
            strategy="Minimize",
            mvc_component="Model",
            gdpr_id=1,
            pbd_id=2
        )
        
        # Verifica il formato dei risultati
        assert "total" in result
        assert "results" in result
        assert result["total"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["strategy"] == "Minimize"
        
    def test_search_patterns_with_error(self):
        """Verifica gestione errori durante ricerca."""
        # Mock del database che solleva un errore
        mock_db = MagicMock(spec=Session)
        mock_db.query.side_effect = SQLAlchemyError("Database error")
        
        with patch("src.services.search_service.logger") as mock_logger:
            service = SearchService()
            result = service.search_patterns(db=mock_db, query="test")
            
            # Verifica risultato vuoto con info errore
            assert result["total"] == 0
            assert len(result["results"]) == 0
            assert "error" in result
            mock_logger.error.assert_called_once()
    
    def test_get_autocomplete_suggestions(self):
        """Verifica che le suggstioni di autocompletamento vengano generate correttamente."""
        # Mock del database
        mock_db = MagicMock(spec=Session)
        
        # Prepara mock patterns per il risultato
        mock_pattern = MagicMock(spec=PrivacyPattern)
        mock_pattern.id = 1
        mock_pattern.title = "Privacy Policy Pattern"
        mock_pattern.strategy = "Inform"
        mock_pattern.description = "A pattern for privacy policies"
        
        # Configura la query mock
        mock_query = MagicMock()
        mock_query.filter.return_value.limit.return_value.all.return_value = [mock_pattern]
        mock_db.query.return_value = mock_query
        
        service = SearchService()
        results = service.get_autocomplete_suggestions(query="privacy", limit=5, db=mock_db)
        
        # Verifica la formattazione dei risultati
        assert len(results) == 1
        assert results[0]["id"] == 1
        assert results[0]["title"] == "Privacy Policy Pattern"
        assert "description" in results[0]
        assert "score" in results[0]
    
    def test_db_autocomplete_fallback(self):
        """Verifica l'implementazione del metodo per autocomplete."""
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
        assert results[0]["score"] == 1.0  # Score uniforme per i risultati SQL
    
    def test_db_autocomplete_fallback_with_error(self):
        """Verifica che l'autocomplete gestisca correttamente gli errori."""
        with patch("src.services.search_service.logger") as mock_logger:
            # Mock del DB che genera un errore
            mock_db = MagicMock(spec=Session)
            mock_db.query.side_effect = Exception("Database error")
            
            service = SearchService()
            results = service._db_autocomplete_fallback(mock_db, "query", 10)
            
            # Verifica che l'errore sia gestito correttamente
            assert results == []
            mock_logger.error.assert_called_once()