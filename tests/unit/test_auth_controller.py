# tests/unit/test_auth_controller.py
"""
Test unitari per il controller di autenticazione.
"""
import pytest
from datetime import datetime
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from unittest.mock import MagicMock, patch

from src.controllers.auth_controller import AuthController
from src.models.user_model import User, UserRole
from src.schemas.auth import UserRegister


class TestAuthController:
    """Test suite per AuthController."""
    
    def test_authenticate_user_success(self, db_session, mocker):
        """Test che authenticate_user restituisca l'utente se le credenziali sono corrette."""
        # Mock per l'utente
        mock_user = mocker.MagicMock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        
        # Mock per il risultato della query
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = mock_user
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Mock per verify_password
        with patch("src.controllers.auth_controller.verify_password", return_value=True):
            # Esegue test
            result = AuthController.authenticate_user(db_session, "test@example.com", "password123")
            
            # Verifica risultato
            assert result == mock_user
            query_mock.filter.assert_called_once()
    
    def test_authenticate_user_user_not_found(self, db_session, mocker):
        """Test che authenticate_user restituisca None se l'utente non esiste."""
        # Mock per il risultato della query
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = None
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Esegue test
        result = AuthController.authenticate_user(db_session, "nonexistent@example.com", "password123")
        
        # Verifica risultato
        assert result is None
        query_mock.filter.assert_called_once()
    
    def test_authenticate_user_wrong_password(self, db_session, mocker):
        """Test che authenticate_user restituisca None se la password è errata."""
        # Mock per l'utente
        mock_user = mocker.MagicMock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        
        # Mock per il risultato della query
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = mock_user
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Mock per verify_password
        with patch("src.controllers.auth_controller.verify_password", return_value=False):
            # Esegue test
            result = AuthController.authenticate_user(db_session, "test@example.com", "wrong_password")
            
            # Verifica risultato
            assert result is None
            query_mock.filter.assert_called_once()
    
    def test_login_success(self, db_session, mocker):
        """Test che login restituisca i token se le credenziali sono corrette."""
        # Mock per l'utente
        mock_user = mocker.MagicMock()
        mock_user.id = 1
        mock_user.is_active = True
        mock_user.role = UserRole.ADMIN
        
        # Mock per authenticate_user
        mocker.patch.object(
            AuthController, "authenticate_user", return_value=mock_user
        )
        
        # Mock per create_access_token e create_refresh_token
        mocker.patch(
            "src.controllers.auth_controller.create_access_token", return_value="access_token"
        )
        mocker.patch(
            "src.controllers.auth_controller.create_refresh_token", return_value="refresh_token"
        )
        
        # Mock per form_data
        form_data = OAuth2PasswordRequestForm(username="test@example.com", password="password123")
        
        # Esegue test
        result = AuthController.login(db_session, form_data)
        
        # Verifica risultato
        assert result == {
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "token_type": "bearer"
        }
    
    def test_login_invalid_credentials(self, db_session, mocker):
        """Test che login sollevi un'eccezione se le credenziali sono errate."""
        # Mock per authenticate_user
        mocker.patch.object(
            AuthController, "authenticate_user", return_value=None
        )
        
        # Mock per form_data
        form_data = OAuth2PasswordRequestForm(username="test@example.com", password="wrong_password")
        
        # Esegue test e verifica eccezione
        with pytest.raises(HTTPException) as excinfo:
            AuthController.login(db_session, form_data)
        
        # Verifica eccezione
        assert excinfo.value.status_code == 401
        assert "Email o password non corrette" in excinfo.value.detail
    
    def test_login_inactive_user(self, db_session, mocker):
        """Test che login sollevi un'eccezione se l'utente è disattivato."""
        # Mock per l'utente
        mock_user = mocker.MagicMock()
        mock_user.is_active = False
        
        # Mock per authenticate_user
        mocker.patch.object(
            AuthController, "authenticate_user", return_value=mock_user
        )
        
        # Mock per form_data
        form_data = OAuth2PasswordRequestForm(username="test@example.com", password="password123")
        
        # Esegue test e verifica eccezione
        with pytest.raises(HTTPException) as excinfo:
            AuthController.login(db_session, form_data)
        
        # Verifica eccezione
        assert excinfo.value.status_code == 403
        assert "Account disattivato" in excinfo.value.detail
    
    def test_register_success(self, db_session, mocker):
        """Test che register crei correttamente un nuovo utente."""
        # Mock per le query di verifica esistenza email e username
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = None
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Mock per get_password_hash
        mocker.patch(
            "src.controllers.auth_controller.get_password_hash",
            return_value="hashed_password"
        )
        
        # Dati utente per la registrazione
        user_data = UserRegister(
            email="new@example.com",
            username="newuser",
            password="password123",
            full_name="New User"
        )
        
        # Esegue test
        result = AuthController.register(db_session, user_data)
        
        # Verifica risultato
        assert result.email == "new@example.com"
        assert result.username == "newuser"
        assert result.full_name == "New User"
        assert result.role == UserRole.VIEWER
        assert result.is_active is True
    
    def test_register_email_exists(self, db_session, mocker):
        """Test che register sollevi un'eccezione se l'email è già in uso."""
        # Mock per la query di verifica email
        query_mock = mocker.MagicMock()
        query_mock.filter.return_value.first.return_value = MagicMock()  # Email esiste
        
        # Mock per db.query
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Dati utente per la registrazione
        user_data = UserRegister(
            email="existing@example.com",
            username="newuser",
            password="password123",
            full_name="New User"
        )
        
        # Esegue test e verifica eccezione
        with pytest.raises(HTTPException) as excinfo:
            AuthController.register(db_session, user_data)
        
        # Verifica eccezione
        assert excinfo.value.status_code == 400
        assert "Email già registrata" in excinfo.value.detail
    
    def test_register_username_exists(self, db_session, mocker):
        """Test che register sollevi un'eccezione se lo username è già in uso."""
        # Mock per la query di verifica email
        email_query = mocker.MagicMock()
        email_query.filter.return_value.first.return_value = None  # Email non esiste
        
        # Mock per la query di verifica username
        username_query = mocker.MagicMock()
        username_query.filter.return_value.first.return_value = MagicMock()  # Username esiste
        
        # Mock per db.query con side effects
        query_mock = mocker.MagicMock()
        query_mock.filter.side_effect = [
            email_query.filter.return_value,
            username_query.filter.return_value
        ]
        mocker.patch.object(db_session, "query", return_value=query_mock)
        
        # Dati utente per la registrazione
        user_data = UserRegister(
            email="new@example.com",
            username="existing",
            password="password123",
            full_name="New User"
        )
        
        # Esegue test e verifica eccezione
        with pytest.raises(HTTPException) as excinfo:
            AuthController.register(db_session, user_data)
        
        # Verifica eccezione
        assert excinfo.value.status_code == 400
        assert "Username già in uso" in excinfo.value.detail