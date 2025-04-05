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
    
    def test_authenticate_user_success(self, db, monkeypatch):
        """Test che authenticate_user restituisca l'utente se le credenziali sono corrette."""
        # Mock per l'utente
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        
        # Mock per il risultato della query
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = mock_user
        
        # Mock per db.query
        monkeypatch.setattr(db, "query", lambda user_model: query_mock)
        
        # Mock per verify_password
        with patch("src.controllers.auth_controller.verify_password", return_value=True):
            # Esegue test
            result = AuthController.authenticate_user(db, "test@example.com", "password123")
            
            # Verifica risultato
            assert result == mock_user
            query_mock.filter.assert_called_once()
    
    def test_authenticate_user_user_not_found(self, db, monkeypatch):
        """Test che authenticate_user restituisca None se l'utente non esiste."""
        # Mock per il risultato della query
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = None
        
        # Mock per db.query
        monkeypatch.setattr(db, "query", lambda user_model: query_mock)
        
        # Esegue test
        result = AuthController.authenticate_user(db, "nonexistent@example.com", "password123")
        
        # Verifica risultato
        assert result is None
        query_mock.filter.assert_called_once()
    
    def test_authenticate_user_wrong_password(self, db, monkeypatch):
        """Test che authenticate_user restituisca None se la password è errata."""
        # Mock per l'utente
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        
        # Mock per il risultato della query
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = mock_user
        
        # Mock per db.query
        monkeypatch.setattr(db, "query", lambda user_model: query_mock)
        
        # Mock per verify_password
        with patch("src.controllers.auth_controller.verify_password", return_value=False):
            # Esegue test
            result = AuthController.authenticate_user(db, "test@example.com", "wrong_password")
            
            # Verifica risultato
            assert result is None
            query_mock.filter.assert_called_once()
    
    def test_login_success(self, db, monkeypatch):
        """Test che login restituisca i token se le credenziali sono corrette."""
        # Mock per l'utente
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_active = True
        mock_user.role = UserRole.ADMIN
        
        # Mock per authenticate_user
        with patch.object(
            AuthController, "authenticate_user", return_value=mock_user
        ) as mock_auth:
            # Mock per create_access_token e create_refresh_token
            with patch(
                "src.controllers.auth_controller.create_access_token", return_value="access_token"
            ) as mock_access:
                with patch(
                    "src.controllers.auth_controller.create_refresh_token", return_value="refresh_token"
                ) as mock_refresh:
                    # Mock per form_data
                    form_data = OAuth2PasswordRequestForm(username="test@example.com", password="password123")
                    
                    # Esegue test
                    result = AuthController.login(db, form_data)
                    
                    # Verifica risultato
                    assert result == {
                        "access_token": "access_token",
                        "refresh_token": "refresh_token",
                        "token_type": "bearer"
                    }
                    mock_auth.assert_called_once_with(db=db, email="test@example.com", password="password123")
                    mock_access.assert_called_once()
                    mock_refresh.assert_called_once()
                    assert mock_user.last_login is not None
    
    def test_login_invalid_credentials(self, db, monkeypatch):
        """Test che login sollevi un'eccezione se le credenziali sono errate."""
        # Mock per authenticate_user
        with patch.object(
            AuthController, "authenticate_user", return_value=None
        ) as mock_auth:
            # Mock per form_data
            form_data = OAuth2PasswordRequestForm(username="test@example.com", password="wrong_password")
            
            # Esegue test e verifica eccezione
            with pytest.raises(HTTPException) as excinfo:
                AuthController.login(db, form_data)
            
            # Verifica eccezione
            assert excinfo.value.status_code == 401
            assert "Email o password non corrette" in excinfo.value.detail
            mock_auth.assert_called_once_with(db=db, email="test@example.com", password="wrong_password")
    
    def test_login_inactive_user(self, db, monkeypatch):
        """Test che login sollevi un'eccezione se l'utente è disattivato."""
        # Mock per l'utente
        mock_user = MagicMock()
        mock_user.is_active = False
        
        # Mock per authenticate_user
        with patch.object(
            AuthController, "authenticate_user", return_value=mock_user
        ) as mock_auth:
            # Mock per form_data
            form_data = OAuth2PasswordRequestForm(username="test@example.com", password="password123")
            
            # Esegue test e verifica eccezione
            with pytest.raises(HTTPException) as excinfo:
                AuthController.login(db, form_data)
            
            # Verifica eccezione
            assert excinfo.value.status_code == 403
            assert "Account disattivato" in excinfo.value.detail
            mock_auth.assert_called_once_with(db=db, email="test@example.com", password="password123")
    
    def test_register_success(self, db, monkeypatch):
        """Test che register crei correttamente un nuovo utente."""
        # Mock per le query di verifica esistenza email e username
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = None
        
        # Mock per db.query
        monkeypatch.setattr(db, "query", lambda user_model: query_mock)
        
        # Mock per get_password_hash
        with patch(
            "src.controllers.auth_controller.get_password_hash", return_value="hashed_password"
        ) as mock_hash:
            # Dati utente per la registrazione
            user_data = UserRegister(
                email="new@example.com",
                username="newuser",
                password="password123",
                full_name="New User"
            )
            
            # Esegue test
            result = AuthController.register(db, user_data)
            
            # Verifica risultato
            assert result.email == "new@example.com"
            assert result.username == "newuser"
            assert result.full_name == "New User"
            assert result.role == UserRole.VIEWER
            assert result.is_active is True
            mock_hash.assert_called_once_with("password123")
            db.add.assert_called_once()
            db.commit.assert_called_once()
            db.refresh.assert_called_once()
    
    def test_register_email_exists(self, db, monkeypatch):
        """Test che register sollevi un'eccezione se l'email è già in uso."""
        # Mock per la query di verifica email
        email_query_mock = MagicMock()
        email_query_mock.filter.return_value.first.return_value = MagicMock()  # Email esiste
        
        # Mock per db.query
        monkeypatch.setattr(db, "query", lambda user_model: email_query_mock)
        
        # Dati utente per la registrazione
        user_data = UserRegister(
            email="existing@example.com",
            username="newuser",
            password="password123",
            full_name="New User"
        )
        
        # Esegue test e verifica eccezione
        with pytest.raises(HTTPException) as excinfo:
            AuthController.register(db, user_data)
        
        # Verifica eccezione
        assert excinfo.value.status_code == 400
        assert "Email già registrata" in excinfo.value.detail
    
    def test_register_username_exists(self, db, monkeypatch):
        """Test che register sollevi un'eccezione se lo username è già in uso."""
        # Mock per la query di verifica email
        email_query_mock = MagicMock()
        email_query_mock.filter.return_value.first.return_value = None  # Email non esiste
        
        # Mock per la query di verifica username
        username_query_mock = MagicMock()
        username_query_mock.filter.return_value.first.return_value = MagicMock()  # Username esiste
        
        # Configurazione mock
        db.query.side_effect = [email_query_mock, username_query_mock]
        
        # Dati utente per la registrazione
        user_data = UserRegister(
            email="new@example.com",
            username="existing",
            password="password123",
            full_name="New User"
        )
        
        # Esegue test e verifica eccezione
        with pytest.raises(HTTPException) as excinfo:
            AuthController.register(db, user_data)
        
        # Verifica eccezione
        assert excinfo.value.status_code == 400
        assert "Username già in uso" in excinfo.value.detail
    
    def test_change_password_success(self, db, monkeypatch):
        """Test che change_password aggiorni correttamente la password."""
        # Mock per l'utente
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.hashed_password = "old_hashed_password"
        
        # Mock per db.query
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = mock_user
        monkeypatch.setattr(db, "query", lambda user_model: query_mock)
        
        # Mock per verify_password e get_password_hash
        with patch(
            "src.controllers.auth_controller.verify_password", return_value=True
        ) as mock_verify:
            with patch(
                "src.controllers.auth_controller.get_password_hash", return_value="new_hashed_password"
            ) as mock_hash:
                # Esegue test
                result = AuthController.change_password(
                    db, user_id=1, current_password="current_password", new_password="new_password"
                )
                
                # Verifica risultato
                assert result is True
                mock_verify.assert_called_once_with("current_password", "old_hashed_password")
                mock_hash.assert_called_once_with("new_password")
                assert mock_user.hashed_password == "new_hashed_password"
                assert mock_user.updated_at is not None
                db.commit.assert_called_once()
    
    def test_change_password_user_not_found(self, db, monkeypatch):
        """Test che change_password sollevi un'eccezione se l'utente non esiste."""
        # Mock per db.query
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = None
        monkeypatch.setattr(db, "query", lambda user_model: query_mock)
        
        # Esegue test e verifica eccezione
        with pytest.raises(HTTPException) as excinfo:
            AuthController.change_password(
                db, user_id=999, current_password="current_password", new_password="new_password"
            )
        
        # Verifica eccezione
        assert excinfo.value.status_code == 404
        assert "Utente non trovato" in excinfo.value.detail
    
    def test_change_password_wrong_current_password(self, db, monkeypatch):
        """Test che change_password sollevi un'eccezione se la password attuale è errata."""
        # Mock per l'utente
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.hashed_password = "old_hashed_password"
        
        # Mock per db.query
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = mock_user
        monkeypatch.setattr(db, "query", lambda user_model: query_mock)
        
        # Mock per verify_password
        with patch(
            "src.controllers.auth_controller.verify_password", return_value=False
        ) as mock_verify:
            # Esegue test e verifica eccezione
            with pytest.raises(HTTPException) as excinfo:
                AuthController.change_password(
                    db, user_id=1, current_password="wrong_password", new_password="new_password"
                )
            
            # Verifica eccezione
            assert excinfo.value.status_code == 400
            assert "Password attuale non corretta" in excinfo.value.detail
            mock_verify.assert_called_once_with("wrong_password", "old_hashed_password")
    
    def test_change_password_too_short(self, db, monkeypatch):
        """Test che change_password sollevi un'eccezione se la nuova password è troppo corta."""
        # Mock per l'utente
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.hashed_password = "old_hashed_password"
        
        # Mock per db.query
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = mock_user
        monkeypatch.setattr(db, "query", lambda user_model: query_mock)
        
        # Mock per verify_password
        with patch(
            "src.controllers.auth_controller.verify_password", return_value=True
        ) as mock_verify:
            # Esegue test e verifica eccezione
            with pytest.raises(HTTPException) as excinfo:
                AuthController.change_password(
                    db, user_id=1, current_password="current_password", new_password="short"
                )
            
            # Verifica eccezione
            assert excinfo.value.status_code == 400
            assert "La password deve essere di almeno 8 caratteri" in excinfo.value.detail
            mock_verify.assert_called_once_with("current_password", "old_hashed_password")