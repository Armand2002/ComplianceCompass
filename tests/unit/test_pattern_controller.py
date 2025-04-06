# tests/unit/test_pattern_controller.py
"""
Test unitari per il controller dei pattern.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from src.controllers.pattern_controller import PatternController
from src.models.privacy_pattern import PrivacyPattern
from src.schemas.privacy_pattern import PatternCreate, PatternUpdate

class TestPatternController:
    """Test suite per PatternController."""
    
    def test_get_pattern_success(self, db_session, mocker):
        """Test che get_pattern restituisca il pattern quando esiste."""
        # Mock per il pattern
        mock_pattern = mocker.MagicMock(spec=PrivacyPattern)
        mock_pattern.id = 1
        mock_pattern.title = "Test Pattern"
        
        # Mock per il risultato della query
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = mock_pattern
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Esegue test
        result = PatternController.get_pattern(db_session, pattern_id=1)
        
        # Verifica risultato
        assert result == mock_pattern
        query_mock.filter.assert_called_once()
    
    def test_get_pattern_not_found(self, db_session, mocker):
        """Test che get_pattern restituisca None quando il pattern non esiste."""
        # Mock per il risultato della query
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = None
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Esegue test
        result = PatternController.get_pattern(db_session, pattern_id=999)
        
        # Verifica risultato
        assert result is None
        query_mock.filter.assert_called_once()
    
    def test_create_pattern_success(self, db_session, mocker):
        """Test che create_pattern crei correttamente un nuovo pattern."""
        # Mock per verificare titolo duplicato
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = None
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Mock per l'utente corrente
        mock_user = mocker.MagicMock()
        mock_user.id = 1
        
        # Dati pattern per la creazione
        pattern_data = PatternCreate(
            title="New Pattern",
            description="This is a test pattern",
            context="Test context",
            problem="Test problem",
            solution="Test solution",
            consequences="Test consequences",
            strategy="Test",
            mvc_component="Model"
        )
        
        # Esegue test
        result = PatternController.create_pattern(db_session, pattern_data, current_user=mock_user)
        
        # Verifica risultato
        assert result.title == "New Pattern"
        assert result.description == "This is a test pattern"
        assert result.strategy == "Test"
        assert result.mvc_component == "Model"
        assert result.created_by_id == 1
        
        # Verifica che il pattern sia stato salvato
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        db_session.refresh.assert_called_once()
    
    def test_create_pattern_duplicate_title(self, db_session, mocker):
        """Test che create_pattern sollevi un'eccezione se il titolo è già in uso."""
        # Mock per pattern esistente con lo stesso titolo
        mock_existing_pattern = mocker.MagicMock(spec=PrivacyPattern)
        mock_existing_pattern.id = 1
        mock_existing_pattern.title = "Existing Pattern"
        
        # Mock per il risultato della query
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = mock_existing_pattern
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Mock per l'utente corrente
        mock_user = mocker.MagicMock()
        mock_user.id = 1
        
        # Dati pattern per la creazione
        pattern_data = PatternCreate(
            title="Existing Pattern",  # Titolo già esistente
            description="This is a test pattern",
            context="Test context",
            problem="Test problem",
            solution="Test solution",
            consequences="Test consequences",
            strategy="Test",
            mvc_component="Model"
        )
        
        # Esegue test e verifica eccezione
        with pytest.raises(HTTPException) as excinfo:
            PatternController.create_pattern(db_session, pattern_data, current_user=mock_user)
        
        # Verifica eccezione
        assert excinfo.value.status_code == 400
        assert "già esistente" in excinfo.value.detail
    
    def test_update_pattern_success(self, db_session, mocker):
        """Test che update_pattern aggiorni correttamente un pattern esistente."""
        # Mock per il pattern esistente
        mock_pattern = mocker.MagicMock(spec=PrivacyPattern)
        mock_pattern.id = 1
        mock_pattern.title = "Original Pattern"
        mock_pattern.description = "Original Description"
        mock_pattern.strategy = "Original"
        mock_pattern.mvc_component = "Model"
        mock_pattern.created_by_id = 1
        
        # Mock per il risultato della query
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = mock_pattern
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Mock per l'utente corrente
        mock_user = mocker.MagicMock()
        mock_user.id = 1
        mock_user.is_admin = False
        
        # Dati aggiornamento pattern
        pattern_update = PatternUpdate(
            title="Updated Pattern",
            description="Updated Description",
            strategy="Updated"
        )
        
        # Esegue test
        result = PatternController.update_pattern(db_session, pattern_id=1, pattern_update=pattern_update, current_user=mock_user)
        
        # Verifica risultato
        assert result == mock_pattern
        assert mock_pattern.title == "Updated Pattern"
        assert mock_pattern.description == "Updated Description"
        assert mock_pattern.strategy == "Updated"
        
        # Verifica che le modifiche siano state salvate
        db_session.commit.assert_called_once()
    
    def test_delete_pattern_success(self, db_session, mocker):
        """Test che delete_pattern elimini correttamente un pattern."""
        # Mock per il pattern esistente
        mock_pattern = mocker.MagicMock(spec=PrivacyPattern)
        mock_pattern.id = 1
        mock_pattern.created_by_id = 1
        
        # Mock per il risultato della query
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = mock_pattern
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Mock per l'utente corrente
        mock_user = mocker.MagicMock()
        mock_user.id = 1
        mock_user.is_admin = True
        
        # Esegue test
        result = PatternController.delete_pattern(db_session, pattern_id=1, current_user=mock_user)
        
        # Verifica risultato
        assert result is True
        
        # Verifica che il pattern sia stato eliminato
        db_session.delete.assert_called_once_with(mock_pattern)
        db_session.commit.assert_called_once()