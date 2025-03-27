# tests/unit/test_auth_controller.py
"""
Test per il controller di autenticazione.

Verifica le funzionalità di login, registrazione e gestione token.
"""
import pytest
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime

from src.controllers.auth_controller import AuthController
from src.schemas.auth import UserRegister
from src.utils.jwt import decode_token


class TestAuthController:
    """Test per AuthController."""
    
    def test_register_success(self, db):
        """Verifica che un utente possa registrarsi con successo."""
        # Arrange
        user_data = UserRegister(
            email="newuser@example.com",
            username="newuser",
            password="password123",
            full_name="New User"
        )
        
        # Act
        result = AuthController.register(db, user_data)
        
        # Assert
        assert result is not None
        assert result.email == "newuser@example.com"
        assert result.username == "newuser"
        assert result.full_name == "New User"
        assert result.is_active is True
    
    def test_register_duplicate_email(self, db, test_user):
        """Verifica che non si possa registrare un utente con email duplicata."""
        # Arrange
        user_data = UserRegister(
            email="test@example.com",  # Email già esistente
            username="uniqueuser",
            password="password123",
            full_name="Unique User"
        )
        
        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            AuthController.register(db, user_data)
        
        assert "Email già registrata" in str(excinfo.value)
    
    def test_register_duplicate_username(self, db, test_user):
        """Verifica che non si possa registrare un utente con username duplicato."""
        # Arrange
        user_data = UserRegister(
            email="unique@example.com",
            username="testuser",  # Username già esistente
            password="password123",
            full_name="Unique User"
        )
        
        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            AuthController.register(db, user_data)
        
        assert "Username già in uso" in str(excinfo.value)
    
    def test_login_success(self, db, test_user):
        """Verifica che un utente possa effettuare il login con successo."""
        # Arrange
        form_data = OAuth2PasswordRequestForm(
            username="test@example.com",
            password="password123",
            scope=""
        )
        
        # Act
        result = AuthController.login(db, form_data)
        
        # Assert
        assert result is not None
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        
        # Verifica che il token contenga l'ID utente
        token_data = decode_token(result["access_token"])
        assert token_data["sub"] == test_user.id
    
    def test_login_invalid_credentials(self, db, test_user):
        """Verifica che il login fallisca con credenziali non valide."""
        # Arrange
        form_data = OAuth2PasswordRequestForm(
            username="test@example.com",
            password="wrongpassword",
            scope=""
        )
        
        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            AuthController.login(db, form_data)
        
        assert "Email o password non corrette" in str(excinfo.value)
    
    def test_authenticate_user(self, db, test_user):
        """Verifica la funzione di autenticazione utente."""
        # Act
        result = AuthController.authenticate_user(db, "test@example.com", "password123")
        
        # Assert
        assert result is not None
        assert result.id == test_user.id
        
        # Verifica con password errata
        result = AuthController.authenticate_user(db, "test@example.com", "wrongpassword")
        assert result is None
        
        # Verifica con email errata
        result = AuthController.authenticate_user(db, "wrong@example.com", "password123")
        assert result is None
    
    def test_change_password(self, db, test_user):
        """Verifica che un utente possa cambiare la propria password."""
        # Act
        result = AuthController.change_password(
            db,
            user=test_user,
            current_password="password123",
            new_password="newpassword123"
        )
        
        # Assert
        assert result is True
        
        # Verifica che la nuova password funzioni
        auth_result = AuthController.authenticate_user(db, "test@example.com", "newpassword123")
        assert auth_result is not None
        assert auth_result.id == test_user.id
    
    def test_change_password_invalid_current(self, db, test_user):
        """Verifica che il cambio password fallisca se la password attuale è errata."""
        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            AuthController.change_password(
                db,
                user=test_user,
                current_password="wrongpassword",
                new_password="newpassword123"
            )
        
        assert "Password attuale non corretta" in str(excinfo.value)